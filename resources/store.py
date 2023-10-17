import uuid
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from http import HTTPStatus

from resources.db import stores
from schemas import StoreSchema

blp = Blueprint("stores", __name__, description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(HTTPStatus.OK, StoreSchema)
    def get(self, store_id: str) -> dict:
        try:
            return stores[store_id]
        except KeyError:
            abort(HTTPStatus.NOT_FOUND, message="Store not found.")

    def delete(self, store_id: str) -> dict:
        try:
            del stores[store_id]
            return {"message": "Store deleted."}
        except KeyError:
            abort(HTTPStatus.NOT_FOUND, message="Store not found.")


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(HTTPStatus.OK, StoreSchema(many=True))
    def get(self):
        return {"stores": list(stores.values())}

    @blp.arguments(StoreSchema)
    @blp.response(HTTPStatus.CREATED, StoreSchema)
    def post(self, store_data: dict) -> dict:
        for store in stores.values():
            if store_data["name"] == store["name"]:
                abort(HTTPStatus.BAD_REQUEST, message="Store already exists.")

        store_id = uuid.uuid4().hex
        store = {**store_data, "id": store_id}
        stores[store_id] = store
        return store
