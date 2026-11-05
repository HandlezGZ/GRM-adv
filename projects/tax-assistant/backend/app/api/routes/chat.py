from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.repositories.chat_repository import ChatRepository
from backend.app.repositories.tax_document_repository import TaxDocumentRepository
from backend.app.schemas.chat import (
    ChatMessageRead,
    ChatQueryRequest,
    ChatQueryResponse,
    ChatSessionCreate,
    ChatSessionRead,
)
from backend.app.services.retrieval import TaxRetrievalService

router = APIRouter(prefix="/chat", tags=["Chat"])
retrieval_service = TaxRetrievalService()


@router.post("/sessions", response_model=ChatSessionRead)
def create_session(
    payload: ChatSessionCreate,
    db: Session = Depends(get_db),
):
    doc_repo = TaxDocumentRepository(db)
    chat_repo = ChatRepository(db)

    doc = doc_repo.get_by_id(payload.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento fiscal não encontrado.")

    title = payload.title or f"Consulta - {doc.filename}"
    session = chat_repo.create_session(document_id=doc.id, title=title)
    return session


@router.post("/sessions/{session_id}/query", response_model=ChatQueryResponse)
def query_session(
    session_id: str,
    payload: ChatQueryRequest,
    db: Session = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    doc_repo = TaxDocumentRepository(db)

    session = chat_repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão de chat não encontrada.")

    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="A pergunta não pode ser vazia.")

    # Save user message
    chat_repo.add_message(session_id, role="user", content=question)

    # Get document chunks
    chunks = doc_repo.get_chunks_by_document_id(session.document_id)

    # Retrieval and grounded answer
    ans_dict = retrieval_service.answer_query(question, chunks)

    # Store assistant message with citations
    citations_data = [c.model_dump() for c in ans_dict["citations"]]
    chat_repo.add_message(
        session_id=session_id,
        role="assistant",
        content=ans_dict["answer"],
        citations=citations_data,
    )

    return ChatQueryResponse(
        session_id=session_id,
        question=question,
        answer=ans_dict["answer"],
        citations=ans_dict["citations"],
        is_grounded=ans_dict["is_grounded"],
    )


@router.get("/sessions/{session_id}/history", response_model=list[ChatMessageRead])
def get_session_history(
    session_id: str,
    db: Session = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    session = chat_repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão de chat não encontrada.")

    return chat_repo.get_history(session_id)
