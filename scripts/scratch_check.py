import asyncio

from app.infrastructure.db.session import SessionFactory
from app.infrastructure.repositories.document_repository import SQLAlchemyDocumentRepository
from app.infrastructure.repositories.project_repository import SQLAlchemyProjectRepository
from app.infrastructure.repositories.task_repository import SQLAlchemyTaskRepository


async def main() -> None:
    async with SessionFactory() as session:
        project_repo = SQLAlchemyProjectRepository(session)
        document_repo = SQLAlchemyDocumentRepository(session)
        task_repo = SQLAlchemyTaskRepository(session)

        projects = await project_repo.list_all()
        print("Projects:", [project.slug for project in projects])

        docs = await document_repo.search("Aurora")
        print("Documents:", [doc.title for doc in docs])

        tasks = await task_repo.search(query="metrics")
        print("Tasks:", [task.title for task in tasks])


if __name__ == "__main__":
    asyncio.run(main())
