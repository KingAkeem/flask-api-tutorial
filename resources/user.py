from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import (
    get_jwt,
    create_access_token,
    jwt_required,
    create_refresh_token,
    get_jwt_identity,
)
from http import HTTPStatus
from sqlalchemy import or_

from models import UserModel
from schemas import UserSchema, UserRegisterSchema
from blocklist import BLOCKLIST

from db import db
from emails import send_simple_message


blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    def post(self, user_data: dict) -> (dict, HTTPStatus):
        if UserModel.query.filter(
            or_(
                UserModel.username == user_data["username"],
                UserModel.email == user_data["email"],
            )
        ).first():
            msg = "A user with that username already exists."
            abort(HTTPStatus.CONFLICT, message=msg)

        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )
        db.session.add(user)
        db.session.commit()

        send_simple_message(
            to=user.email,
            subject="Successfully signed up",
            body=f"Hi {user.username}! yYou have successfully signed up.",
        )
        return {"message": "User created successfully."}, HTTPStatus.CREATED


@blp.route("/user/<int:user_id>")
class User(MethodView):
    """
    This resource can be useful when testing our Flask app.
    We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful
    when we are manipulating data regarding the users.
    """

    @blp.response(HTTPStatus.OK, UserSchema)
    def get(self, user_id: str) -> UserModel:
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id: str) -> (dict, HTTPStatus):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, HTTPStatus.OK


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data: dict) -> (dict, HTTPStatus):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }, HTTPStatus.OK

        abort(HTTPStatus.UNAUTHORIZED, message="Invalid credentials.")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self) -> (dict, HTTPStatus):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, HTTPStatus.OK


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self) -> (dict, HTTPStatus):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        # Make it clear that when to add the refresh token to the
        # blocklist will depend on the app design
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, HTTPStatus.OK
