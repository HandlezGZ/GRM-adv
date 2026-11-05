import os
from typing import Any, Optional

import requests

API_BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8001")


def get_health() -> dict[str, Any]:
    try:
        res = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return res.json() if res.status_code == 200 else {"status": "unhealthy"}
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}


def get_dashboard_metrics() -> Optional[dict[str, Any]]:
    try:
        res = requests.get(f"{API_BASE_URL}/api/v1/dashboard/metrics", timeout=10)
        return res.json() if res.status_code == 200 else None
    except Exception:
        return None


def get_datasets() -> list[dict[str, Any]]:
    try:
        res = requests.get(f"{API_BASE_URL}/api/v1/datasets", timeout=10)
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []


def get_dataset_cases(dataset_id: str) -> list[dict[str, Any]]:
    try:
        res = requests.get(f"{API_BASE_URL}/api/v1/datasets/{dataset_id}/cases", timeout=10)
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []


def create_test_case(dataset_id: str, payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    try:
        res = requests.post(f"{API_BASE_URL}/api/v1/datasets/{dataset_id}/cases", json=payload, timeout=10)
        return res.json() if res.status_code == 201 else None
    except Exception:
        return None


def get_prompts() -> list[dict[str, Any]]:
    try:
        res = requests.get(f"{API_BASE_URL}/api/v1/prompts", timeout=10)
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []


def get_eval_runs() -> list[dict[str, Any]]:
    try:
        res = requests.get(f"{API_BASE_URL}/api/v1/eval/runs", timeout=10)
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []


def get_eval_run_detail(run_id: str) -> Optional[dict[str, Any]]:
    try:
        res = requests.get(f"{API_BASE_URL}/api/v1/eval/runs/{run_id}", timeout=10)
        return res.json() if res.status_code == 200 else None
    except Exception:
        return None


def trigger_evaluation(payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    try:
        res = requests.post(f"{API_BASE_URL}/api/v1/eval/run", json=payload, timeout=60)
        return res.json() if res.status_code == 201 else None
    except Exception:
        return None


def compare_runs(run_a_id: str, run_b_id: str) -> Optional[dict[str, Any]]:
    try:
        res = requests.get(
            f"{API_BASE_URL}/api/v1/eval/compare",
            params={"run_a_id": run_a_id, "run_b_id": run_b_id},
            timeout=15,
        )
        return res.json() if res.status_code == 200 else None
    except Exception:
        return None


def get_failures(dataset_id: Optional[str] = None, reason: Optional[str] = None) -> list[dict[str, Any]]:
    try:
        params = {}
        if dataset_id:
            params["dataset_id"] = dataset_id
        if reason:
            params["reason"] = reason
        res = requests.get(f"{API_BASE_URL}/api/v1/eval/failures", params=params, timeout=15)
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []
