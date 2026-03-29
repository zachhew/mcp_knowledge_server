from __future__ import annotations

from uuid import UUID

from app.application.dto.documents import DocumentDetailDTO, DocumentListItemDTO
from app.application.interfaces.repositories import DocumentRepositoryProtocol
from app.domain.models.document import Document


class DocumentService:
    def __init__(self, repository: DocumentRepositoryProtocol) -> None:
        self._repository = repository

    async def search_documents(
        self,
        query: str,
        project_id: UUID | None = None,
        limit: int = 10,
    ) -> list[DocumentListItemDTO]:
        documents = await self._repository.search(
            query=query,
            project_id=project_id,
            limit=limit,
        )
        return [self._to_list_item_dto(document) for document in documents]

    async def get_document(self, document_id: UUID) -> DocumentDetailDTO | None:
        document = await self._repository.get_by_id(document_id)
        if document is None:
            return None

        return self._to_detail_dto(document)

    @staticmethod
    def _to_list_item_dto(document: Document) -> DocumentListItemDTO:
        return DocumentListItemDTO(
            id=document.id,
            project_id=document.project_id,
            title=document.title,
            summary=document.summary,
            owner=document.owner,
            document_type=document.document_type,
            tags=document.tags,
        )

    @staticmethod
    def _to_detail_dto(document: Document) -> DocumentDetailDTO:
        return DocumentDetailDTO(
            id=document.id,
            project_id=document.project_id,
            title=document.title,
            content=document.content,
            summary=document.summary,
            owner=document.owner,
            document_type=document.document_type,
            tags=document.tags,
        )