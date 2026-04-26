"""SQLite 上のライバーデータへアクセスする Repository 実装。"""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.adapters.outbound.sqlalchemy.models import (
    LiverAliasRecord,
    LiverColorRecord,
    LiverRecord,
)
from core.application.ports.outbound import LiverRepository
from core.domain.entities import (
    BranchEnum,
    LiverAliasEntity,
    LiverColorEntity,
    LiverEntity,
    LiverStatusEnum,
    LiverSummaryEntity,
)


class SqlAlchemyLiverRepository(LiverRepository):
    """SQLAlchemy ORM を使ってライバー情報を取得する。"""

    def __init__(self, session: AsyncSession) -> None:
        """利用する AsyncSession を受け取る。"""

        self._session = session

    async def find_all(
        self,
        *,
        branch: BranchEnum | None = None,
        generation: str | None = None,
        status: LiverStatusEnum | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[LiverSummaryEntity], int]:
        """条件に一致するライバー一覧と総件数を返す。"""

        conditions = self._build_list_conditions(
            branch=branch,
            generation=generation,
            status=status,
        )
        offset = (page - 1) * limit
        total_statement = select(func.count()).select_from(LiverRecord).where(*conditions)
        statement = (
            select(LiverRecord)
            .options(selectinload(LiverRecord.colors))
            .where(*conditions)
            .order_by(LiverRecord.name, LiverRecord.id)
            .offset(offset)
            .limit(limit)
        )

        total = await self._session.scalar(total_statement) or 0
        records = list((await self._session.scalars(statement)).all())
        items = [self._to_summary_entity(record) for record in records]
        return items, int(total)

    async def find_by_id(self, liver_id: UUID) -> LiverEntity | None:
        """ID に一致するライバー詳細を返す。"""

        statement = (
            select(LiverRecord)
            .options(
                selectinload(LiverRecord.aliases),
                selectinload(LiverRecord.colors),
            )
            .where(LiverRecord.id == str(liver_id))
        )
        record = await self._session.scalar(statement)
        if record is None:
            return None
        return self._to_liver_entity(record)

    async def search(
        self,
        *,
        query: str,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[LiverSummaryEntity], int]:
        """名前や別名に一致するライバー一覧と総件数を返す。"""

        normalized_query = query.strip()
        if not normalized_query:
            return [], 0

        offset = (page - 1) * limit
        pattern = f"%{normalized_query}%"
        search_condition = or_(
            LiverRecord.name.ilike(pattern),
            LiverRecord.kana_name.ilike(pattern),
            LiverRecord.english_name.ilike(pattern),
            LiverAliasRecord.alias.ilike(pattern),
        )
        matched_ids_statement = (
            select(
                LiverRecord.id.label("id"),
                LiverRecord.name.label("name"),
            )
            .outerjoin(LiverAliasRecord, LiverAliasRecord.liver_id == LiverRecord.id)
            .where(search_condition)
            .distinct()
        )
        total_statement = select(func.count()).select_from(
            matched_ids_statement.subquery()
        )
        page_statement = (
            matched_ids_statement.order_by(LiverRecord.name, LiverRecord.id)
            .offset(offset)
            .limit(limit)
        )

        total = await self._session.scalar(total_statement) or 0
        rows = list((await self._session.execute(page_statement)).all())
        matched_ids = [row.id for row in rows]
        if not matched_ids:
            return [], int(total)

        records_statement = (
            select(LiverRecord)
            .options(selectinload(LiverRecord.colors))
            .where(LiverRecord.id.in_(matched_ids))
        )
        records = list((await self._session.scalars(records_statement)).all())
        records_by_id = {record.id: record for record in records}
        items = [
            self._to_summary_entity(records_by_id[matched_id])
            for matched_id in matched_ids
            if matched_id in records_by_id
        ]
        return items, int(total)

    async def find_current_color(self, liver_id: UUID) -> LiverColorEntity | None:
        """ライバーの現在カラー情報を返す。"""

        statement = (
            select(LiverColorRecord)
            .where(
                LiverColorRecord.liver_id == str(liver_id),
                LiverColorRecord.is_current.is_(True),
            )
            .order_by(LiverColorRecord.updated_at.desc(), LiverColorRecord.id.desc())
            .limit(1)
        )
        record = await self._session.scalar(statement)
        if record is None:
            return None
        return self._to_color_entity(record)

    @staticmethod
    def _build_list_conditions(
        *,
        branch: BranchEnum | None,
        generation: str | None,
        status: LiverStatusEnum | None,
    ) -> list[object]:
        """一覧取得で使う WHERE 条件を組み立てる。"""

        conditions: list[object] = []
        if branch is not None:
            conditions.append(LiverRecord.branch == branch)
        if generation is not None:
            conditions.append(LiverRecord.generation == generation)
        if status is not None:
            conditions.append(LiverRecord.status == status)
        return conditions

    def _to_summary_entity(self, record: LiverRecord) -> LiverSummaryEntity:
        """一覧向けエンティティへ変換する。"""

        return LiverSummaryEntity(
            id=UUID(record.id),
            name=record.name,
            kana_name=record.kana_name,
            english_name=record.english_name,
            branch=record.branch,
            generation=record.generation,
            status=record.status,
            current_color=self._resolve_current_color(record.colors),
        )

    def _to_liver_entity(self, record: LiverRecord) -> LiverEntity:
        """詳細向けエンティティへ変換する。"""

        return LiverEntity(
            id=UUID(record.id),
            name=record.name,
            kana_name=record.kana_name,
            english_name=record.english_name,
            branch=record.branch,
            generation=record.generation,
            status=record.status,
            debuted_at=record.debuted_at,
            retired_at=record.retired_at,
            aliases=[self._to_alias_entity(alias) for alias in record.aliases],
            current_color=self._resolve_current_color(record.colors),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    @staticmethod
    def _to_alias_entity(record: LiverAliasRecord) -> LiverAliasEntity:
        """別名レコードをドメインエンティティへ変換する。"""

        return LiverAliasEntity(
            id=UUID(record.id),
            alias=record.alias,
            alias_type=record.alias_type,
            locale=record.locale,
        )

    @staticmethod
    def _to_color_entity(record: LiverColorRecord) -> LiverColorEntity:
        """カラー履歴レコードをドメインエンティティへ変換する。"""

        return LiverColorEntity(
            hex=record.hex,
            r=record.r,
            g=record.g,
            b=record.b,
            display_name=record.display_name,
            is_official=record.is_official,
            source=record.source,
            source_url=record.source_url,
            note=record.note,
            updated_at=record.updated_at,
        )

    def _resolve_current_color(
        self,
        records: Sequence[LiverColorRecord],
    ) -> LiverColorEntity | None:
        """現在色フラグが立ったカラーを 1 件だけ取り出す。"""

        current_records = [record for record in records if record.is_current]
        if not current_records:
            return None
        current_record = max(
            current_records,
            key=lambda record: (record.updated_at, record.id),
        )
        return self._to_color_entity(current_record)
