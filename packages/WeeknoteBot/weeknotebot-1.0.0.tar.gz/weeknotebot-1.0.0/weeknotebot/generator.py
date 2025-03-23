import datetime
import logging
import os
from pathlib import Path

from rich.logging import RichHandler

from weeknotebot.sources.feed import generate_feed_text
from weeknotebot.sources.fix_links import generate_fix_text
from weeknotebot.sources.goodreads_shelf import get_books_from_shelf

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


FORMAT = "%(message)s"
logging.basicConfig(
    level=LOG_LEVEL, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


WEEKNOTE_TEMPLATE = """---
title: "Week Note Nº {week}/{year}"
date: "{today_str}"
lastmod: "{today_str}"
draft: true
tags: ["{tag}"]
type : "{type}"
summary: "Random notes for week {week} of {year}"
---

"""


def get_data_meta(today) -> tuple[str, str, str]:
    year = today.strftime("%Y")
    week = today.strftime("%W")
    today_str = today.strftime("%Y-%m-%d")
    return year, week, today_str


def generate_weeknote(config: dict, today: datetime) -> tuple[str, str]:
    year, week, today_str = get_data_meta(today)
    weeknote = WEEKNOTE_TEMPLATE.format(
        week=week,
        year=year,
        today_str=today_str,
        tag=config["generator"]["tag"],
        type=config["generator"]["type_weeknote"],
    )
    file_name = f"{year}/{week}.md"
    log.debug(file_name)
    log.debug(weeknote)
    return weeknote, file_name


def write_weeknote(config: dict, today: datetime) -> None:
    weeknote, filename = generate_weeknote(config, today)

    for data in config["feeds"]:
        weeknote += generate_feed_text(
            title=data["title"], link=data["url"], today=today
        )

    weeknote += generate_fix_text(
        links=config["fix_links"],
        fix_link_label=config["generator"]["fix_links_label"],
    )

    if "goodread" in config:
        weeknote += get_books_from_shelf(
            user_id=config["goodread"]["user_id"],
            shelf_name_code=config["goodread"]["shelf_name_code"],
            shelf_name_label=config["goodread"]["shelf_name_label"],
        )

    output = os.path.join(config["generator"]["output"], filename)

    output_file = Path(output)
    output_file.parent.mkdir(exist_ok=True, parents=True)

    with open(output_file, "w") as f:
        f.write(weeknote)
