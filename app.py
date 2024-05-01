# app.py
from flask import Flask , render_template_string
from auth import auth , login_manager , avatars , mail
from onboarding import onboarding
from profile_management import profile
from appointments import appointments
from search_engine import search
from views import views
from models import db
from classes import classes
from videocall import video
from chat import chat
import config


def create_app():
    app = Flask(__name__)

   
    app.config.from_object(config.Config())
    db.init_app(app)
    login_manager.init_app(app)
    avatars.init_app(app)
    mail.init_app(app)

    # Register the blueprint with the Flask app
    app.register_blueprint(auth)
    app.register_blueprint(onboarding)
    app.register_blueprint(views)
    app.register_blueprint(appointments)
    app.register_blueprint(search)
    app.register_blueprint(profile)
    app.register_blueprint(classes)
    app.register_blueprint(video)
    app.register_blueprint(chat)

    
    @app.before_first_request
    def create_tables():
        db.create_all()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template_string('404 error'), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return render_template_string('500 error'), 500

    return app
    
app = create_app()
"""
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
"""