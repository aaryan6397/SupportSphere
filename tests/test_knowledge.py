from app.extensions import db
from app.models.knowledge_article import KnowledgeArticle
from app.models.user import User


def test_admin_can_publish_knowledge_article_and_customer_can_read_it(client, app):
    with app.app_context():
        admin = User(name="Admin", email="admin@example.com", role="admin")
        admin.set_password("Password123")
        customer = User(name="Customer", email="customer@example.com", role="customer")
        customer.set_password("Password123")
        db.session.add_all([admin, customer])
        db.session.commit()

    client.post("/auth/login", data={"email": "admin@example.com", "password": "Password123"})
    response = client.post("/knowledge/new", data={
        "title": "Reset your password",
        "category": "Account",
        "summary": "Steps to regain account access.",
        "body": "Use the password reset link from the login page.",
        "is_published": "on",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Reset your password" in response.data

    with app.app_context():
        article = KnowledgeArticle.query.first()
        assert article is not None
        assert article.is_published is True

    client.post("/auth/logout")
    client.post("/auth/login", data={"email": "customer@example.com", "password": "Password123"})
    response = client.get("/knowledge/?q=password")
    assert response.status_code == 200
    assert b"Reset your password" in response.data
