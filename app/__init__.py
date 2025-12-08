from flask import Flask


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Register blueprints
    from app.routes.analyzer import analyzer_bp
    from app.routes.news import news_bp
    from app.routes.webhook import webhook_bp

    app.register_blueprint(analyzer_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(webhook_bp)

    return app
