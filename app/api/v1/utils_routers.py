from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_session
from app.entities.post import PostEntity
from app.entities.rank import RankEntity
from app.entities.company_duty import CompanyDutyEntity
from app.entities.vigil_enum import VigilEnumEntity

from app.entities.user import UserEntity
from app.exceptions.exceptions import UserAlreadyExistsError

from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

from app.services.utils_service import UtilsService


router = APIRouter(prefix="/utils", tags=["utils"])


@router.get(
    "/update_database_config",
    description="Вносит данные в справочники. Запуск возможен только если таблицы пустые",
)
async def update_data_config(session=Depends(get_session)):
    """Роут для того, чтобы создавать необходимые для функционирования данные, по идеи запускается при развертывании системы."""
    try:
        service = UtilsService(
            user_repo=UserRepository(session),
            schedule_repo=ScheduleRepository(session),
        )
        user_service = UserService(UserRepository(session))
        exist_superuser = await service.get_superusers()
        if exist_superuser:
            raise HTTPException(
                status_code=400,
                detail="Суперюзер уже существует, запуская данный метод вы можете нарушить работу всей системы так как сотрете данные справочников.",
            )

        vigil = [
            VigilEnumEntity(
                name="Дежурный по роте",
                is_deleted=False,
                name_in_csv="Р",
                post_in_csv="ДЖ",
            ),
            VigilEnumEntity(
                name="Дневальный по роте",
                is_deleted=False,
                name_in_csv="Р",
                post_in_csv="ДН",
            ),
            VigilEnumEntity(
                name="Заступающий дежурный по роте",
                is_deleted=False,
                name_in_csv="ЗН Р",
                post_in_csv="ДЖ",
            ),
            VigilEnumEntity(
                name="Заступающий дневальный по роте",
                is_deleted=False,
                name_in_csv="ЗН Р",
                post_in_csv="ДН",
            ),
            VigilEnumEntity(
                name="Ответственный",
                is_deleted=False,
                name_in_csv="Ответственный",
                post_in_csv="Ответственный",
            ),
            VigilEnumEntity(
                name="Рабочая группа",
                is_deleted=False,
                name_in_csv="РГ",
                post_in_csv="РГ",
            ),
            VigilEnumEntity(
                name="Дежурный по технопарку",
                is_deleted=False,
                name_in_csv="ДТП",
                post_in_csv="ДТП",
            ),
            VigilEnumEntity(
                name="Заступающий дежурный по технопарку",
                is_deleted=False,
                name_in_csv="ЗН ДТП",
                post_in_csv="ЗН ДТП",
            ),
        ]

        vigils_type = await service.set_standard_vigils(data=vigil)
        company_duties = [
            CompanyDutyEntity(name="СОЗДАТЕЛЬ"),
            CompanyDutyEntity(name="Каптер"),
            CompanyDutyEntity(name="Принтер/плоттер"),
            CompanyDutyEntity(name="Полив цветов"),
            CompanyDutyEntity(name="Аквариум"),
            CompanyDutyEntity(name="Спорт-организатор"),
            CompanyDutyEntity(name="Учет боевой подготовки"),
            CompanyDutyEntity(name="Писарь"),
            CompanyDutyEntity(name="Боевые листки"),
            CompanyDutyEntity(name="Подведение итогов"),
            CompanyDutyEntity(name="ВПР"),
            CompanyDutyEntity(name="Трудоустройство"),
            CompanyDutyEntity(name="Наука"),
            CompanyDutyEntity(name="Сборник НР"),
            CompanyDutyEntity(name="Графики нарядов"),
            CompanyDutyEntity(name="Увольнения"),
            CompanyDutyEntity(name="План выходных дней"),
            CompanyDutyEntity(name="Журнал проведения бесед"),
            CompanyDutyEntity(name="Казначей"),
            CompanyDutyEntity(name="Медиагруппа"),
            CompanyDutyEntity(name="ЗГТ"),
            CompanyDutyEntity(name="Культ-массы"),
            CompanyDutyEntity(name="Почта"),
            CompanyDutyEntity(name="Парикхмахер"),
            CompanyDutyEntity(name="План работы НР"),
            CompanyDutyEntity(name="Лазарет"),
            CompanyDutyEntity(name="Библиотека"),
            CompanyDutyEntity(name="Газеты"),
            CompanyDutyEntity(name="Журнал автовладельцев"),
            CompanyDutyEntity(name="Профессионально-должностная подготовка"),
            CompanyDutyEntity(name="Отчет с нарастающим итогом"),
            CompanyDutyEntity(name="Регистрация ПО ФИПС"),
            CompanyDutyEntity(name="Регистрация ПО ВАС"),
            CompanyDutyEntity(name="Подбор кандидатов НР"),
            CompanyDutyEntity(name="Глажка формы"),
            CompanyDutyEntity(name="Заполнение вечерней поверки"),
        ]
        duties = await service.set_standard_duties(data=company_duties)

        ranks = [
            RankEntity(name="Рядовой", short_name="ряд."),
            RankEntity(name="Ефрейтор", short_name="ефр."),
            RankEntity(name="Младший сержант", short_name="мл. с-т"),
            RankEntity(name="Сержант", short_name="с-т"),
            RankEntity(name="Старший сержант", short_name="ст. с-т"),
            RankEntity(name="Старшина", short_name="с-на"),
            RankEntity(name="Прапорщик", short_name="пр-к"),
            RankEntity(name="Старший прапорщик", short_name="ст. пр-к"),
            RankEntity(name="Младший лейтенант", short_name="мл. л-т"),
            RankEntity(name="Лейтенант", short_name="л-т"),
            RankEntity(name="Старший лейтенант", short_name="ст. л-т"),
            RankEntity(name="Капитан", short_name="к-н"),
            RankEntity(name="Майор", short_name="м-р"),
            RankEntity(name="Подполковник", short_name="п/п-к"),
            RankEntity(name="Полковник", short_name="п-к"),
        ]
        ranks = await service.set_standard_ranks(data=ranks)
        posts = [
            PostEntity(name="Оператор роты (научной)"),
            PostEntity(name="Старший оператор роты (научной)"),
            PostEntity(name="Командир отделения роты (научной)"),
            PostEntity(name="Заместитель командира взвода роты (научной)"),
            PostEntity(name="Командир взвода роты (научной)"),
            PostEntity(name="Старшина роты (научной)"),
            PostEntity(name="Командир роты (научной)"),
        ]
        posts = await service.set_standard_posts(data=posts)
        # ТЕСТОВЫЙ АККАУНТ МОДЕРАТОРА В ПОСЛЕДСТВИИ ДОЛЖЕН БЫТЬ АККАУНТ КОМ РОТЫ (пока непонятно по логике, скорее всего будет не только ком роты но и какая-то ротная обязанность)
        user = UserEntity(
            username="admin",
            name="admin",
            surname="admin",
            second_name="admin",
            invocation="Аккаунт модератора",
            hashed_password="admin",
            is_superuser=True,
            post_id=posts[-1].id,
            rank_id=ranks[-1].id,
        )
        created_user = await user_service.create(user)

        return {
            "duties": [d.to_dict() for d in duties],
            "vigils_type": [v.to_dict() for v in vigils_type],
            "ranks": [rank.to_dict() for rank in ranks],
            "posts": [post.to_dict() for post in posts],
            "admin_user": created_user.to_dict(),
        }
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
