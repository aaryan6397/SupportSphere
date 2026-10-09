from flask import Blueprint


knowledge_bp = Blueprint("knowledge", __name__, url_prefix="/knowledge")

from app.knowledge import routes
