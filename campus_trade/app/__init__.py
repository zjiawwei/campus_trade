from flask import Flask, render_template
from app.config import config_map
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_name=None):
    if config_name is None:
        # Default to FLASK_CONFIG env var, fallback to development
        import os
        config_name = os.environ.get("FLASK_CONFIG", "development")

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Flask-Login user loader
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Register context processors
    @app.context_processor
    def inject_globals():
        return {"app_name": "校园二手交易平台"}

    # CLI commands
    import click

    @app.cli.command("create-admin")
    @click.argument("username")
    @click.argument("student_id")
    @click.argument("password")
    @click.argument("campus")
    def create_admin(username, student_id, password, campus):
        """Create an admin user: flask create-admin <username> <student_id> <password> <campus>"""
        from app.models.user import User
        user = User(
            username=username,
            student_id=student_id,
            campus=campus,
            role="admin",
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Admin user '{username}' created successfully.")

    @app.cli.command("seed-categories")
    def seed_categories():
        """Seed the database with default product categories."""
        from app.models.category import Category

        categories = [
            {"name": "图书教材", "description": "课程教材、参考书、考研资料", "icon": "bi-book", "sort_order": 1},
            {"name": "电子产品", "description": "手机、电脑、平板、耳机等", "icon": "bi-laptop", "sort_order": 2},
            {"name": "生活用品", "description": "宿舍收纳、日用品等", "icon": "bi-basket", "sort_order": 3},
            {"name": "运动器材", "description": "球类、健身器材等", "icon": "bi-bicycle", "sort_order": 4},
            {"name": "衣物鞋帽", "description": "服装、鞋子、配饰等", "icon": "bi-handbag", "sort_order": 5},
            {"name": "学习用品", "description": "文具、笔记本等", "icon": "bi-pencil", "sort_order": 6},
            {"name": "其他", "description": "其他未分类物品", "icon": "bi-grid", "sort_order": 7},
        ]
        for cat_data in categories:
            existing = Category.query.filter_by(name=cat_data["name"]).first()
            if existing:
                # Update existing
                for k, v in cat_data.items():
                    setattr(existing, k, v)
            else:
                db.session.add(Category(**cat_data))
        db.session.commit()
        print(f"Seeded {len(categories)} categories.")

    return app


def register_blueprints(app):
    from app.blueprints.main import bp as main_bp
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.user import bp as user_bp
    from app.blueprints.admin import bp as admin_bp
    from app.blueprints.product import bp as product_bp
    from app.blueprints.order import bp as order_bp
    from app.blueprints.message import bp as message_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(message_bp)


def register_error_handlers(app):

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500
