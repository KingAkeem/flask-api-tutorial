import uuid
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from http import HTTPStatus

from schemas import ItemSchema, ItemUpdateSchema
from resources.db import items

blp = Blueprint("Items", "items", description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(HTTPStatus.OK, ItemSchema)
    def get(self, item_id: str) -> dict:
        try:
            return items[item_id]
        except KeyError:
            abort(HTTPStatus.NOT_FOUND, message="Item not found.")

    def delete(self, item_id: str) -> dict:
        try:
            del items[item_id]
            return {"message": "Item deleted."}
        except KeyError:
            abort(HTTPStatus.NOT_FOUND, message="Item not found.")

    @blp.arguments(ItemUpdateSchema)
    @blp.response(HTTPStatus.OK, ItemSchema)
    def put(self, item_data: dict, item_id: str) -> dict:
        try:
            item = items[item_id]
            item |= item_data
            return item
        except KeyError:
            abort(HTTPStatus.NOT_FOUND, message="Item not found.")


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(HTTPStatus.OK, ItemSchema(many=True))
    def get(self) -> list[dict]:
        return items.values()

    @blp.arguments(ItemSchema)
    @blp.response(HTTPStatus.CREATED, ItemSchema)
    def post(self, item_data: dict) -> dict:
        for item in items.values():
            if (
                item_data["name"] == item["name"]
                and item_data["store_id"] == item["store_id"]
            ):
                abort(HTTPStatus.BAD_REQUEST, message="Item already exists.")

        item_id = uuid.uuid4().hex
        item = {**item_data, "id": item_id}
        items[item_id] = item
        return item
