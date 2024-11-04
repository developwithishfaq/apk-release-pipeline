from typing import List,Dict,Optional
from pydantic import BaseModel

class CreateBuildRequest(BaseModel):
    jksName: str
    repoLink: str
    branchName : Optional[str] = None
    accessToken : Optional[str] = None
    bitbuckerUserName : Optional[str] = None
    bitbuckerAppPassword : Optional[str] = None
    keyForBitBucketToken : Optional[str] = None



class JksModel(BaseModel):
    path: str
    storePass: str
    keyAlias: str
    keyPass: str


class ContainerModel(BaseModel):
    projectName: str
    containerId: str
    startTime: str
