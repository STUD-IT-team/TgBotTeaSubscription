import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

_async_session_maker = None

@dataclass
class Repositories:
    def __init__(
        self,
        transaction_repo: ITransactRepository,
        user_repo: IUserRepository,
    ):
        self.transaction_repo = transaction_repo
        self.user_repo = user_repo


async def get_sessionmaker(max_retries: int = 5, delay: int = 2) -> Any:
    global _async_session_maker
    if _async_session_maker is not None:
        return _async_session_maker
    engine = create_async_engine(
        settings.DATABASE_URL_ASYNC,
        connect_args={"server_settings": {"search_path": "bot_schema"}},
        echo=True,
        pool_pre_ping=True,
    )
    for attempt in range(max_retries):
        try:
            _async_session_maker = sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )  # type: ignore
            return _async_session_maker
        except OperationalError as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Повторная попытка подключения через {delay} секунд...")
                await asyncio.sleep(delay)
            else:
                raise RuntimeError(
                    "Не удалось подключиться к базе данных после нескольких попыток."
                )
    return None


async def get_service_locator() -> ServiceLocator:
    global _async_session_maker

        if _async_session_maker is None:
            _async_session_maker = await get_sessionmaker()
        async with _async_session_maker() as session:
            user_repo: IUserRepository = UserRepository(session)
            transaction_repo: ITransactRepository = TransactRepository(session)

            repositories = Repositories(user_repo,transaction_repo)

    #     acc_serv = AccommodationService(acc_repo)
    #     city_serv = CityService(city_repo)
    #     d_route_serv = DirectoryRouteService(d_route_repo)
    #     ent_serv = EntertainmentService(ent_repo)
    #     route_serv = RouteService(route_repo)
    #     travel_serv = TravelService(travel_repo)
    #     user_serv = UserService(user_repo)
    #     auth_serv = AuthService(user_repo)

    # city_contr = CityController(city_serv)
    # route_contr = RouteController(
    #     route_serv, travel_serv, d_route_serv, user_serv, ent_serv, acc_serv
    # )
    # d_route_contr = DirectoryRouteController(d_route_serv, city_serv)
    # acc_contr = AccommodationController(acc_serv, city_serv)
    # ent_contr = EntertainmentController(ent_serv, city_serv)
    # travel_contr = TravelController(travel_serv, user_serv, ent_serv, acc_serv)
    # user_contr = UserController(user_serv, auth_serv)

    # services = Services(
    #     acc_serv,
    #     city_serv,
    #     d_route_serv,
    #     ent_serv,
    #     route_serv,
    #     travel_serv,
    #     user_serv,
    #     auth_serv,
    # )
    # controllers = Controllers(
    #     acc_contr,
    #     route_contr,
    #     ent_contr,
    #     travel_contr,
    #     user_contr,
    #     d_route_contr,
    #     city_contr,
    # )
    return ServiceLocator(repositories)
    # return ServiceLocator(repositories, services, controllers)
