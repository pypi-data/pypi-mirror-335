"""Run-specific API operations."""

from typing import Dict, List, TypedDict, NotRequired
from ..http import HTTPClient


class ChallengeParticipant(TypedDict):
    """A participant in a challenge."""

    agent: str
    role: NotRequired[str]


class RunAPI:
    """Run management API endpoints."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def create(
        self, challenge_slug: str, participants: List[ChallengeParticipant]
    ) -> Dict:
        """Create a new run."""

        return self.http.post(
            "jobs",
            {
                "challenge": challenge_slug,
                "participants": participants,
            },
        )

    def get(self, run_id: str) -> Dict:
        """Get run details by ID."""
        return self.http.get(f"runs/{run_id}")
