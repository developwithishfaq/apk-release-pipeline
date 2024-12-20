from fastapi import APIRouter, HTTPException
import json
import os
from helpers import security

app = APIRouter()
FILE_PATH = "General/key_value_store.txt"

def load_data():
    # Load data from file if it exists and is valid JSON; otherwise, return an empty dictionary
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {} 
    
    return {}

def save_data(data):
    directory = os.path.dirname(FILE_PATH)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)    
    with open(FILE_PATH, 'w') as f:
        json.dump(data, f)

@app.post("/saveKey")
def save_key_value(key: str, value: str):
    data = load_data()
    
    # Save or update the key-value pair
    data[key] = security.encrypt_string(value)
    print(f"Data to save:{data}")
    save_data(data)
    
    return {"message": "Key-value pair ko save kar dia gia hy.", "data": {key: value}}

@app.delete("/deleteKey")
def delete_key(key: str):
    data = load_data()
    
    if key not in data:
        raise HTTPException(status_code=404, detail="Key not found")
    
    # Delete the key
    del data[key]
    save_data(data)
    
    return {"message": f"Key '{key}' deleted successfully"}


def get_value(key: str):
    data = load_data()
    
    if key not in data:
        return key
    else:
        return security.decrypt_string(data[key])

@app.get("/getAllKeys")
def get_all_keys():
    data = load_data()
    
    # Convert the dictionary to a list of dictionaries in the required format
    all_keys = [{"key": k, "value": ""} for k, v in data.items()]
    
    return all_keys
