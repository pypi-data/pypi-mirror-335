import json
import logging
import time
import typing

import fastapi
import pymongo
import pymongo.collection
import pymongo.database
import pymongo.errors

from any_auth.backend._base import BaseCollection
from any_auth.types.organization import (
    Organization,
    OrganizationCreate,
    OrganizationUpdate,
)
from any_auth.types.pagination import Page

if typing.TYPE_CHECKING:
    from any_auth.backend._client import BackendClient

logger = logging.getLogger(__name__)


class Organizations(BaseCollection):
    def __init__(self, client: "BackendClient"):
        super().__init__(client)

    @property
    def collection_name(self):
        return "organizations"

    def create_indexes(
        self,
        *args,
        **kwargs,
    ):
        super().create_indexes(self.settings.indexes_organizations)

    def create(self, org: OrganizationCreate) -> Organization:
        org_in_db = org.to_org()
        doc = org_in_db.to_doc()

        try:
            result = self.collection.insert_one(doc)
            org_in_db._id = str(result.inserted_id)

            # Delete cache
            self._client.cache.delete(f"organization:{org_in_db.id}")

            return org_in_db

        except pymongo.errors.DuplicateKeyError as e:
            raise fastapi.HTTPException(
                status_code=409, detail="An organization with this name already exists."
            ) from e

    def retrieve(self, id: typing.Text) -> typing.Optional[Organization]:
        # Get from cache
        cached_org = self._client.cache.get(f"organization:{id}")
        if cached_org:
            return Organization.model_validate_json(cached_org)  # type: ignore

        org_data = self.collection.find_one({"id": id})
        if org_data:
            org = Organization.model_validate(org_data)
            org._id = str(org_data["_id"])

            # Cache
            self._client.cache.set(
                f"organization:{id}",
                org.model_dump_json(),
                self._client.cache_ttl,
            )

            return org
        return None

    def retrieve_by_name(self, name: typing.Text) -> typing.Optional[Organization]:
        # Get from cache
        cached_org = self._client.cache.get(f"organization_by_name:{name}")
        if cached_org:
            return Organization.model_validate_json(cached_org)  # type: ignore

        org_data = self.collection.find_one({"name": name})
        if org_data:
            org = Organization.model_validate(org_data)
            org._id = str(org_data["_id"])

            # Cache
            self._client.cache.set(
                f"organization_by_name:{name}",
                org.model_dump_json(),
                self._client.cache_ttl,
            )

            return org
        return None

    def retrieve_by_ids(self, ids: typing.List[str]) -> typing.List[Organization]:
        cursor = self.collection.find({"id": {"$in": ids}})
        out: typing.List[Organization] = []
        for doc in cursor:
            org = Organization.model_validate(doc)
            org._id = str(doc["_id"])
            out.append(org)
        return out

    def list(
        self,
        *,
        limit: typing.Optional[int] = 20,
        order: typing.Literal["asc", "desc", 1, -1] = -1,
        after: typing.Optional[typing.Text] = None,
        before: typing.Optional[typing.Text] = None,
    ) -> Page[Organization]:
        limit = limit or 20
        if limit > 100:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail="Limit cannot be greater than 100",
            )

        sort_direction = (
            pymongo.DESCENDING if order in ("desc", -1) else pymongo.ASCENDING
        )

        query = {}
        cursor_id = after if after is not None else before
        cursor_type = "after" if after is not None else "before"

        if cursor_id:
            cursor_doc = self.collection.find_one({"id": cursor_id})
            if cursor_doc is None:
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_404_NOT_FOUND,
                    detail=f"Organization with id {cursor_id} not found",
                )
            comparator = (
                "$lt"
                if (
                    (cursor_type == "after" and sort_direction == pymongo.DESCENDING)
                    or (cursor_type == "before" and sort_direction == pymongo.ASCENDING)
                )
                else "$gt"
            )
            query["$or"] = [
                {"created_at": {comparator: cursor_doc["created_at"]}},
                {
                    "created_at": cursor_doc["created_at"],
                    "id": {comparator: cursor_doc["id"]},
                },
            ]

        # Fetch `limit + 1` docs to detect if there's a next/previous page
        logger.debug(
            f"List organizations with query: {query}, "
            + f"sort: {sort_direction}, limit: {limit}"
        )
        cursor = (
            self.collection.find(query)
            .sort([("created_at", sort_direction), ("id", sort_direction)])
            .limit(limit + 1)
        )

        docs = list(cursor)
        has_more = len(docs) > limit

        # If we got an extra doc, remove it so we only return `limit` docs
        if has_more:
            docs = docs[:limit]

        # Convert raw MongoDB docs into Organization models
        organizations: typing.List[Organization] = []
        for doc in docs:
            org = Organization.model_validate(doc)
            org._id = doc["_id"]
            organizations.append(org)

        first_id = organizations[0].id if organizations else None
        last_id = organizations[-1].id if organizations else None

        page = Page[Organization](
            data=organizations,
            first_id=first_id,
            last_id=last_id,
            has_more=has_more,
        )
        return page

    def update(self, id: typing.Text, org_update: OrganizationUpdate) -> Organization:
        update_data = json.loads(org_update.model_dump_json(exclude_none=True))
        update_data["updated_at"] = int(time.time())

        try:
            updated_doc = self.collection.find_one_and_update(
                {"id": id},
                {"$set": update_data},
                return_document=pymongo.ReturnDocument.AFTER,
            )
        except pymongo.errors.DuplicateKeyError as e:
            raise fastapi.HTTPException(
                status_code=409, detail="An organization with this name already exists."
            ) from e

        if updated_doc is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail=f"Organization with id {id} not found",
            )

        updated_org = Organization.model_validate(updated_doc)
        updated_org._id = str(updated_doc["_id"])

        # Delete cache
        self._client.cache.delete(f"organization:{id}")

        return updated_org

    def set_disabled(self, id: typing.Text, disabled: bool) -> Organization:
        updated_doc = self.collection.find_one_and_update(
            {"id": id},
            {"$set": {"disabled": disabled}},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        if updated_doc is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail=f"Organization with id {id} not found",
            )

        updated_org = Organization.model_validate(updated_doc)
        updated_org._id = str(updated_doc["_id"])

        # Delete cache
        self._client.cache.delete(f"organization:{id}")

        return updated_org
