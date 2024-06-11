from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta


def lists_are_eq(first: list, second: list) -> bool:
    return sorted(list(map(lambda x: x.lower(), first))) == sorted(
        list(map(lambda x: x.lower(), second))
    )


def strip_all(data: str) -> str:
    to_remove = ["\n", "\t", "\r", "\r\n", "\xa0"]
    ret = data
    for tr in to_remove:
        ret = ret.replace(tr, "")
    return ret


@dataclass
class Event:
    datetime: datetime
    stream: str
    commentators: [str]
    participants: [str]

    def __init__(
        self: Event,
        date_e: _Element = None,
        participants_e: _Element = [],
        stream_e: _Element = None,
        commentators_e: _Element = [],
        json_payload: dict = None,
    ):
        if json_payload is not None:
            self.datetime = datetime.fromisoformat(json_payload["start"]["dateTime"])
            if json_payload.get("location") is not None:
                self.stream = json_payload["location"]
            else:
                self.stream = ""
            self.participants = json_payload["summary"].split(" vs ")
            self.commentators = json_payload["description"].split(": ")[-1].split(", ")
        else:
            raw_date = strip_all(date_e.text)
            parsed = datetime.strptime(raw_date, "%a %b %d,%I:%M %p")
            self.datetime = datetime(
                datetime.now().year,
                parsed.month,
                parsed.day,
                parsed.hour,
                parsed.minute,
                tzinfo=timezone(timedelta(days=-1, seconds=72000)),
            )
            self.participants = strip_all(participants_e.text).split(" vs ")
            self.commentators = (
                tostring(commentators_e.getchildren()[0])
                .decode("utf-8")
                .split(">")[1]
                .split(", ")
            )
            self.stream = "" if stream_e is None else stream_e.attrib["href"]

    @staticmethod
    def is_updatable(first: Event, second: Event) -> bool:
        now = datetime.now(timezone.utc)
        return (first.datetime > now) and lists_are_eq(
            first.participants, second.participants
        )

    def __str__(self: Event) -> str:
        participants = " vs ".join(self.participants)
        commentators = ", ".join(self.commentators)
        return (
            f"[{self.datetime.strftime('%b %d, %H:%M %p')}]:"
            f" {participants}"
            f" (commentators: {commentators})"
            f" -> {self.stream}"
        )

    def __eq__(self: Event, other: Event) -> bool:
        return (
            self.datetime == other.datetime
            and lists_are_eq(self.participants, other.participants)
            and lists_are_eq(self.commentators, other.commentators)
            and self.stream == other.stream
        )

    def to_json(self: Event) -> dict:
        comentators = ", ".join(self.commentators)
        end_dt = self.datetime + timedelta(hours=1)
        return {
            "summary": " vs ".join(self.participants),
            "location": self.stream,
            "description": f"Commentary Panel: {comentators}",
            "start": {
                "dateTime": self.datetime.isoformat(),
                "timeZone": "Etc/GMT-4",
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "Etc/GMT-4",
            },
            "attendeesOmitted": True,
        }
