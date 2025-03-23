#  Copyright 2023 Reid Swanson.
#
#  This file is part of scrachy.
#
#  scrachy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  scrachy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with scrachy.  If not, see <https://www.gnu.org/licenses/>.
# Loosely based on: https://hackernoon.com/building-a-to-do-list-app-with-python-data-access-layer-with-sqlalchemy

"""
The Data Access Layer.
"""

# Standard Library
import abc
import datetime
import logging

from typing import Any, Callable, Generic, Iterable, Optional, Sequence, Type, TypeVar

# 3rd Party Library
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.postgresql.dml import Insert as PostgresInsert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.sqlite.dml import Insert as SqliteInsert
from sqlalchemy.orm import Session, load_only, selectinload

# 1st Party Library
from scrachy.db.base import Base
from scrachy.db.models import Response, ScrapeHistory
from scrachy.settings.defaults.storage import RetrievalMethod

BaseT = TypeVar("BaseT", bound=Base)

InsertFunction = Callable[[Any], SqliteInsert | PostgresInsert]


log = logging.getLogger(__name__)


class BaseRepository(abc.ABC, Generic[BaseT]):
    def __init__(self, model: Type[BaseT], session: Session):
        if session.bind is None:
            raise ValueError("A repository requires a bound session.")

        self.model = model
        self.session = session
        self.dialect = session.bind.dialect.name
        self.upsert_fn = self._get_upsert_fn()

    def find_all(self) -> Sequence[BaseT]:
        stmt = select(self.model)

        return self.session.scalars(stmt).all()

    def insert(self, obj: BaseT):
        self.session.add(obj)

    def insert_all(self, objs: Iterable[BaseT]):
        self.session.add_all(objs)

    def _get_upsert_fn(self) -> InsertFunction:
        if self.dialect == "sqlite":
            return sqlite_insert

        if self.dialect == "postgresql":
            return pg_insert

        raise ValueError(
            f"The current dialect '{self.dialect}' does not support upserts."
        )


class ResponseRepository(BaseRepository[Response]):
    def __init__(self, session: Session):
        super().__init__(Response, session=session)

    def find_timestamp_by_fingerprint(
        self, fingerprint: bytes
    ) -> Optional[datetime.datetime]:
        stmt = select(Response.scrape_timestamp).where(
            Response.fingerprint == fingerprint
        )

        return self.session.scalars(stmt).first()

    def find_by_fingerprint(
        self, fingerprint: bytes, retrieval_method: RetrievalMethod = "full"
    ) -> Optional[Response]:
        if retrieval_method == "minimal":
            return self._find_minimal(fingerprint)

        if retrieval_method == "standard":
            return self._find_standard(fingerprint)

        if retrieval_method == "full":
            return self._find_full(fingerprint)

        raise ValueError(f"Unknown retrieval method: {retrieval_method}")

    def upsert(self, response: Response, returning: bool = False) -> Optional[Response]:
        # If the dialect is not postgresql or sqlite, we first need to
        # query for any existing items. If one exists we should perform
        # an update. Otherwise, we can use the upsert capabilities of the
        # specific dialects.
        if self.dialect in ("sqlite", "postgresql"):
            return self._upsert_on_conflict(response, returning)

        return self._multi_query_upsert(response)

    # region Utility Methods
    def _find_minimal(self, fingerprint: bytes) -> Optional[Response]:
        stmt = (
            select(Response)
            .options(load_only(Response.body))
            .where(Response.fingerprint == fingerprint)
        )

        # This should be unique
        return self.session.scalars(stmt).one_or_none()

    def _find_standard(self, fingerprint: bytes) -> Optional[Response]:
        stmt = (
            select(Response)
            .options(
                load_only(
                    Response.body, Response.meta, Response.headers, Response.status
                )
            )
            .where(Response.fingerprint == fingerprint)
        )

        return self.session.scalars(stmt).one_or_none()

    def _find_full(self, fingerprint: bytes) -> Optional[Response]:
        stmt = (
            select(Response)
            .options(selectinload(Response.scrape_history))
            .where(
                Response.fingerprint == fingerprint,
            )
        )

        return self.session.scalars(stmt).one_or_none()

    def _upsert_on_conflict(
        self, response: Response, returning: bool
    ) -> Optional[Response]:
        columns = response.__table__.columns.keys()

        stmt = self.upsert_fn(Response).values(**{
            c: getattr(response, c, None) for c in columns if c != "id"
        })

        update_stmt = stmt.on_conflict_do_update(
            index_elements=[Response.fingerprint],
            set_={
                c: stmt.excluded[c] for c in columns if c not in ("id", "fingerprint")
            },
        )

        if returning:
            update_stmt = update_stmt.returning(Response)
            result = self.session.scalars(
                update_stmt, execution_options={"populate_existing": True}
            )
            return result.one_or_none()

        self.session.execute(update_stmt, execution_options={"populate_existing": True})

        return response

    def _multi_query_upsert(self, response: Response) -> Response:
        # TODO I'm not sure what to do about these kinds of errors.
        #      SqlAlchemy allows for type mapping, which seems very helpful,
        #      but it looks like it also causes a lot of problems for the type
        #      checker.
        existing_response = self.find_by_fingerprint(response.fingerprint)  # type: ignore
        update_columns = [
            c
            for c in response.__table__.columns.keys()
            if c not in ("id", "fingerprint")
        ]

        if existing_response is None:
            self.session.add(response)
            existing_response = response
        else:
            for col in update_columns:
                new_value = getattr(response, col)
                setattr(existing_response, col, new_value)

        return existing_response

    # endregion Utility Methods


class ScrapeHistoryRepository(BaseRepository[ScrapeHistory]):
    def __init__(self, session: Session):
        super().__init__(ScrapeHistory, session)
