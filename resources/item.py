import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from http import HTTPStatus

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
        # There's  more validation to do here!
        # Like making sure price is a number, and also both items are optional
        # Difficult to do with an if statement...
        if "price" not in item_data or "name" not in item_data:
            abort(
                HTTPStatus.BAD_REQUEST,
                message="Ensure 'price', and 'name' are included in the JSON.",
            )
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
        # Here not only we need to validate data exists,
        # But also what type of data. Price should be a float,
        # for example.
        if (
            "price" not in item_data
            or "store_id" not in item_data
            or "name" not in item_data
        ):
            abort(
                HTTPStatus.BAD_REQUEST,
                message=" ".join(
                    "Ensure 'price', 'store_id', and 'name' are included",
                    "in the JSON payload.",
                ),
            )
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
