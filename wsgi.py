"""Production WSGI entrypoint for hosted deployments."""

import os

from app import app, db, User


application = app


with app.app_context():
    db.create_all()
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if admin_username and admin_password and not User.query.filter_by(username=admin_username).first():
        admin = User(username=admin_username, display_name='系统管理员', role='admin')
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
