from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    total_requests: int
    open_requests: int
    resolved_requests: int
    by_category: dict[str, int]
    by_priority: dict[str, int]
    by_status: dict[str, int]
    reviewed_count: int
    ai_failure_count: int
    avg_resolution_hours: float | None = None
