from pathlib import Path
from uuid import uuid4

from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.attachment import TicketAttachment
from app.models.comment import TicketComment
from app.models.feedback import TicketFeedback
from app.models.ticket import Ticket, calculate_sla_due_at
from app.models.user import User
from app.services.notification_service import create_notification
from app.services.ticket_service import transition_ticket
from app.services.file_service import safe_upload_path, validate_upload
from app.services.audit_service import log_event
from app.tickets import tickets_bp


def can_access_ticket(ticket):
    if current_user.role == "admin":
        return True

    if current_user.role == "customer":
        return ticket.customer_id == current_user.id

    if current_user.role == "agent":
        return ticket.assigned_agent_id == current_user.id

    return False


@tickets_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_ticket():
    if current_user.role != "customer":
        flash("Only customers can create support tickets.", "error")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        category = request.form.get("category", "").strip()
        priority = request.form.get("priority", "medium").strip()
        description = request.form.get("description", "").strip()

        uploaded_file = request.files.get("attachment")

        allowed_categories = [
            "Payment",
            "Delivery",
            "Account",
            "Refund",
            "Product",
            "Other"
        ]

        allowed_priorities = ["low", "medium", "high", "critical"]

        if not subject or not category or not description:
            flash("Please complete all required fields.", "error")
            return render_template("tickets/create.html")

        if len(subject) > 200 or len(description) > 5000:
            flash("Subject must be under 200 characters and description under 5,000 characters.", "error")
            return render_template("tickets/create.html")

        if category not in allowed_categories:
            flash("Please select a valid category.", "error")
            return render_template("tickets/create.html")

        if priority not in allowed_priorities:
            flash("Please select a valid priority.", "error")
            return render_template("tickets/create.html")

        if uploaded_file and uploaded_file.filename:
            file_is_valid, file_error = validate_upload(
                uploaded_file, current_app.config["ALLOWED_FILE_EXTENSIONS"]
            )
            if not file_is_valid:
                flash(file_error, "error")
                return render_template("tickets/create.html")

        ticket = Ticket(
            subject=subject,
            category=category,
            priority=priority,
            description=description,
            customer_id=current_user.id,
            sla_due_at=calculate_sla_due_at(priority)
        )

        db.session.add(ticket)
        db.session.flush()
        log_event("ticket_created", f"Created ticket {ticket.ticket_code}.", current_user.id, "ticket", ticket.id)

        ticket_link = url_for("tickets.ticket_detail", ticket_id=ticket.id)
        for admin in User.query.filter_by(role="admin", is_active_account=True).all():
            create_notification(
                admin.id,
                "New ticket created",
                f"{ticket.ticket_code}: {ticket.subject}",
                ticket_link,
            )

        if uploaded_file and uploaded_file.filename:
            original_filename = secure_filename(uploaded_file.filename)

            extension = original_filename.rsplit(".", 1)[1].lower()

            stored_filename = f"{uuid4().hex}.{extension}"

            upload_folder = Path(
                current_app.config["UPLOAD_FOLDER"]
            )

            upload_folder.mkdir(
                parents=True,
                exist_ok=True
            )

            storage_path = safe_upload_path(upload_folder, stored_filename)
            uploaded_file.save(storage_path)

            attachment = TicketAttachment(
                original_filename=original_filename,
                stored_filename=stored_filename,
                content_type=uploaded_file.content_type,
                file_size=storage_path.stat().st_size,
                ticket_id=ticket.id,
                uploaded_by_id=current_user.id
            )

            db.session.add(attachment)

        db.session.commit()

        flash(
            f"Ticket {ticket.ticket_code} was created successfully.",
            "success"
        )

        return redirect(url_for("main.dashboard"))

    return render_template("tickets/create.html")


