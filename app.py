import os

from http import HTTPStatus
from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from blocklist import BLOCKLIST
from resources.user import blp as UserBlueprint
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from db import db

import models  # noqa: F401


def create_app(db_url: str = None) -> Flask:
    app = Flask(__name__)
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    swagger_ui_url = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["OPENAPI_SWAGGER_UI_URL"] = swagger_ui_url

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "akeem"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        desc = "The token has been revoked."
        return (
            jsonify({"description": desc, "error": "token_revoked"}),
            HTTPStatus.UNAUTHORIZED,
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        err_msg = "The token has expired."
        err_resp = {"message": err_msg, "error": "token_expired"}
        return (
            jsonify(err_resp),
            HTTPStatus.UNAUTHORIZED,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        err_msg = "Signature verification failed."
        return (
            jsonify({"message": err_msg, "error": "invalid_token"}),
            HTTPStatus.UNAUTHORIZED,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        desc = "Request does not contain an access token."
        return (
            jsonify(
                {
                    "description": desc,
                    "error": "authorization_required",
                }
            ),
            HTTPStatus.UNAUTHORIZED,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            HTTPStatus.UNAUTHORIZED,
        )

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)

    return app
