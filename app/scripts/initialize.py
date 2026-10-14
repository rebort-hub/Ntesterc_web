from app.api.v1.system.seed import seed_system_data


class InitializeData:
    async def seed(self) -> None:
        await seed_system_data()
