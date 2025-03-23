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

"""Main logic to generate heatmap."""

import argparse
import calendar
import datetime
import logging
import multiprocessing
import os
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Generate matplotlib graphs without an X server.
# See http://stackoverflow.com/a/4935945
mpl.use("agg")

# Suppress logging from matplotlib in debug mode.
logging.getLogger("matplotlib").propagate = False
logger = multiprocessing.get_logger()


def run(config: argparse.Namespace) -> None:
    """Run the main flow.

    Args:
        config (argparse.Namespace): Config from command line arguments.

    Returns:
        None
    """
    logger.debug(config)
    logger.debug("Number of CPU: %d", multiprocessing.cpu_count())

    _refresh_output_dir(config)

    dataframe = _massage_data(config)
    args = [
        (*seq_cmap, config, dataframe)
        for seq_cmap in enumerate(config.cmap, 1)
    ]

    # Fork, instead of spawn process (child) inherit parent logger config.
    # See https://stackoverflow.com/q/14643568
    with multiprocessing.get_context("fork").Pool() as pool:
        pool.starmap(_generate_heatmap, args)


def _massage_data(config: argparse.Namespace) -> pd.DataFrame:
    """Filter the data from CSV file.

    Args:
        config (argparse.Namespace): Config from command line arguments.

    Returns:
        dataframe (pd.DataFrame): Filtered DataFrame.
    """
    try:
        dataframe = pd.read_csv(
            config.input_filename, header=None, names=["date", "count"]
        )
    except pd.errors.EmptyDataError:
        raise ValueError(
            f"The input CSV file {config.input_filename} is empty."
        )
    except pd.errors.ParserError:
        raise ValueError(
            f"The input CSV file {config.input_filename} has parsing errors."
        )

    if "date" not in dataframe.columns or "count" not in dataframe.columns:
        raise ValueError(
            "The input CSV file must contain 'date' and 'count' columns."
        )

    try:
        dataframe["date"] = pd.to_datetime(dataframe["date"])
    except ValueError:
        raise ValueError(
            "The 'date' column in the input CSV file has an invalid format. "
            "Please use a format that can be parsed by pandas to_datetime."
        )

    dataframe["weekday"] = dataframe["date"].dt.weekday + 1
    dataframe["year"] = dataframe["date"].dt.isocalendar().year
    dataframe["week"] = (
        dataframe["date"].dt.isocalendar().week.astype(str).str.zfill(2)
    )

    try:
        dataframe["count"] = pd.to_numeric(dataframe["count"])
    except ValueError:
        msg = (
            "The 'count' column in the input CSV file "
            "contains non-numeric values."
        )
        raise ValueError(msg)

    dataframe["count"] = dataframe["count"].apply(_truncate_rounded_count)

    if config.end_date:
        steps = dataframe[
            (dataframe["year"] == config.year)
            & (dataframe["date"] <= config.end_date)
        ]
    elif config.week >= 52:
        steps = dataframe[dataframe["date"].dt.year == config.year]
    else:
        steps = dataframe[
            (dataframe["year"] == config.year)
            & (dataframe["week"] <= str(config.week).zfill(2))
        ]

    duplicate_dates = dataframe[dataframe["date"].duplicated(keep=False)]
    if len(duplicate_dates):
        raise ValueError(f"Duplicate dates: {duplicate_dates} found!")

    if steps.empty:
        raise ValueError("No data extracted from CSV file!")

    logger.debug(
        "Last date: %s of current week: %s",
        max(steps["date"]).date(),
        config.week,
    )

    first_day_of_year = pd.to_datetime(f"{config.year}-01-01")
    pre_missing_steps = pd.DataFrame(
        {
            "date": pd.date_range(
                start=first_day_of_year,
                end=pd.to_datetime(min(steps["date"])) - datetime.timedelta(days=1),
            )
        }
    )
    pre_missing_steps["weekday"] = pre_missing_steps["date"].dt.weekday + 1
    pre_missing_steps["week"] = (
        pre_missing_steps["date"]
        .dt.isocalendar()
        .week.astype(str)
        .str.zfill(2)
    )
    pre_missing_steps["count"] = 0

    post_missing_steps = pd.DataFrame(
        {
            "date": pd.date_range(
                start=pd.to_datetime(max(steps["date"])) + datetime.timedelta(days=1),
                end=pd.to_datetime(f"{config.year}-12-31"),
            )
        }
    )
    post_missing_steps["weekday"] = post_missing_steps["date"].dt.weekday + 1
    post_missing_steps["week"] = (
        post_missing_steps["date"]
        .dt.isocalendar()
        .week.astype(str)
        .str.zfill(2)
    )
    post_missing_steps["count"] = 0

    if not pre_missing_steps.empty:
        steps = pd.concat([pre_missing_steps, steps], ignore_index=True)

    if not post_missing_steps.empty:
        steps = pd.concat([steps, post_missing_steps], ignore_index=True)

    steps.reset_index(drop=True, inplace=True)

    year_dataframe = steps.pivot_table(
        values="count", index=["weekday"], columns=["week"], fill_value=0
    )
    return year_dataframe


def _truncate_rounded_count(count: float) -> int:
    """Truncate and round count values to fit them in heatmap box.

    Args:
        count (int/float): The original count value.

    Returns:
        int: Truncated count value (divided by 100).
    """
    return int(round(count, -2) / 100)


