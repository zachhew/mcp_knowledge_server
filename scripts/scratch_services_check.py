import asyncio

from app.application.services.document_service import DocumentService
from app.application.services.project_service import ProjectService
from app.application.services.task_service import TaskService
from app.infrastructure.db.session import SessionFactory
from app.infrastructure.repositories.document_repository import SQLAlchemyDocumentRepository
from app.infrastructure.repositories.project_repository import SQLAlchemyProjectRepository
from app.infrastructure.repositories.task_repository import SQLAlchemyTaskRepository


async def main() -> None:
    async with SessionFactory() as session:
        project_repo = SQLAlchemyProjectRepository(session)
        document_repo = SQLAlchemyDocumentRepository(session)
        task_repo = SQLAlchemyTaskRepository(session)

        document_service = DocumentService(document_repo)
        task_service = TaskService(task_repo)
        project_service = ProjectService(project_repo, document_repo, task_repo)

        documents = await document_service.search_documents("Aurora")
        print("DocumentService.search_documents:", [item.title for item in documents])

        tasks = await task_service.search_tasks(query="metrics")
        print("TaskService.search_tasks:", [item.title for item in tasks])

        context = await project_service.build_project_context("aurora")
        if context is not None:
            print("ProjectService.build_project_context.project:", context.project.slug)
            print(
                "ProjectService.build_project_context.documents:",
                [item.title for item in context.recent_documents],
            )
            print(
                "ProjectService.build_project_context.open_tasks:",
                [item.title for item in context.open_tasks],
            )


if __name__ == "__main__":
    asyncio.run(main())