from __future__ import annotations

from .event import Event, strip_all, build_datetime
from . import SPEEDGAMING_URL, GOOGLE_API_SCOPES

from os import getenv
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen
from logging import Logger, getLogger
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow

LOG: Logger = getLogger(__name__)


class EventCoordinator:
    speedgaming_url: str = ""
    google_calendar_id: str = ""
    google_calendar_scpoes: [str] = []
    google_calendar_client: Resource = None

    def __init__(
        self: EventCoordinator,
        speedgaming_url: str,
        google_calendar_name: str = "luigi's mansion",
    ):
        # User-provided parameters
        self.speedgaming_url = speedgaming_url
        self.google_calendar_scpoes = GOOGLE_API_SCOPES

        # Build and authenticate google api client
        self.google_calendar_client = self.__build_gc_client()

        # Fetch the desired calendar ID
        self.google_calendar_id = self.gc_get_calendar_id(google_calendar_name)

    def __build_gc_client(
        self: EventCoordinator,
        token_path: str = "./token.json",
        client_path: str = "./client.json",
    ) -> Resource:
        creds = None

        # Load local token auth or fetch a new token via client secrets
        try:
            creds = Credentials.from_authorized_user_file(
                token_path, self.google_calendar_scpoes
            )
        except:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_path, self.google_calendar_scpoes
            )
            creds = flow.run_local_server(port=0)
            with open("token.json", "w+") as file:
                file.write(creds.to_json())

        # Build the calendar resource
        return build("calendar", "v3", credentials=creds)

    def gc_create_event(self: EventCoordinator, event: dict) -> None:
        try:
            res = (
                self.google_calendar_client.events()
                .insert(calendarId=self.google_calendar_id, body=event)
                .execute()
            )
            LOG.debug(res)
        except HttpError as e:
            LOG.error(e)

    def gc_update_event(self: EventCoordinator, event_id: str, event: Event) -> bool:
        try:
            res = (
                self.google_calendar_client.events()
                .update(
                    calendarId=self.google_calendar_id,
                    eventId=event_id,
                    body=event.to_json(),
                )
                .execute()
            )
            LOG.debug(res)
        except HttpError as e:
            LOG.error(e)

    def gc_delete_event(self: EventCoordinator, event_id: str) -> None:
        try:
            res = self.google_calendar_client.events().delete(
                calendarId=self.google_calendar_id, eventId=event_id
            )
            LOG.debug(res)
        except HttpError as e:
            LOG.error(e)

    def gc_get_all_calendars(self: EventCoordinator) -> [tuple]:
        calendars = []
        try:
            raw_calendars = self.google_calendar_client.calendarList().list().execute()
            raw_calendars = raw_calendars["items"]
            for cal in raw_calendars:
                calendars.append((cal["summary"], cal["id"]))
        except HttpError as e:
            LOG.error(e)
        finally:
            return calendars

    def gc_get_calendar_id(self: EventCoordinator, name: str) -> str:
        calendars = self.gc_get_all_calendars()
        for c in calendars:
            if name.lower() in c[0].lower():
                return c[1]
        return None

    def gc_get_all_events(self: EventCoordinator) -> [Event]:
        events = []
        raw_events = (
            self.google_calendar_client.events()
            .list(
                calendarId=self.google_calendar_id,
                timeZone=timezone.utc,
                pageToken=None,
            )
            .execute()
        )

        for e in raw_events.get("items"):
            start_time = e.get("start").get("dateTime")
            end_time = e.get("end").get("dateTime")
            stream_url = '' if e.get('location') is None else e.get("location")
            participants = e.get("summary").split(" vs ")
            commentators = e.get("description").split(': ')[-1].split(', ')
            event_id = e.get("id")

            events.append(
                Event(
                    start_time=start_time,
                    end_time=end_time,
                    stream_url=stream_url,
                    participants=participants,
                    commentators=commentators,
                    event_id=event_id,
                )
            )
            return events

    def sg_get_all_events(self: EventCoordinator, index_path: str = None) -> [Event]:
        events: list = []
        html_src = (
            urlopen(self.speedgaming_url)
            if (index_path is None)
            else open(index_path, "r")
        )
        soup = BeautifulSoup(html_src, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")[1:]  # Skip the header row

        # Serialize into Event objects
        for row in rows:
            columns = row.find_all("td")
            start_time: datetime = build_datetime(
                strip_all(columns[0].find("span").text)
            )
            end_time: datetime = start_time + timedelta(hours=1)
            raw_stream_url = columns[2].find("a")
            stream_url = "" if raw_stream_url is None else raw_stream_url.attrs["href"]
            participants = strip_all(columns[1].text).split(" vs ")
            commentators = strip_all(columns[3].text).split(", ")

            events.append(
                Event(
                    start_time=start_time,
                    end_time=end_time,
                    stream_url=stream_url,
                    participants=participants,
                    commentators=commentators,
                )
            )

        return events
