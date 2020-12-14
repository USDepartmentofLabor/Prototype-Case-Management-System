from datetime import datetime
from flask import jsonify, request, current_app, session
from flask_jwt_extended import jwt_required, create_access_token, get_raw_jwt
from . import auth
from .. import db, blacklist
from ..models import User
from ..email import send_email
import flask_babel
from ..helpers import is_number


# /auth/login
@auth.route('/login', methods=['POST'])
def login():

    current_app.logger.info("login request")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    login_id = request.json.get('login', None)
    password = request.json.get('password', None)

    if not login_id:
        msg = flask_babel.gettext("Missing login parameter")
        return jsonify({"message": msg}), 400
    if not password:
        msg = flask_babel.gettext("Missing password parameter")
        return jsonify({"message": msg}), 400

    user = User.query.filter_by(username=login_id).first()
    if not user:
        user = User.query.filter_by(email=login_id).first()
        if not user:
            msg = flask_babel.gettext("unknown user")
            return jsonify({'message': msg}), 401
    
    current_app.logger.info("retrieved user %s", user)

    if not user.is_active:
        msg = flask_babel.gettext("User is inactive")
        return jsonify({"message": msg}), 401
    
    if not user.verify_password(password):
        msg = flask_babel.gettext("Bad login or password")
        return jsonify({"message": msg}), 401
    
    current_app.logger.info(f"user {user} successfully logged in")
    session['current_user_id'] = user.id
    user.ping()

    latitude = request.json.get('latitude', None)
    longitude = request.json.get('longitude', None)
    position_accuracy = request.json.get('position_accuracy', None)
    altitude = request.json.get('altitude', None)
    altitude_accuracy = request.json.get('altitude_accuracy', None)
    heading = request.json.get('heading', None)
    speed = request.json.get('speed', None)

    got_location_data = False
    if (latitude is not None and is_number(latitude)) and (longitude is not None and is_number(longitude)):
        user.last_login_location_coordinates = f"POINT({longitude} {latitude})"
        got_location_data = True
    if position_accuracy is not None and is_number(position_accuracy):
        user.last_login_location_position_accuracy = position_accuracy
        got_location_data = True
    if altitude is not None and is_number(altitude):
        user.last_login_location_altitude = altitude
        got_location_data = True
    if altitude_accuracy is not None and is_number(altitude_accuracy):
        user.last_login_location_altitude_accuracy = altitude_accuracy
        got_location_data = True
    if heading is not None and is_number(heading):
        user.last_login_location_heading = heading
        got_location_data = True
    if speed is not None and is_number(speed):
        user.last_login_location_speed = speed
        got_location_data = True

    if got_location_data:
        user.last_login_location_dt = datetime.utcnow()

    db.session.commit()

    access_token = create_access_token(identity=user.id)
    return jsonify({
        "profile": user.__getstate__(),
        "access_token": access_token
    }), 200


@auth.route('/logout', methods=['POST'])
@jwt_required
def logout():
    
    current_app.logger.info("logout")

    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    msg = flask_babel.gettext("Successfully logged out")
    return jsonify({"message": msg}), 200


# /auth/request-password-reset
@auth.route('/request-password-reset', methods=['POST'])
def request_reset_password():
    current_app.logger.info("password reset request")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    email = request.json.get('email', None)

    if email is None:
        current_app.logger.info("password reset request sent without email address")
        msg = flask_babel.gettext("User's email addresses cannot be null or empty.")
        return jsonify({"message": msg}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        session['current_user_id'] = user.id
        current_app.logger.info(f"password reset request sent for user {user.username}")
        token = user.generate_reset_token()
        web_app_url = f"{current_app.config['WEB_APP_URL']}/reset-password/{token}"
        send_email(user.email, 'Reset Your Password', 'auth/email/reset_password', user=user, web_app_url=web_app_url)
    else:
        current_app.logger.info("password reset request send for unknown user")

    msg = flask_babel.gettext("An email with instructions to reset your password has been sent to you.")
    return jsonify({"message": msg}), 200


# /auth/reset-password
@auth.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    current_app.logger.info("password reset submission")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    new_password = request.json.get('new_password', None)
    confirm_password = request.json.get('confirm_password', None)

    if not new_password:
        msg = flask_babel.gettext("New password is missing.")
        return jsonify({"message": msg}), 400
    if not confirm_password:
        msg = flask_babel.gettext("Confirmation password is missing.")
        return jsonify({"message": msg}), 400
    if not new_password == confirm_password:
        msg = flask_babel.gettext("Passwords must match.")
        return jsonify({"message": msg}), 400
    if len(new_password) < 10:
        msg = flask_babel.gettext("Password must be at least 10 characters long.")
        return jsonify({"message": msg}), 400
    if len(new_password) > 64:
        msg = flask_babel.gettext("Password must be less than 64 characters long.")
        return jsonify({"message": msg}), 400

    if User.reset_password(token, new_password):
        db.session.commit()
        msg = flask_babel.gettext("Your password was successfully reset.")
        return jsonify({"message": msg}), 200
    else:
        msg = flask_babel.gettext("Your password was not successfully reset.")
        return jsonify({"message": msg}), 400
