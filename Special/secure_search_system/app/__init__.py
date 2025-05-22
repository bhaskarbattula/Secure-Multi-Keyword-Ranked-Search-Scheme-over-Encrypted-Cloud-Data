from flask import Flask
from .routes.admin_routes import admin_bp
from .routes.auth_routes import auth_bp
from .routes.user_routes import user_bp
from .routes.main_routes import main_bp
from .routes.signup_routes import signup_bp
from .routes.login_routes import login_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "super-secret-key"

    from .routes.admin_routes import admin_bp
    from .routes.user_routes import user_bp
    from .routes.auth_routes import auth_bp
    from .routes.main_routes import main_bp
    from .routes.signup_routes import signup_bp
    from .routes.login_routes import login_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(login_bp)
    app.secret_key= 'your_secret_key'

    return app
