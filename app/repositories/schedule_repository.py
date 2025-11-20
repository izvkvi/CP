from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime
from typing import List

from app.entities.vigil_enum import VigilEnumEntity
from app.interfaces.interfaces import IScheduleRepository
from app.models.vigils_enum_model import VigilEnum
from app.models.schedule_gc_model import ScheduleGC
from app.models.schedule_vigil_model import ScheduleVigil
from app.exceptions.exceptions import VigilsTypeNotFound


class ScheduleRepository(IScheduleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_vigils(
        self,
        start_at: datetime = None,
        end_at: datetime = None,
        user_ids: List[UUID] = None,
        vigil_ids: List[UUID] = None,
        ignore_id: int = None,
    ):
        if vigil_ids:
            if ignore_id in vigil_ids:
                vigil_ids.remove(ignore_id)

        stmt = select(ScheduleVigil)
        if start_at:
            stmt = stmt.where(ScheduleVigil.date >= start_at)
        if end_at:
            stmt = stmt.where(ScheduleVigil.date <= end_at)
        if user_ids:
            stmt = stmt.where(ScheduleVigil.user_id.in_(user_ids))
        if vigil_ids:
            stmt = stmt.where(ScheduleVigil.vigil_id.in_(vigil_ids))
        elif ignore_id:
            stmt = stmt.where(ScheduleVigil.vigil_id != ignore_id)

        result = (await self.session.execute(stmt)).scalars().all()
        return result

    async def save_responsible_schedule(
        self,
        responsible: dict[str, int],
        start_date: datetime,
        end_date: datetime,
    ):
        """
        Метод для загрузки данных об графике ответственных в БД, предварительно удалив старые данные для предостережения от пересечений
        """
        try:
            stmt = select(VigilEnum).where(VigilEnum.is_deleted.is_(False))
            result = (await self.session.execute(stmt)).scalars().all()

            if not result:
                raise VigilsTypeNotFound("В БД отсутствуют типы дежурств")

            vigil_resp_id = next(
                (v.id for v in result if v.name == "Ответственный"), None
            )
            if not vigil_resp_id:
                raise VigilsTypeNotFound(
                    "В БД отсутствуют тип дежурства 'Ответственный'"
                )

            stmt = select(ScheduleVigil).where(
                and_(
                    ScheduleVigil.date.between(start_date, end_date),
                    ScheduleVigil.vigil_id == vigil_resp_id,
                )
            )
            existing = (await self.session.execute(stmt)).scalars().all()

            for ev in existing:
                await self.session.delete(ev)

            for date, user_id in responsible.items():
                schedule = ScheduleVigil(
                    date=datetime.strptime(date, "%d-%m-%Y"),
                    user_id=user_id,
                    vigil_id=vigil_resp_id,
                )
                self.session.add(schedule)

            await self.session.commit()

        except (IntegrityError, SQLAlchemyError) as e:
            await self.session.rollback()
            raise e
        except Exception as e:
            await self.session.rollback()
            raise e

    async def save_group_control_schedule(
        self, group_control_schedule: list, start_date, end_date
    ):
        """
        Сохраняет записи графика группы контроля.
        Сначала удаляет старые записи за период, затем добавляет новые.
        """
        try:
            stmt = select(ScheduleGC).where(
                ScheduleGC.date.between(start_date, end_date)
            )
            result = (await self.session.execute(stmt)).scalars().all()
            for gc in result:
                await self.session.delete(gc)

            for gc_date in group_control_schedule:
                self.session.add(ScheduleGC(date=gc_date))

            await self.session.commit()

        except IntegrityError as e:
            await self.session.rollback()
            raise e
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
        except Exception as e:
            await self.session.rollback()
            raise e

    async def save_vigils_schedule(
        self, vigils_schedule: dict, start_date: datetime, end_date: datetime
    ):
        try:
            stmt = select(VigilEnum).where(VigilEnum.is_deleted.is_(False))
            vigils_types = (await self.session.execute(stmt)).scalars().all()

            if not vigils_types:
                raise VigilsTypeNotFound("В БД отсутствуют типы дежурств")

            vigil_resp_id = next(
                (v.id for v in vigils_types if v.name == "Ответственный"), None
            )
            if not vigil_resp_id:
                raise VigilsTypeNotFound(
                    "В БД отсутствуют тип дежурства 'Ответственный'"
                )

            stmt = select(ScheduleVigil).where(
                and_(
                    ScheduleVigil.date.between(start_date, end_date),
                    ScheduleVigil.vigil_id != vigil_resp_id,
                )
            )
            old_vigils = (await self.session.execute(stmt)).scalars().all()

            for v in old_vigils:
                await self.session.delete(v)

            for user_id, user_data in vigils_schedule.items():
                user_excel_position = user_data.get("position")
                user_excel_schedule = user_data.get("schedule")

                for date_str, user_excel_vigil in user_excel_schedule.items():
                    if not user_excel_vigil or user_excel_vigil == "-":
                        continue

                    temp_str = user_excel_vigil
                    if "ЗН Р" in temp_str:
                        temp_str = temp_str.replace("ЗН Р", "")

                        for item in vigils_types:
                            if (
                                item.name_in_csv == "ЗН Р"
                                and item.post_in_csv == user_excel_position
                            ):
                                schedule = ScheduleVigil(
                                    date=datetime.strptime(
                                        date_str, "%Y-%m-%d"
                                    ),
                                    user_id=user_id,
                                    vigil_id=item.id,
                                )
                                self.session.add(schedule)
                                break

                    if "РГ" in temp_str:
                        temp_str = temp_str.replace("РГ", "")

                        for item in vigils_types:
                            if item.name_in_csv == "РГ":
                                schedule = ScheduleVigil(
                                    date=datetime.strptime(
                                        date_str, "%Y-%m-%d"
                                    ),
                                    user_id=user_id,
                                    vigil_id=item.id,
                                )
                                self.session.add(schedule)
                                break

                    if "Р" in temp_str:
                        temp_str = temp_str.replace("Р", "")

                        for item in vigils_types:
                            if (
                                item.name_in_csv == "Р"
                                and item.post_in_csv == user_excel_position
                            ):
                                schedule = ScheduleVigil(
                                    date=datetime.strptime(
                                        date_str, "%Y-%m-%d"
                                    ),
                                    user_id=user_id,
                                    vigil_id=item.id,
                                )
                                self.session.add(schedule)
                                break

                    if "ЗН ДТП" in temp_str:
                        temp_str = temp_str.replace("ЗН ДТП", "")

                        for item in vigils_types:
                            if item.name_in_csv == "ЗН ДТП":
                                schedule = ScheduleVigil(
                                    date=datetime.strptime(
                                        date_str, "%Y-%m-%d"
                                    ),
                                    user_id=user_id,
                                    vigil_id=item.id,
                                )
                                self.session.add(schedule)
                                break

                    if "ДТП" in temp_str:
                        temp_str = temp_str.replace("ДТП", "")

                        for item in vigils_types:
                            if item.name_in_csv == "ДТП":
                                schedule = ScheduleVigil(
                                    date=datetime.strptime(
                                        date_str, "%Y-%m-%d"
                                    ),
                                    user_id=user_id,
                                    vigil_id=item.id,
                                )
                                self.session.add(schedule)
                                break

                    for item in vigils_types:
                        if item.name_in_csv in temp_str:
                            temp_str = temp_str.replace(item.name_in_csv, "")
                            schedule = ScheduleVigil(
                                date=datetime.strptime(date_str, "%Y-%m-%d"),
                                user_id=user_id,
                                vigil_id=item.id,
                            )
                            self.session.add(schedule)

            await self.session.commit()

        except IntegrityError as e:
            await self.session.rollback()
            raise e
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_vigils_type(self, name: List[str] = None):
        stmt = select(VigilEnum).where(VigilEnum.is_deleted.is_(False))
        if name:
            stmt = stmt.where(VigilEnum.name.in_(name))
        result = (await self.session.execute(stmt)).scalars().all()
        if not result:
            raise VigilsTypeNotFound(
                "Vigils type not added in db, maybe you not run utils route to create base working data"
            )
        return result

    async def create_vigils_type(
        self, data: List[VigilEnumEntity]
    ) -> List[VigilEnumEntity]:
        if not data:
            return []
        vigils_orm = [VigilEnum(**v.to_dict()) for v in data]

        self.session.add_all(vigils_orm)
        await self.session.commit()
        return [VigilEnumEntity(
            id=v.id,
            name=v.name,
            is_deleted=v.is_deleted,
            name_in_csv=v.name_in_csv,
            post_in_csv=v.post_in_csv
        ) for v in vigils_orm]
