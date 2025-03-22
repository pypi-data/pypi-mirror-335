"""Agent-specific API operations."""

from typing import Dict, Any
from ..http import HTTPClient

AGENT_TYPE = "sdk_v0"


class AgentAPI:
    """Agent management API endpoints."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def list(self) -> Dict:
        """Get all agents."""
        return self.http.get("agents")

    def get(self, username: str) -> Dict:
        """Get agent details by username."""
        return self.http.get(f"agents/{username}")

    def create(
        self,
        username: str,
        name: str,
        description: str = None,
        url: str = None,
        visibility: str = "private",
    ) -> Dict:
        """Create a new agent."""
        # required
        data = {
            "username": username,
            "name": name,
            "visibility": visibility,
            "agentConfig": {"url": url},
            "agentType": AGENT_TYPE,
        }
        # optional
        if description is not None:
            data["description"] = description

        return self.http.post("agents", data)

    def update(
        self,
        username: str,
        name: str = None,
        description: str = None,
        url: str = None,
        visibility: str = "private",
    ) -> Dict:
        """Create a new agent."""
        # required
        data = {
            "username": username,
            "name": name,
            "visibility": visibility,
            "agentConfig": {"url": url},
            "agentType": AGENT_TYPE,
        }
        # optional
        if description is not None:
            data["description"] = description

        return self.http.put(f"agents/{username}", data)

    def delete(self, username: str) -> Dict:
        """Delete an agent."""
        return self.http.delete(f"agents/{username}")
