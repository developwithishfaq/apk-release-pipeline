from fastapi import FastAPI,HTTPException,WebSocket,BackgroundTasks,Query,Request
from pydantic import BaseModel
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List,Dict,Optional
from routers import docker_apis,resources,tokens


app = FastAPI()

app.include_router(resources.router)
app.include_router(docker_apis.router)
app.include_router(tokens.app)

