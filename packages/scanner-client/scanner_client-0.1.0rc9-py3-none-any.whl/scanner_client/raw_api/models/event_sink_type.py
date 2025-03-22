from enum import Enum


class EventSinkType(str, Enum):
    SLACK = "Slack"
    TINES = "Tines"
    UNKNOWN = "Unknown"
    WEBHOOK = "Webhook"

    def __str__(self) -> str:
        return str(self.value)
