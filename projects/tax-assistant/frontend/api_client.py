import os
from typing import Any

import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8002/api/v1")


class LexTaxAPIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def get_metrics(self) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{self.base_url}/dashboard/metrics")
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return {
            "total_documents": 0,
            "total_tax_amount": 0.0,
            "total_pages_analyzed": 0,
            "documents_by_type": {},
            "taxes_distribution": {},
            "average_confidence_score": 0.0,
        }

    def list_documents(self, doc_type: str | None = None) -> list[dict[str, Any]]:
        params = {}
        if doc_type and doc_type != "TODOS":
            params["doc_type"] = doc_type
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{self.base_url}/documents", params=params)
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return []

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{self.base_url}/documents/{doc_id}")
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return None

    def upload_document(self, filename: str, content_bytes: bytes) -> dict[str, Any] | None:
        try:
            files = {"file": (filename, content_bytes, "application/pdf" if filename.endswith(".pdf") else "text/plain")}
            with httpx.Client(timeout=15.0) as client:
                res = client.post(f"{self.base_url}/documents/upload", files=files)
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return None

    def intake_text_document(self, filename: str, text: str, doc_type: str | None = None) -> dict[str, Any] | None:
        try:
            payload = {"filename": filename, "text": text, "document_type": doc_type}
            with httpx.Client(timeout=10.0) as client:
                res = client.post(f"{self.base_url}/documents/text", json=payload)
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return None

    def extract_document(self, doc_id: str, force: bool = False) -> dict[str, Any] | None:
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(f"{self.base_url}/documents/{doc_id}/extract?force_recompute={force}")
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return None

    def get_summary(self, doc_id: str) -> dict[str, Any] | None:
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(f"{self.base_url}/documents/{doc_id}/summary")
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return None

    def create_chat_session(self, doc_id: str, title: str = "Consulta") -> dict[str, Any] | None:
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.post(f"{self.base_url}/chat/sessions", json={"document_id": doc_id, "title": title})
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return None

    def query_chat_session(self, session_id: str, question: str) -> dict[str, Any] | None:
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(f"{self.base_url}/chat/sessions/{session_id}/query", json={"question": question})
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return None

    def get_chat_history(self, session_id: str) -> list[dict[str, Any]]:
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{self.base_url}/chat/sessions/{session_id}/history")
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return []


api_client = LexTaxAPIClient()
