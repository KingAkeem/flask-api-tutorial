from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from http import HTTPStatus

from models import TagModel, StoreModel, ItemModel
from schemas import TagSchema, TagAndItemSchema
from resources.db import db

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

    @blp.response(
        HTTPStatus.ACCEPTED,
        description="Deletes a tag if no item is tagged with it.",
        example={"message": "Tag deleted."},
    )
    @blp.alt_response(HTTPStatus.NOT_FOUND, description="Tag not found.")
    @blp.alt_response(
        HTTPStatus.BAD_REQUEST,
        description=" ".join(
            "Returned if the tag is assigned to one or more items.",
            "In this case, the tag is not deleted.",
        ),
    )
    def delete(self, tag_id: str) -> dict:
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}
        abort(
            HTTPStatus.BAD_REQUEST,
            message=" ".join(
                "Could not delete tag. Make sure tag is not",
                "associated with any items, then try again.",
            ),
        )


@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(HTTPStatus.CREATED, TagSchema)
    def post(self, item_id: str, tag_id: str) -> TagModel:
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                message="An error occurred while inserting the tag.",
            )

        return tag

    @blp.response(HTTPStatus.OK, TagAndItemSchema)
    def delete(self, item_id: str, tag_id: str) -> dict:
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                message="An error occurred while inserting the tag.",
            )

        return {"message": "Item removed from tag", "item": item, "tag": tag}
