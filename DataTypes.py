from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class SentDate:
    year: int
    month: int
    day: int
    weekday: int

@dataclass_json
@dataclass
class Notify:
    notify_id: str
    day: str # 1-31, к, пн, вт, ср, чт, пт, сб, вс
    hour: int
    minute: int
    text: str
    lastSentDate: SentDate = None

@dataclass_json
@dataclass
class UserInfo:
    user_id: int
    notifies: dict[str, Notify] # uuid, Notify

@dataclass
class UserCommandContext:
    user_id: int
    notify_id: str
    waitCommand: str
