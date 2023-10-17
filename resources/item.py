from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from http import HTTPStatus

from schemas import ItemSchema, ItemUpdateSchema
from resources.db import db
from resources.models import ItemModel

blp = Blueprint("Items", "items", description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(HTTPStatus.OK, ItemSchema)
    def get(self, item_id: str) -> ItemModel:
        item = ItemModel.query.get_or_404(item_id)
        return item

    def delete(self, item_id: str) -> (dict, HTTPStatus):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}, HTTPStatus.OK

    @blp.arguments(ItemUpdateSchema)
    @blp.response(HTTPStatus.OK, ItemSchema)
    def put(self, item_data: dict, item_id: str) -> ItemModel:
        item = ItemModel.query.get_or_404(item_id)
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(HTTPStatus.OK, ItemSchema(many=True))
    def get(self) -> list[ItemModel]:
        return ItemModel.query.all()

    @blp.arguments(ItemSchema)
    @blp.response(HTTPStatus.CREATED, ItemSchema)
    def post(self, item_data: dict) -> ItemModel:
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            msg = "Unable to insert item."
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=msg)

        return item
