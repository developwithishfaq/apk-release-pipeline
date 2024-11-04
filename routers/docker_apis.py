from fastapi import FastAPI,BackgroundTasks,Query,Request,APIRouter,WebSocket
import core
from models.models import JksModel,CreateBuildRequest
from helpers import logging
import os
import threading
import docker
import asyncio
from helpers import logging
from typing import Dict
from datetime import datetime
from models.models import ContainerModel
from routers import tokens


client = docker.from_env()

router = APIRouter()

runningContainers : Dict[str,ContainerModel] = {}

@router.post("/run")
async def runContainer(request: Request,model: CreateBuildRequest):
    size = len(client.containers.list())
    if size>=5:
        return {
            "message": "Sorry Already itney container chal rehay hein",
            "data" : get_containers_info()
        }
    projectName = core.getProjectName(model.repoLink)
    logging.addLog(projectName,"")
    jksModel : JksModel = core.getJksModelByName(model.jksName)

    host_volume_path = os.path.join(os.getcwd(), f"Apks/{projectName}")
    container_volume_path = "/data/apks"
    
    value = tokens.get_value(model.keyForBitBucketToken)["value"]
    if value is None:
        authToken = model.keyForBitBucketToken
    else:
        authToken = value
    try:
        if 'bitbucket.org' in model.repoLink:
            imageName = "bitbucket"
            env = {
                "REPO_LINK" : model.repoLink,
                "JKS_NAME" : jksModel.path,
                "KEYSTORE_PASSWORD" : jksModel.storePass,
                "KEY_ALIAS" : jksModel.keyAlias,
                "KEY_PASSWORD" : jksModel.keyPass,
                "BRANCH_NAME" : model.branchName,
                "BITBUCKET_USERNAME": model.bitbuckerUserName,
                "BITBUCKET_APP_PASSWORD": model.bitbuckerAppPassword,
                "BITBUCKET_OAUTH_TOKEN" : authToken
            }
        else:
            imageName = "github"
            env = {
                "REPO_LINK" : model.repoLink,
                "JKS_NAME" : jksModel.path,
                "KEYSTORE_PASSWORD" : jksModel.storePass,
                "KEY_ALIAS" : jksModel.keyAlias,
                "KEY_PASSWORD" : jksModel.keyPass,
                "BRANCH_NAME" : model.branchName,
                "ACCESS_TOKEN" : model.accessToken
            }
        container = client.containers.run(
            image=imageName,
            name= projectName,
            detach= True,
            environment = env,
            volumes={
                host_volume_path: {
                    "bind": container_volume_path,
                    "mode": "rw"  # "rw" for read-write access; "ro" if you need it read-only
                }
            }
        )
        container_id = container.id
        runningContainers[projectName] = ContainerModel(
            containerId=container_id,
            projectName=projectName,
            startTime=core.getGoodTime(),
        )
        threading.Thread(target=consume_logs, args=(container_id,projectName), daemon=True).start()
        return {
            "paigham" : "container chal para, ab intezar karo ap bas",
            "hitForLogs" : f"{request.base_url}logs?projectName={projectName}",
            "id" : container.id
        }
    except Exception as e:
        return {
            "error" : str(e)
        }

@router.get("/containers")
def get_containers_info():
    client = docker.from_env()  # Connect to Docker client
    containers = client.containers.list(all=True)  # List all containers (including stopped, paused, etc.)
    
    container_info = []
    for container in containers:
        logs = container.logs(tail=8).decode('utf-8').strip().split('\n')  # Get last 8 logs
        start_time = container.attrs['State']['StartedAt']  # Get start time in ISO 8601
        status = container.status  # Get container status (running, exited, etc.)
        
        # Convert ISO 8601 to desired format if start time is available
        formatted_start_time = (
            datetime.fromisoformat(start_time[:-1]).strftime("%b %d, %I:%M %p") if start_time else "N/A"
        )
        
        container_info.append({
            "naam": container.name,
            "shanakht": container.id,
            "qadmon_k_nishan": logs,
            "shruwati_waqt": formatted_start_time,  # Use formatted time
            "haalat": status  # Add status of the container
        })
    
    return container_info

@router.get("/stopAndRemove")
def force_stop_container(container_id:str=Query()):
    client = docker.from_env()  # Connect to Docker client
    try:
        container = client.containers.get(container_id)  # Get the container by ID
        container.stop(timeout=0)  # Forcefully stop the container
        container.remove()
        return {
            "paigham" : f"Container {container.name} ko ap k kehnay pay band kar dia hy."
        }
    except docker.errors.NotFound:
        return {
            "paigham" : f"Mazrat k sath ye container mila hi nhi."
        }
    except Exception as e:
        return {
            "paigham" : f"Herat ki bat hy k koi masla aa reha hy "
        }
        



def consume_logs(container_id: str,projectName: str):
    try:
        container = client.containers.get(container_id)
        for log_line in container.logs(stream=True):
            logLine = log_line.decode("utf-8")
            newText =logging.all_logs[projectName]+logLine
            logging.all_logs[projectName] = newText
            
    finally:
        container.remove(force=True)


@router.websocket("/liveLogs/{project_name}")
async def websocket_endpoint(websocket: WebSocket, project_name: str):
    await websocket.accept()
    
    previous_logs = ""
    try:
        while True:
            latest_logs = logging.all_logs.get(project_name, "")
            if latest_logs != previous_logs:
                await websocket.send_text(latest_logs[len(previous_logs):])
                previous_logs = latest_logs
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()