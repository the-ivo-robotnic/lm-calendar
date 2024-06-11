from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from urllib.parse import ParseResult


def lists_are_eq(first: list, second: list) -> bool:
    return sorted(list(map(lambda x: x.lower(), first))) == sorted(
        list(map(lambda x: x.lower(), second))
    )


def strip_all(data: str) -> str:
    rm_chars = ["\n", "\t", "\r", "\xa0", "&nbsp;"]
    data = data.strip()
    for c in rm_chars:
        data = data.replace(c, "")
    return data


def build_datetime(data: str) -> datetime:
    data = strip_all(data)
    parsed = datetime.strptime(data, "%a %b %d,%I:%M %p")
    return datetime(
        datetime.now().year,
        parsed.month,
        parsed.day,
        parsed.hour,
        parsed.minute,
        tzinfo=timezone(timedelta(days=-1, seconds=72000)),
    )


# if json_payload is not None:
#     self.datetime = datetime.fromisoformat(json_payload["start"]["dateTime"])
#     if json_payload.get("location") is not None:
#         self.stream = json_payload["location"]
#     else:
#         self.stream = ""
#     self.participants = json_payload["summary"].split(" vs ")
#     self.commentators = json_payload["description"].split(": ")[-1].split(", ")
# else:
#     raw_date = strip_all(date_e.text)
#     parsed = datetime.strptime(raw_date, "%a %b %d,%I:%M %p")
#     self.datetime = datetime(
#         datetime.now().year,
#         parsed.month,
#         parsed.day,
#         parsed.hour,
#         parsed.minute,
#         tzinfo=timezone(timedelta(days=-1, seconds=72000)),
#     )
#     self.participants = strip_all(participants_e.text).split(" vs ")
#     self.commentators = (
#         tostring(commentators_e.getchildren()[0])
#         .decode("utf-8")
#         .split(">")[1]
#         .split(", ")
#     )
#     self.stream = "" if stream_e is None else stream_e.attrib["href"]


@dataclass
class Event:
    start_time: datetime
    end_time: datetime
    stream_url: ParseResult
    participants: [str]
    commentators: [str]
    event_id: str

    def __init__(
        self: Event,
        start_time: datetime,
        end_time: datetime,
        stream_url: ParseResult,
        participants: [str],
        commentators: [str],
        event_id: str = None,
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.stream_url = stream_url
        self.participants = participants
        self.commentators = commentators
        self.event_id = event_id

    def is_a_pair(self: Event, data: Event) -> bool:
        now = datetime.now(timezone.utc)
        return (
            (self.start_time > now)
            and (data.start_time > now)
            and lists_are_eq(self.participants, data.participants)
        )

    def __str__(self: Event) -> str:
        participants = " vs ".join(self.participants)
        commentators = ", ".join(self.commentators)
        return (
            f"<{self.start_time.strftime('%b %d')}> "
            f"[{self.start_time.strftime('%H:%M %p')}]:"
            f" {participants}"
            f" (commentators: {commentators})"
            f" -> {self.stream_url}"
        )

    def __eq__(self: Event, other: Event) -> bool:
        return (
            self.start_time == other.start_time
            and self.end_time == other.end_time
            and self.stream_url == other.stream_url
            and lists_are_eq(self.participants, other.participants)
            and lists_are_eq(self.commentators, other.commentators)
        )

    def to_json(self: Event) -> dict:
        return {
            "summary": " vs ".join(self.participants),
            "location": self.stream_url,
            "description": f"Commentary Panel: {', '.join(self.commentators)}",
            "start": {
                "dateTime": self.start_time.isoformat(),
                "timeZone": self.start_time.tzname(),
            },
            "end": {
                "dateTime": self.end_time.isoformat(),
                "timeZone": self.end_time.tzname(),
            },
            "attendeesOmitted": True,
        }
