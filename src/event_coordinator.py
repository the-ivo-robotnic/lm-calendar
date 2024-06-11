from __future__ import annotations

from .event import Event
from . import SPEEDGAMING_URL, GOOGLE_API_SCOPES

from os import getenv
from lxml.etree import parse
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
        google_calendar_id: str,
        google_calendar_scpoes: list = GOOGLE_API_SCOPES,
    ):
        # User-provided parameters
        self.speedgaming_url = speedgaming_url
        self.google_calendar_id = google_calendar_id
        self.google_calendar_scpoes = google_calendar_scpoes

        # Build and authenticate google api client
        self.google_calendar_client = self.__build_gc_client()

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

    def gc_update_event(self: EventCoordinator, event_id: str, event: Event) -> None:
        LOG.debug(
            f"Updating Google Calendar Event for {event.participants} on {event.datetime.ctime()}"
        )
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

    def sg_get_events(self: EventCoordinator, index_path: str = None) -> [Event]:
        page = None

        # Fetch SG events
        if index_path is None:  # Fetch SG events from the web
            LOG.debug(f"Fetching SG results from the web -> {self.speedgaming_url}")
            req: HTTPResponse = urlopen(self.speedgaming_url)
            page = req.read().decode("utf-8").replace("\t", "").replace("\n", "")
        else:  # Fetch SG events from local index file
            LOG.debug(f"Fetching SG results from local file -> {index_path}")
            with open(index_path, "r") as file:
                page = file.read()

        # Parse the SG results
        root: _Element = parse(page)
        body: _Element = root.find("body")
        table: _Element = body.find("table")
        tbody: _Element = table.find("tbody")
        rows = tbody.findall("tr")[1:]

        # Serialize into Event objects
        events: [Event] = []
        for row in rows:
            children = row.getchildren()
            if len(children) < 4:
                LOG.warn(
                    f"Bad element detected, tossing line: {strip_all(tostring(row).decode('utf-8'))}"
                )
                continue

            date_e: _Element = children[0].find("span")
            participants_e: _Element = children[1]
            stream_e: _Element = children[2].find("a")
            commentators_e: _Element = children[3]
            events.append(Event(date_e, participants_e, stream_e, commentators_e))
        return events
