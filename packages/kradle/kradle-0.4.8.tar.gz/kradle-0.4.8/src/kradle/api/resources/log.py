"""Run-specific API operations."""

from typing import Dict, List, TypedDict, NotRequired
from ..http import HTTPClient
import json


class LogAPI:
    """Log management API endpoints."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def create(self, run_id, participant_id, message):
        if not isinstance(message, str):
            message = json.dumps(message)
        return self.http.post(
            f"runs/{run_id}/logs",
            {"message": message, "participantId": participant_id},
        )
