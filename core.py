from models.models import JksModel
from typing import List,Dict,Optional
from routers import resources
from datetime import datetime


def getJksModelByName(name: str):
    list : List[JksModel] = resources.getJksList()
    for item in list:
        if item.path==name:
            return item


def getProjectName(github_url:str):
    parts = github_url.split("/")
    return parts[len(parts)-1]


def getGoodTime(time=None):
    if time is None:
        time = datetime.now().timestamp()  # Default to current time
    creation_time = datetime.fromtimestamp(time).strftime("%b %d, %I:%M %p")
    return creation_time