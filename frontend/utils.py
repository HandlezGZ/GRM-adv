import logging
import os
from typing import Any

import httpx

logger = logging.getLogger("lexflow.frontend")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_V1 = f"{BACKEND_URL}/api/v1"


def get_health() -> dict[str, Any] | None:
    try:
        with httpx.Client(timeout=3.0) as client:
            res = client.get(f"{BACKEND_URL}/health")
            if res.status_code == 200:
                return res.json()
    except httpx.HTTPError as err:
        logger.warning("Erro ao consultar health check: %s", err)
    return None


def get_metrics() -> dict[str, Any] | None:
    try:
        with httpx.Client(timeout=5.0) as client:
            res = client.get(f"{API_V1}/dashboard/metrics")
            if res.status_code == 200:
                return res.json()
    except httpx.HTTPError as err:
        logger.warning("Erro ao consultar métricas: %s", err)
    return None


def list_requests(
    status: str | None = None,
    category: str | None = None,
    priority: str | None = None,
    search: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"limit": limit}
    if status and status != "TODOS":
        params["status"] = status
    if category and category != "TODAS":
        params["category"] = category
    if priority and priority != "TODAS":
        params["priority"] = priority
    if search:
        params["search"] = search

    try:
        with httpx.Client(timeout=5.0) as client:
            res = client.get(f"{API_V1}/requests", params=params)
            if res.status_code == 200:
                return res.json().get("items", [])
    except httpx.HTTPError as err:
        logger.warning("Erro ao listar solicitações: %s", err)
    return []


def get_request(request_id: str) -> dict[str, Any] | None:
    try:
        with httpx.Client(timeout=5.0) as client:
            res = client.get(f"{API_V1}/requests/{request_id}")
            if res.status_code == 200:
                return res.json()
    except httpx.HTTPError as err:
        logger.warning("Erro ao obter solicitação %s: %s", request_id, err)
    return None


def create_request(payload: dict[str, Any]) -> tuple[bool, Any]:
    try:
        with httpx.Client(timeout=5.0) as client:
            res = client.post(f"{API_V1}/requests", json=payload)
            if res.status_code == 201:
                return True, res.json()
            return False, res.json().get("detail", "Erro ao criar solicitação.")
    except httpx.HTTPError as err:
        return False, str(err)


def classify_request(request_id: str) -> tuple[bool, Any]:
    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(f"{API_V1}/requests/{request_id}/classify")
            if res.status_code == 200:
                return True, res.json()
            return False, res.json().get("detail", "Erro ao classificar.")
    except httpx.HTTPError as err:
        return False, str(err)


def review_request(
    request_id: str, payload: dict[str, Any]
) -> tuple[bool, Any]:
    try:
        with httpx.Client(timeout=5.0) as client:
            res = client.post(f"{API_V1}/requests/{request_id}/review", json=payload)
            if res.status_code == 200:
                return True, res.json()
            return False, res.json().get("detail", "Erro ao revisar.")
    except httpx.HTTPError as err:
        return False, str(err)


def update_status(
    request_id: str, new_status: str, reason: str | None = None
) -> tuple[bool, Any]:
    try:
        payload = {"new_status": new_status, "reason": reason, "actor": "demo_user"}
        with httpx.Client(timeout=5.0) as client:
            res = client.patch(f"{API_V1}/requests/{request_id}/status", json=payload)
            if res.status_code == 200:
                return True, res.json()
            return False, res.json().get("detail", "Erro na transição.")
    except httpx.HTTPError as err:
        return False, str(err)


def get_request_events(request_id: str) -> list[dict[str, Any]]:
    try:
        with httpx.Client(timeout=5.0) as client:
            res = client.get(f"{API_V1}/requests/{request_id}/events")
            if res.status_code == 200:
                return res.json()
    except httpx.HTTPError as err:
        logger.warning("Erro ao buscar eventos de %s: %s", request_id, err)
    return []


def list_failures() -> list[dict[str, Any]]:
    try:
        with httpx.Client(timeout=5.0) as client:
            res = client.get(f"{API_V1}/classification/failures")
            if res.status_code == 200:
                return res.json()
    except httpx.HTTPError as err:
        logger.warning("Erro ao listar falhas: %s", err)
    return []
