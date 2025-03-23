# Copyright (C) 2023,2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""A console program that generates a yearly calendar heatmap.

website: https://github.com/kianmeng/heatmap_cli
changelog: https://github.com/kianmeng/heatmap_cli/blob/master/CHANGELOG.md
issues: https://github.com/kianmeng/heatmap_cli/issues
"""

import argparse
import datetime
import logging
import multiprocessing
import sys
from itertools import zip_longest
from typing import Optional, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt

from heatmap_cli import (
    DemoAction,
    EnvironmentAction,
    __version__,
    setup_logging,
)
from heatmap_cli.heatmap import run as generate_heatmaps

IMAGE_FORMATS = [
    "eps",
    "jpeg",
    "jpg",
    "pdf",
    "pgf",
    "png",
    "ps",
    "raw",
    "rgba",
    "svg",
    "svgz",
    "tif",
    "tiff",
    "webp",
]

# Generate matplotlib graphs without an X server.
# See http://stackoverflow.com/a/4935945
mpl.use("Agg")

# Suppress logging from matplotlib in debug mode.
logging.getLogger("matplotlib").propagate = False
logger = multiprocessing.get_logger()

# Sort colormaps in a case-insensitive manner.
CMAPS = sorted(plt.colormaps, key=str.casefold)
DEFAULT_CMAP = "RdYlGn_r"


def build_parser(
    args: Optional[Sequence[str]] = None,
) -> argparse.ArgumentParser:
    """Parse the CLI arguments.

    Args:
        args (List | None): Argument passed through the command line.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="heatmap_cli",
        add_help=False,
        description=__doc__,
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(
            prog,
            max_help_position=6,
        ),
    )

    parser.add_argument(
        "--demo",
        const=len(CMAPS),
        action=DemoAction,
        type=int,
        dest="demo",
        help=(
            "generate number of heatmaps by colormaps "
            f"(default: '{len(CMAPS)}')"
        ),
        metavar="NUMBER_OF_COLORMAP",
    )

    parser.add_argument(
        "-y",
        "--year",
        dest="year",
        type=int,
        default=datetime.datetime.today().year,
        help="filter by year from the CSV file (default: '%(default)s')",
        metavar="YEAR",
    )

    parser.add_argument(
        "-w",
        "--week",
        dest="week",
        type=int,
        default=datetime.datetime.today().isocalendar().week,
        help=(
            "filter until week of the year from the CSV file "
            "(default: '%(default)s')"
        ),
        metavar="WEEK",
    )

    parser.add_argument(
        "-e",
        "--end-date",
        dest="end_date",
        default=None,
        help=(
            "filter until the date of the year from the CSV file and "
            "this will overwrite -y and -w option (default: %(default)s)"
        ),
        metavar="END_DATE",
    )

    parser.add_argument(
        "-O",
        "--output-dir",
        dest="output_dir",
        default="output",
        help="set default output folder (default: '%(default)s')",
    )

    parser.add_argument(
        "-o",
        "--open",
        default=False,
        action="store_true",
        dest="open",
        help=(
            "open the generated heatmap using the default program "
            "(default: %(default)s)"
        ),
    )

    parser.add_argument(
        "-p",
        "--purge",
        default=False,
        action="store_true",
        dest="purge",
        help=(
            "remove all leftover artifacts set by "
            "--output-dir folder (default: %(default)s)"
        ),
    )

    parser.add_argument(
        "-v",
        "--verbose",
        default=0,
        action="count",
        dest="verbose",
        help="show verbosity of debugging log. Use -vv, -vvv for more details",
    )

    config, _remainder_args = parser.parse_known_args(args)

    parser.add_argument(
        "input_filename",
        help="CSV filename",
        type=str,
        metavar="CSV_FILENAME",
        nargs="?" if config.demo else None,  # type: ignore
    )

    # Date will overwrite the year and week.
    if config.end_date:
        date = datetime.datetime.strptime(config.end_date, "%Y-%m-%d")
        (year, week, _day) = date.isocalendar()
        parser.set_defaults(year=year)
        parser.set_defaults(week=week)

    parser.add_argument(
        "-t",
        "--title",
        dest="title",
        default=False,
        help="set title for the heatmap (default: %(default)s)",
    )

    parser.add_argument(
        "-f",
        "--format",
        dest="format",
        choices=IMAGE_FORMATS,
        default="png",
        help="set the default image format (default: '%(default)s')",
        metavar="IMAGE_FORMAT",
    )

    parser.add_argument(
        "-c",
        "--cmap",
        choices=plt.colormaps,
        dest="cmap",
        default=[DEFAULT_CMAP],
        action="append",
        help=_generate_cmap_help(config),
        metavar="COLORMAP",
    )

    parser.add_argument(
        "-i",
        "--cmap-min",
        dest="cmap_min",
        default=False,
        help=(
            "Set the minimum value of the colormap range "
            "(default: %(default)s)"
        ),
        metavar="COLORMAP_MIN_VALUE",
    )

    parser.add_argument(
        "-x",
        "--cmap-max",
        dest="cmap_max",
        default=False,
        help=(
            "Set the maximum value of the colormap range "
            "(default: %(default)s)"
        ),
        metavar="COLORMAP_MAX_VALUE",
    )

    parser.add_argument(
        "-b",
        "--cbar",
        default=False,
        action="store_true",
        dest="cbar",
        help="show colorbar (default: %(default)s)",
    )

    parser.add_argument(
        "-a",
        "--annotate",
        default=True,
        action=argparse.BooleanOptionalAction,
        dest="annotate",
        help="add count to each heatmap region",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        default=False,
        action="store_true",
        dest="quiet",
        help="suppress all logging",
    )

    parser.add_argument(
        "-Y",
        "--yes",
        default=False,
        action="store_true",
        dest="yes",
        help="yes to prompt",
    )

    parser.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        dest="debug",
        help="show debugging log and stack trace",
    )

    parser.add_argument(
        "-E",
        "--env",
        action=EnvironmentAction,
        dest="env",
        help="print environment information for bug reporting",
    )

    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="show this help message and exit.",
    )

    return parser


def _generate_cmap_help(config: argparse.Namespace) -> str:
    """Generate the help text for colormap options.

    Args:
        config (argparse.Namespace): Config from parsed command line arguments.

    Returns:
        str: Formatted help text.
    """
    cmap_help = "Set default colormap."
    cmap_default = f" (default: '{DEFAULT_CMAP}')"
    if not config.verbose:
        return cmap_help + ", use -v to show all colormaps" + cmap_default

    items_per_row = 6
    cmap_choices = ""
    cmap_bygroups = zip_longest(*(iter(CMAPS),) * items_per_row)
    for cmap_bygroup in cmap_bygroups:
        cmap_choices += ", ".join(filter(None, cmap_bygroup)) + "\n"

    return cmap_help + cmap_default + "\n" + cmap_choices


def main(args: Optional[Sequence[str]] = None) -> None:
    """Run the main program flow.

    Args:
        args (List | None): Argument passed through the command line.

    Returns:
        None
    """
    args = args or sys.argv[1:]

    try:
        parser = build_parser(args)
        parsed_args = parser.parse_args(args)

        setup_logging(parsed_args)
        generate_heatmaps(parsed_args)
    except Exception as error:
        debug = "-d" in args or "--debug" in args
        message = getattr(error, "message", str(error))
        logger.error("Error: %s", message, exc_info=debug)

        raise SystemExit(1) from None
