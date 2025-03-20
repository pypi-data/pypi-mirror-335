from datetime import datetime

from pydantic import BaseModel

from igx_api.l2.types.organization import OrganizationId
from igx_api.l2.types.user import UserId


class Event(BaseModel):
    """A single event body representing a single action that has happened in the Platform."""

    timestamp: datetime
    """The timestamp when the event was fired."""
    organization_id: OrganizationId
    """The organization that the event belongs to."""
    user_id: UserId | None
    """The user that the event belongs to, if any."""
    category: str
    """The category of the event."""
    action: str
    """The action that was performed."""
    payload: dict[str, int | float | bool | str | None]
    """The payload of the event.

    The contents of the payload are specific to the event category and action, and may contain more detailed information
    about the event that occurred.
    """
