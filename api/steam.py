import dataclasses
from datetime import datetime

import requests
from bs4 import BeautifulSoup


@dataclasses.dataclass
class GroupInfo:
    url: str
    name: str
    founded: datetime
    tag: str = None


def parse_group_tag_and_date(group_id: int | str) -> tuple[str, datetime]:
    response = requests.get(f"https://steamcommunity.com/gid/{group_id}")
    soup = BeautifulSoup(response.text, features="html.parser")

    group_tag = soup.find("span", {"class": "grouppage_header_abbrev"}).text
    founded = soup.find("div", {"class": "data"}).text.replace(",", "")
    founded = datetime.strptime(founded, "%d %B %Y")

    return str(group_tag), founded


def get_group_info(url: str) -> GroupInfo:
    response = requests.get(url + "/memberslistxml/?xml=1")

    if not response.ok:
        raise requests.RequestException

    soup = BeautifulSoup(response.text, features="html.parser")

    group_id = soup.find("groupid64").text

    tag, founded = parse_group_tag_and_date(group_id)
    name = soup.find("groupname").text
    url = soup.find("groupurl").text

    return GroupInfo(
        url=url,
        name=name,
        tag=tag,
        founded=founded,
    )
