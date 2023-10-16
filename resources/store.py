import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from resources.db import stores
from http import HTTPStatus


blp = Blueprint("stores", __name__, description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    def get(self, store_id):
        try:
            return stores[store_id]
        except KeyError:
            abort(HTTPStatus.NOT_FOUND, message="Store not found.")

    def delete(self, store_id):
        try:
            del stores[store_id]
            return {"message": "Store deleted."}
        except KeyError:
            abort(HTTPStatus.NOT_FOUND, message="Store not found.")


@blp.route("/store")
class StoreList(MethodView):
    def get(self):
        return {"stores": list(stores.values())}

    def post(self):
        store_data = request.get_json()
        if "name" not in store_data:
            abort(
                HTTPStatus.BAD_REQUEST,
                message="Ensure 'name' is included in the JSON.",
            )
        for store in stores.values():
            if store_data["name"] == store["name"]:
                abort(HTTPStatus.BAD_REQUEST, message="Store already exists.")

        store_id = uuid.uuid4().hex
        store = {**store_data, "id": store_id}
        stores[store_id] = store

        return store