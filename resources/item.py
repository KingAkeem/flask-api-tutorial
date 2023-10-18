from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from http import HTTPStatus

from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema
from db import db

blp = Blueprint("Items", "items", description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(HTTPStatus.OK, ItemSchema)
    def get(self, item_id: str) -> ItemModel:
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self, item_id: str) -> (dict, HTTPStatus):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(HTTPStatus.UNAUTHORIZED, message="Admin privilege required.")

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
    @jwt_required()
    @blp.response(HTTPStatus.OK, ItemSchema(many=True))
    def get(self) -> list[ItemModel]:
        return ItemModel.query.all()

    @jwt_required(fresh=True)
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
