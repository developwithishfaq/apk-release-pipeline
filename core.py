from models.models import JksModel
from typing import List,Dict,Optional
from routers import resources,jks_crud
from datetime import datetime
from pathlib import Path
import os


def getJksModelByName(name: str):
    list : List[JksModel] = jks_crud.getJsksApi()
    for item in list:
        if item.path==name:
            return item
    return None


def getProjectName(github_url:str):
    parts = github_url.split("/")
    return parts[len(parts)-1]


def getGoodTime(time=None):
    if time is None:
        time = datetime.now().timestamp()  # Default to current time
    creation_time = datetime.fromtimestamp(time).strftime("%b %d, %I:%M %p")
    return creation_time

def get_creation_time(file_path):
    path = Path(file_path)
    if os.name == 'nt':  # Windows
        return path.stat().st_ctime  # Creation time
    else:
        return path.stat().st_mtime 
