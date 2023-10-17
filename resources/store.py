from flask.views import MethodView
from flask_smorest import Blueprint, abort
from http import HTTPStatus
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from resources.db import db
from resources.models import StoreModel
from schemas import StoreSchema

blp = Blueprint("stores", __name__, description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(HTTPStatus.OK, StoreSchema)
    def get(self, store_id: str) -> StoreModel:
        store = StoreModel.query.get_or_404(store_id)
        return store

    def delete(self, store_id: str) -> (dict, HTTPStatus):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "store deleted"}, HTTPStatus.OK


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(HTTPStatus.OK, StoreSchema(many=True))
    def get(self) -> list[StoreModel]:
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(HTTPStatus.CREATED, StoreSchema)
    def post(self, store_data: dict) -> StoreModel:
        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(HTTPStatus.BAD_REQUEST, message="Store already exists.")
        except SQLAlchemyError:
            msg = "Unable to insert store."
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=msg)

        return store
