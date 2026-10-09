from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.decorators import admin_required
from app.extensions import db
from app.knowledge import knowledge_bp
from app.models.knowledge_article import KnowledgeArticle, article_slug


ARTICLE_CATEGORIES = ("Account", "Payment", "Delivery", "Product", "Security", "General")


def article_form_values():
    return {
        "title": request.form.get("title", "").strip(),
        "category": request.form.get("category", "").strip(),
        "summary": request.form.get("summary", "").strip(),
        "body": request.form.get("body", "").strip(),
    }


def validate_article(values):
    if not all(values.values()):
        return "All article fields are required."
    if values["category"] not in ARTICLE_CATEGORIES:
        return "Choose a valid article category."
    if len(values["title"]) > 200 or len(values["summary"]) > 400:
        return "Title or summary is too long."
    if len(values["body"]) > 20000:
        return "Article body must be 20,000 characters or fewer."
    return None


@knowledge_bp.route("/")
@login_required
def index():
    search = request.args.get("q", "").strip()[:120]
    category = request.args.get("category", "").strip()
    query = KnowledgeArticle.query
    if current_user.role != "admin":
        query = query.filter_by(is_published=True)
    if search:
        needle = f"%{search}%"
        query = query.filter(or_(
            KnowledgeArticle.title.ilike(needle),
            KnowledgeArticle.summary.ilike(needle),
            KnowledgeArticle.body.ilike(needle),
        ))
    if category in ARTICLE_CATEGORIES:
        query = query.filter_by(category=category)
    articles = query.order_by(KnowledgeArticle.updated_at.desc()).all()
    return render_template(
        "knowledge/index.html", articles=articles, search=search,
        selected_category=category, categories=ARTICLE_CATEGORIES,
    )


@knowledge_bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_article():
    if request.method == "POST":
        values = article_form_values()
        error = validate_article(values)
        if error:
            flash(error, "error")
        else:
            article = KnowledgeArticle(
                **values,
                slug=article_slug(values["title"]),
                is_published=request.form.get("is_published") == "on",
                created_by_id=current_user.id,
            )
            db.session.add(article)
            db.session.commit()
            flash("Knowledge Base article created.", "success")
            return redirect(url_for("knowledge.article_detail", slug=article.slug))
    return render_template("knowledge/form.html", article=None, categories=ARTICLE_CATEGORIES)


@knowledge_bp.route("/<slug>")
@login_required
def article_detail(slug):
    article = KnowledgeArticle.query.filter_by(slug=slug).first_or_404()
    if not article.is_published and current_user.role != "admin":
        abort(404)
    return render_template("knowledge/detail.html", article=article)


@knowledge_bp.route("/<int:article_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_article(article_id):
    article = db.get_or_404(KnowledgeArticle, article_id)
    if request.method == "POST":
        values = article_form_values()
        error = validate_article(values)
        if error:
            flash(error, "error")
        else:
            article.title = values["title"]
            article.category = values["category"]
            article.summary = values["summary"]
            article.body = values["body"]
            article.is_published = request.form.get("is_published") == "on"
            db.session.commit()
            flash("Article updated.", "success")
            return redirect(url_for("knowledge.article_detail", slug=article.slug))
    return render_template("knowledge/form.html", article=article, categories=ARTICLE_CATEGORIES)


@knowledge_bp.route("/<int:article_id>/publish", methods=["POST"])
@login_required
@admin_required
def toggle_publish(article_id):
    article = db.get_or_404(KnowledgeArticle, article_id)
    article.is_published = not article.is_published
    db.session.commit()
    flash("Article published." if article.is_published else "Article moved to drafts.", "success")
    return redirect(url_for("knowledge.index"))
