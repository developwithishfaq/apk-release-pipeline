from typing import List,Dict,Optional


all_logs : Dict[str,str] = {} 


def addLog(key:str,value:str):
    all_logs[key] = value
