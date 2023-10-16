import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from http import HTTPStatus

from resources.validation.items import valid_update_item, valid_new_item
from resources.db import items

blp = Blueprint("Items", "items", description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
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

    def put(self, item_id: str) -> dict:
        item_data = request.get_json()

        try:
            if not valid_update_item(item_data):
                abort(HTTPStatus.BAD_REQUEST, message="Invalid item found")
        except Exception as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

        try:
            item = items[item_id]

            # https://blog.teclado.com/python-dictionary-merge-update-operators/
            item |= item_data

            return item
        except KeyError:
            abort(HTTPStatus.NOT_FOUND, message="Item not found.")


@blp.route("/item")
class ItemList(MethodView):
    def get(self) -> dict:
        return {"items": list(items.values())}

    def post(self) -> dict:
        item_data = request.get_json()

        try:
            if not valid_new_item(item_data):
                abort(HTTPStatus.BAD_REQUEST, message="Invalid item found.")

        except Exception as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

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
