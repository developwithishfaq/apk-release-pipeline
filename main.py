from fastapi import FastAPI,HTTPException,WebSocket,BackgroundTasks,Query
from pydantic import BaseModel
import subprocess
import docker
import os
import threading
from typing import List,Dict,Optional

app = FastAPI()

all_logs : Dict[str,str] = {} 

client = docker.from_env()


class CreateBuildRequest(BaseModel):
    jksName: str
    repoLink: str
    branchName : Optional[str] = None
    accessToken : Optional[str] = None
    bitbuckerUserName : Optional[str] = None
    bitbuckerAppPassword : Optional[str] = None
    bitbuckerOAuthToken : Optional[str] = None

@app.post("/run")
async def runContainer(background_tasks: BackgroundTasks,model: CreateBuildRequest):
    projectName = getProjectName(model.repoLink)
    all_logs[projectName] = ""
    jksModel : JksModel = getJksModelByName(model.jksName)

    host_volume_path = os.path.join(os.getcwd(), f"Apks/{projectName}")
    container_volume_path = "/data/apks"
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
                "BITBUCKET_OAUTH_TOKEN" : model.bitbuckerOAuthToken
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
        threading.Thread(target=consume_logs, args=(container_id,projectName), daemon=True).start()
        return {
            "message" : "container started succefully",
            "id" : container.id
        }
    except Exception as e:
        return {
            "error" : str(e)
        }
    

def consume_logs(container_id: str,projectName: str):
    try:
        container = client.containers.get(container_id)
        for log_line in container.logs(stream=True):
            # Process each log line (e.g., save to a database, print, etc.)
            logLine = log_line.decode("utf-8")
            all_logs[projectName] +=logLine
            # print(f"{logLine}")
    finally:
        # Optionally clean up the container
        container.remove(force=True)
    
@app.get("/logs")
def getLogs(projectName: str = Query()):
    if projectName in all_logs:
        logs = all_logs[projectName]
        return {
            "project":projectName,
            "logs": logs
        }
    else:
        return {
            "project":projectName,
            "logs": "No Project Found"
        }



class JksModel(BaseModel):
    path: str
    storePass: str
    keyAlias: str
    keyPass: str


def getJksModelByName(name: str):
    list : List[JksModel] = getJksList()
    for item in list:
        if item.path==name:
            return item

def getJksList()-> List[JksModel]:
    return [
        JksModel(
            path="ishfaq.jks",
            keyAlias="ishfaq",
            keyPass="ishfaq",
            storePass="ishfaq"
        )
    ]
    

def getProjectName(github_url:str):
    parts = github_url.split("/")
    return parts[len(parts)-1]