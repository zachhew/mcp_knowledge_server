import asyncio

from app.infrastructure.db.session import SessionFactory
from app.infrastructure.repositories.project_repository import SQLAlchemyProjectRepository


async def main() -> None:
    async with SessionFactory() as session:
        repo = SQLAlchemyProjectRepository(session)
        projects = await repo.list_all()
        for project in projects:
            print(project.slug, project.id)


if __name__ == "__main__":
    asyncio.run(main())