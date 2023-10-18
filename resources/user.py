from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import get_jwt, create_access_token, jwt_required
from http import HTTPStatus

from models import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST

from db import db


blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data: dict) -> (dict, HTTPStatus):
        filter_cond = UserModel.username == user_data["username"]
        if UserModel.query.filter(filter_cond).first():
            msg = "A user with that username already exists."
            abort(HTTPStatus.CONFLICT, message=msg)

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )
        db.session.add(user)
        db.session.commit()

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
        return {"message": "User deleted."}, 200


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data: dict) -> (dict, HTTPStatus):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}, HTTPStatus.OK

        abort(HTTPStatus.UNAUTHORIZED, message="Invalid credentials.")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self) -> (dict, HTTPStatus):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, HTTPStatus.OK
