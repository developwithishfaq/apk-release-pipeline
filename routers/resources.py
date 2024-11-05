from models.models import JksModel
from typing import List,Optional
from fastapi import APIRouter,Request,Query,WebSocket,WebSocketDisconnect
from pathlib import Path
from fastapi.responses import FileResponse,PlainTextResponse,JSONResponse
import core
from helpers import logging
from typing import List,Dict
from datetime import datetime


router = APIRouter()


@router.get("/download/{file_path:path}")
def download_file(file_path: str):
    file = Path("Apks") / file_path
    if file.exists():
        return FileResponse(file)
    return {"error": "Mazrat file kisi nay shayd delete kar dia"}


@router.get("/jksList")
def getJsksApi():
    return getJksList()

def getJksList()-> List[JksModel]:
    return [
        JksModel(
            path="ishfaq.jks",
            keyAlias="ishfaq",
            keyPass="ishfaq",
            storePass="ishfaq"
        )
    ]



@router.get("/results")
def list_files(request: Request,projectName:str=Query()):
    root_dir = Path("Apks")
    base_url = request.base_url  # Capture the base URL (e.g., "http://127.0.0.1:8000/")
    projects = []

    for project_dir in root_dir.iterdir():
        if project_dir.is_dir():
            resources = []
            for file in project_dir.glob("*"):
                if file.suffix in [".apk", ".aab"] or True:
                    creation_time = core.getGoodTime(file.stat().st_ctime)
                    resources.append({
                        "extension": file.suffix[1:],  # Get file extension without the dot
                        "downloadableLink": f"{base_url}download/{project_dir.name}/{file.name}",
                        "creationTime": creation_time  # Add the formatted creation time
                    })
            name = project_dir.name
            if projectName==name:
                projects.append({
                    "projectName": name,
                    "resources": resources
                })

    return projects

@router.get("/logs",response_class=PlainTextResponse)
def getLogs(projectName: str = Query()):
    # return "ok"
    if projectName in logging.all_logs:
        logs = logging.all_logs[projectName]
        return logs
    else:
        return JSONResponse({
            "project":projectName,
            "logs": "Abhi tak to aesay kisi project ka naam nhi suna menay"
        })
    