from . import APP_NAME, APP_DESCRIPTION, SPEEDGAMING_URL
from .event_coordinator import EventCoordinator

from logging import basicConfig, getLogger, INFO, WARN, DEBUG
from os import getenv
from argparse import ArgumentParser


LOG = getLogger(__name__)


def parse_args():
    parser = ArgumentParser(prog=APP_NAME, description=APP_DESCRIPTION)

    parser.add_argument(
        "-v",
        "--verbose",
        dest="log_level",
        action="store_const",
        const=WARN,
        help="Set logging to WARN.",
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="log_level",
        action="store_const",
        const=DEBUG,
        help="Set logging to DEBUG.",
    )
    parser.add_argument(
        "-l",
        "--local-index",
        dest="local_index",
        metavar="Local Index File",
        type=str,
        default=None,
        help="Set a local index page to read from for SG Events instead of the live SG URL.",
    )
    parser.add_argument(
        "--speedgaming-url",
        "-s",
        dest="speedgaming_url",
        metavar="Speedgaming URL",
        type=str,
        default=SPEEDGAMING_URL,
        help="Set the URL to vist for grabbing a tournament schedule."
        f" (Default: {SPEEDGAMING_URL})",
    )
    parser.add_argument(
        "--google-calendar-id",
        "-g",
        dest="google_calendar_id",
        metavar="Google Calendar ID",
        type=str,
        required=True,
        help=f"Set the ID of the Google Calendar to update and manage.)",
    )
    return parser.parse_args()


def main():
    # Argument config
    args = parse_args()
    basicConfig(level=args.log_level)

    # Setup the event coordinator
    ec = EventCoordinator(
        speedgaming_url=args.speedgaming_url, google_calendar_id=args.google_calendar_id
    )

    # Do stuff
    events = ec.sg_get_events(index_path=args.local_index)
    for e in events:
        print(e)


if __name__ == "__main__":
    main()
