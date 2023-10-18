from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from http import HTTPStatus

from resources.db import db
from resources.models import TagModel, StoreModel
from schemas import TagSchema

blp = Blueprint("Tags", "tags", description="Operations on tags")


@blp.route("/store/<string:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(HTTPStatus.OK, TagSchema(many=True))
    def get(self, store_id: str) -> list[TagModel]:
        store = StoreModel.query.get_or_404(store_id)

        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(HTTPStatus.CREATED, TagSchema)
    def post(self, tag_data: dict, store_id: str) -> TagModel:
        if TagModel.query.filter(
            TagModel.store_id == store_id, TagModel.name == tag_data["name"]
        ).first():
            abort(
                HTTPStatus.BAD_REQUEST,
                message="A tag with that name already exists in that store.",
            )

        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                message=str(e),
            )

        return tag


@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(HTTPStatus.OK, TagSchema)
    def get(self, tag_id: str) -> TagModel:
        tag = TagModel.query.get_or_404(tag_id)
        return tag