def _generate_heatmap(
    seq: int,
    cmap: str,
    config: argparse.Namespace,
    dataframe: pd.core.frame.DataFrame,
) -> None:
    """Generate a heatmap.

    Args:
        seq (int): Sequence number for generated heatmap image file.
        cmap (str): Colormap name used for the heatmap.
        config (argparse.Namespace): Config from command line arguments.
        dataframe (pd.core.frame.DataFrame): DataFrame with data loaded from
        CSV file.

    Returns:
        None
    """
    _, axis = plt.subplots(figsize=(8, 5))
    axis.tick_params(axis="both", which="major", labelsize=9)
    axis.tick_params(axis="both", which="minor", labelsize=9)

    cbar_options = {
        "orientation": "horizontal",
        "label": (
            "Generated by: pypi.org/project/heatmap_cli, " f"colormap: {cmap}"
        ),
        "pad": 0.10,
        "aspect": 60,
        "extend": "max",
    }
    options = {
        "ax": axis,
        "fmt": "",
        "square": True,
        "cmap": cmap,
        "cbar": config.cbar,
        "cbar_kws": cbar_options,
    }

    if config.cmap_min:
        options.update({"vmin": config.cmap_min})

    if config.cmap_max:
        options.update({"vmax": config.cmap_max})

    if config.annotate:
        cbar_options.update(
            {
                "label": f"{cbar_options['label']}, count: by hundred",
            }
        )
        options.update(
            {
                "annot": True,
                "annot_kws": {"fontsize": 8},
                "linewidth": 0,
            }
        )

    # Convert value larger than 100 to >1.
    res = sns.heatmap(dataframe, **options)
    for text in res.texts:
        count = int(float(text.get_text()))
        if count >= 100:
            text.set_text(">" + str(count)[0])
        else:
            text.set_text(count)

    img_filename = (
        Path.cwd() / config.output_dir / _generate_filename(config, seq, cmap)
    )
    img_filename.parent.mkdir(parents=True, exist_ok=True)

    axis.set_title(_generate_title(config), fontsize=11, loc="left")
    axis.set_title("kianmeng.org", fontsize=11, loc="right")
    plt.tight_layout()
    plt.savefig(
        img_filename,
        bbox_inches="tight",
        transparent=False,
        dpi=76,
        format=config.format,
    )
    logger.info("Generate heatmap: %s", img_filename)

    if config.open:
        _open_heatmap(img_filename)


def _open_heatmap(filename: Path) -> None:
    """Open generated heatmap using the default program.

    Args:
        filename (str): The filename of the heatmap to open.

    Returns:
        None
    """
    if sys.platform == "linux":
        subprocess.call(["xdg-open", filename])
    elif sys.platform == "darwin":
        subprocess.call(["open", filename])
    elif sys.platform == "win32":
        os.startfile(filename)
    else:
        logger.warning(
            "Unsupported platform for opening files: %s", sys.platform
        )

    logger.info("Open heatmap: %s using default program.", filename.resolve())


def _generate_filename(config: argparse.Namespace, seq: int, cmap: str) -> str:
    """Generate an image filename.

    Args:
        config (argparse.Namespace): Config from command line arguments.
        seq (int): Sequence number for generated heatmap image file.
        cmap (str): Colormap name used for the heatmap.

    Returns:
        str: A generated file name for the PNG image.
    """
    annotated = ""
    if config.annotate:
        annotated = "_annotated"

    filename = (
        f"{annotated}_heatmap_of_total_daily_walked_steps_count"
        f".{config.format}"
    )
    if config.week >= 52:
        return f"{seq:03}_{config.year}_{cmap}" + filename

    return f"{seq:03}_{config.year}_week_{config.week}_{cmap}" + filename


def _generate_title(config: argparse.Namespace) -> str:
    """Generate a title for the heatmap.

    Args:
        config (argparse.Namespace): Config from command line arguments.

    Returns:
        str: A generated title for the heatmap.
    """
    if not config.title:
        title = f"Year {config.year}: Total Daily Walking Steps"
        last_week = 53 if calendar.isleap(config.year) else 52
        if config.week != last_week:
            title += f" Through Week {config.week:02d}"
    else:
        title = config.title

    logger.debug(title)
    return title


def _refresh_output_dir(config: argparse.Namespace) -> None:
    """Delete and recreate the output folder.

    Args:
        config (argparse.Namespace): Config from command line arguments.

    Returns:
        None
    """
    output_dir = _get_output_dir(config)

    if not config.purge or not output_dir.exists():
        return

    prompt = (
        f"Are you sure to purge output folder: {output_dir.absolute()}? [y/N] "
    )
    if config.yes or input(prompt).lower() == "y":
        logger.info("Purge output folder: %s", output_dir.absolute())
        try:
            shutil.rmtree(output_dir)
        except OSError as e:
            logger.error("Error removing directory: %s - %s.", output_dir, e)
            return
        logger.info("Create output folder: %s", output_dir.absolute())
        output_dir.mkdir(parents=True, exist_ok=True)


def _get_output_dir(config: argparse.Namespace) -> Path:
    """Get the current working directory.

    Args:
        config (argparse.Namespace): Config from command line arguments.

    Returns:
        str: The output directory path.
    """
    output_dir = Path(config.output_dir)
    if output_dir.is_absolute():
        return output_dir

    return Path.cwd() / config.output_dir
