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
        "-c",
        "--config-dir",
        dest="config_dir",
        metavar="Config Directory",
        type=str,
        default=None,
        help="Set the path to the config directory.",
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
        "--google-calendar-name",
        "-n",
        dest="google_calendar_name",
        metavar="Google Calendar Name",
        type=str,
        default="luigi's mansion",
        help=f"Set specify part-or-all of the calendar name to use for updating. (Default: luigi's mansion)",
    )
    return parser.parse_args()


def main():
    # Argument config
    args = parse_args()
    basicConfig(level=args.log_level)

    # Setup the event coordinator
    ec = EventCoordinator(
        speedgaming_url=args.speedgaming_url,
        google_calendar_name=args.google_calendar_name,
    )

    # Do stuff
    gc_events = ec.gc_get_all_events()
    for e in gc_events:
        import ipdb; ipdb.set_trace()


if __name__ == "__main__":
    main()