@tickets_bp.route("/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)

    if not can_access_ticket(ticket):
        abort(403)

    comments = ticket.comments
    if current_user.role == "customer":
        comments = [comment for comment in comments if not comment.is_internal]

    return render_template(
        "tickets/detail.html",
        ticket=ticket,
        comments=comments
    )


@tickets_bp.route("/<int:ticket_id>/comments", methods=["POST"])
@login_required
def add_comment(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)

    if not can_access_ticket(ticket):
        abort(403)

    message = request.form.get("message", "").strip()
    is_internal = request.form.get("is_internal") == "on"

    if is_internal and current_user.role not in {"agent", "admin"}:
        abort(403)

    if not message:
        flash("Reply message cannot be empty.", "error")

        return redirect(
            url_for("tickets.ticket_detail", ticket_id=ticket.id)
        )

    if len(message) > 5000:
        flash("Reply must be 5,000 characters or fewer.", "error")
        return redirect(
            url_for("tickets.ticket_detail", ticket_id=ticket.id)
        )

    comment = TicketComment(
        message=message,
        ticket_id=ticket.id,
        author_id=current_user.id,
        is_internal=is_internal
    )

    if current_user.role in {"agent", "admin"} and not ticket.first_responded_at:
        from datetime import datetime
        ticket.first_responded_at = datetime.utcnow()

    if not is_internal:
        ticket_link = url_for("tickets.ticket_detail", ticket_id=ticket.id)
        if current_user.role in {"agent", "admin"}:
            create_notification(
                ticket.customer_id,
                "New reply on your ticket",
                f"{ticket.ticket_code} has a new support response.",
                ticket_link,
            )
        elif ticket.assigned_agent_id:
            create_notification(
                ticket.assigned_agent_id,
                "Customer replied",
                f"{ticket.ticket_code} has a new customer reply.",
                ticket_link,
            )

    db.session.add(comment)
    log_event(
        "internal_note_added" if is_internal else "ticket_reply_added",
        f"Added {'an internal note' if is_internal else 'a public reply'} to {ticket.ticket_code}.",
        current_user.id, "ticket", ticket.id,
    )
    db.session.commit()

    flash("Internal note added successfully." if is_internal else "Your reply was added successfully.", "success")

    return redirect(
        url_for("tickets.ticket_detail", ticket_id=ticket.id)
    )


@tickets_bp.route("/<int:ticket_id>/reopen", methods=["POST"])
@login_required
def reopen_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)

    if current_user.role != "customer" or ticket.customer_id != current_user.id:
        abort(403)

    success, message = transition_ticket(ticket, "reopened")
    if success:
        if ticket.assigned_agent_id:
            create_notification(
                ticket.assigned_agent_id,
                "Ticket reopened",
                f"{ticket.ticket_code} was reopened by the customer.",
                url_for("tickets.ticket_detail", ticket_id=ticket.id),
            )
        log_event("ticket_reopened", f"Reopened ticket {ticket.ticket_code}.", current_user.id, "ticket", ticket.id)
        db.session.commit()
        flash("Ticket reopened. Our team will review it shortly.", "success")
    else:
        flash(message, "error")

    return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))


@tickets_bp.route("/attachments/<int:attachment_id>/download")
@login_required
def download_attachment(attachment_id):
    attachment = db.get_or_404(
        TicketAttachment,
        attachment_id
    )

    if not can_access_ticket(attachment.ticket):
        abort(403)

    upload_folder = Path(
        current_app.config["UPLOAD_FOLDER"]
    )

    return send_from_directory(
        upload_folder,
        attachment.stored_filename,
        as_attachment=True,
        download_name=attachment.original_filename
    )


@tickets_bp.route("/<int:ticket_id>/feedback", methods=["POST"])
@login_required
def submit_feedback(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)

    if current_user.role != "customer":
        abort(403)

    if ticket.customer_id != current_user.id:
        abort(403)

    if ticket.status != "resolved":
        flash(
            "Feedback can only be submitted after ticket resolution.",
            "error"
        )

        return redirect(
            url_for("tickets.ticket_detail", ticket_id=ticket.id)
        )

    if ticket.feedback:
        flash("Feedback has already been submitted.", "error")

        return redirect(
            url_for("tickets.ticket_detail", ticket_id=ticket.id)
        )

    rating = request.form.get("rating", type=int)
    comment = request.form.get("feedback_comment", "").strip()

    if len(comment) > 2000:
        flash("Feedback comment must be 2,000 characters or fewer.", "error")
        return redirect(
            url_for("tickets.ticket_detail", ticket_id=ticket.id)
        )

    if not rating or rating not in [1, 2, 3, 4, 5]:
        flash("Please choose a rating from 1 to 5.", "error")

        return redirect(
            url_for("tickets.ticket_detail", ticket_id=ticket.id)
        )

    feedback = TicketFeedback(
        rating=rating,
        comment=comment,
        ticket_id=ticket.id,
        customer_id=current_user.id
    )

    db.session.add(feedback)
    log_event("feedback_submitted", f"Submitted feedback for {ticket.ticket_code}.", current_user.id, "ticket", ticket.id)
    db.session.commit()

    flash("Thank you for your feedback!", "success")

    return redirect(
        url_for("tickets.ticket_detail", ticket_id=ticket.id)
    )
