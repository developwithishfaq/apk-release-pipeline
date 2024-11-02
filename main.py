from fastapi import FastAPI,HTTPException,WebSocket
from pydantic import BaseModel
import subprocess
import docker
import os

app = FastAPI()

client = docker.from_env()


class CreateBuildRequest(BaseModel):
    jksName: str
    repoLink: str


@app.post("/buildImage")
def buildImage():
    try:
        # Ensure the Dockerfile is in the current working directory
        if not os.path.exists('Dockerfile'):
            raise HTTPException(status_code=404, detail="Dockerfile not found")

        # Build the Docker image
        image, build_logs = client.images.build(path=".", tag="test")

        # Optionally, print build logs
        for log in build_logs:
            if 'stream' in log:
                print(log['stream'].strip())

        return {
            "message": f"Image built successfully.",
            "image_id": image.id
        }
    except docker.errors.BuildError as e:
        raise HTTPException(status_code=500, detail=f"Error building image: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run")
def runContainer(model: CreateBuildRequest):
    try:
        container = client.containers.run(
            "test",
            name= "Hathi",
            detach= True,
            environment= {
                "REPO_LINK" : model.repoLink,
            }
        )
        return {
            "message" : "container started succefully",
            "id" : container.id
        }
    except Exception as e:
        return {
            "error" : str(e)
        }

@app.websocket("/logs/{container_name}")
async def log_websocket(websocket: WebSocket, container_name: str):
    await websocket.accept()
    try:
        container = client.containers.get(container_name)
        logs_generator = container.logs(stream=True, follow=True)
        for log in logs_generator:
            await websocket.send_text(log.decode('utf-8').strip())
    except docker.errors.NotFound:
        await websocket.close(code=1003)  # Close with "not found" code
    except Exception as e:
        await websocket.close(code=1000)  # Close with normal code



class JksModel(BaseModel):
    path: str
    password: str
    key: str

def getKeysData():
    return list(
        JksModel(
            path="ishfaq.jks",
            password="",
            key=""
        )
    )
    