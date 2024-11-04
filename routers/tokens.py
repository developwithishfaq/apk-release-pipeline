from fastapi import APIRouter, HTTPException
import json
import os

app = APIRouter()
FILE_PATH = "General/key_value_store.txt"

def load_data():
    # Load data from file if it exists, else return an empty dictionary
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    # Save the dictionary to a file
    with open(FILE_PATH, 'w') as f:
        json.dump(data, f)

@app.post("/saveKey")
def save_key_value(key: str, value: str):
    data = load_data()
    
    # Save or update the key-value pair
    data[key] = value
    save_data(data)
    
    return {"message": "Key-value pair saved successfully", "data": {key: value}}

@app.delete("/deleteKey")
def delete_key(key: str):
    data = load_data()
    
    if key not in data:
        raise HTTPException(status_code=404, detail="Key not found")
    
    # Delete the key
    del data[key]
    save_data(data)
    
    return {"message": f"Key '{key}' deleted successfully"}

@app.get("/getKey")
def get_value(key: str):
    data = load_data()
    
    if key not in data:
        raise HTTPException(status_code=404, detail="Key not found")
    
    return {"key": key, "value": data[key]}

@app.get("/getAllKeys")
def get_all_keys():
    data = load_data()
    
    # Convert the dictionary to a list of dictionaries in the required format
    all_keys = [{"key": k, "value": v} for k, v in data.items()]
    
    return all_keys
