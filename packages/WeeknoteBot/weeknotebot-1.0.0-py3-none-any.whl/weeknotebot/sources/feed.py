import datetime

import feedparser


def generate_feed_text(title: str, link: str, today: datetime) -> str:
    flag = False
    output = f"""\n## {title}\n"""
    for element_link in feedparser.parse(link).entries:
        if (
            today.date() - datetime.timedelta(days=6)
            < datetime.datetime(*element_link.published_parsed[:6]).date()
        ):
            flag = True
            output += f"- [{element_link.title}]({element_link.link})\n"

    if flag:
        return output
    else:
        return ""
