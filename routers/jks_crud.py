from fastapi import APIRouter, File, UploadFile, Query, HTTPException
from models.models import JksModel
import os
from typing import List
import json

app = APIRouter()
BASE_DIR = "data/keys"  # Set your base directory path
JKS_DATA_FILE = os.path.join("General", "jks_data_list.txt")

# Helper function to read entries from file



def getJsksApi()-> List[JksModel]:
    jks = read_all_jks_entries()
    models : List[JksModel] = []
    for item in jks:
        model = JksModel(
            path=item.get("path"),
            keyAlias=item.get("keyAlias"),
            keyPass=item.get("keyPass"),
            storePass=item.get("storePass"),
        )
        models.append(model)
    return models
        
    

def read_all_jks_entries():
    if os.path.exists(JKS_DATA_FILE):
        with open(JKS_DATA_FILE, "r") as file:
            data = file.read()
            return json.loads(data) if data else []
    return []

# Helper function to save entries to file
def save_all_jks_entries(entries):
    with open(JKS_DATA_FILE, "w") as file:
        json.dump(entries, file, indent=4)

@app.post("/uploadJks")
async def upload_file(
    file: UploadFile = File(...),
    keyAlias: str = Query(),
    keyPass: str = Query(),
    storePass: str = Query()
):
    os.makedirs(BASE_DIR, exist_ok=True)
    file_path = os.path.join(BASE_DIR, file.filename)

    # Save the file only if it doesn't already exist
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(await file.read())
    else:
        return {"message": f"File '{file.filename}' already exists and was not uploaded again."}

    jks_data = JksModel(
        path=file.filename,
        keyAlias=keyAlias,
        keyPass=keyPass,
        storePass=storePass
    )

    # Load existing entries and check if the file already has an entry
    entries = read_all_jks_entries()
    if any(entry['path'] == file.filename for entry in entries):
        return {"message": f"Entry for '{file.filename}' already exists in the database."}

    # Add new entry if it's unique
    entries.append(jks_data.dict())
    save_all_jks_entries(entries)

    return {"message": f"File '{file.filename}' saved and entry added successfully."}

# READ ALL - Get all JKS entries
@app.get("/jks")
def get_all_jks():
    return read_all_jks_entries()

# READ BY PATH - Get a specific JKS entry by path
@app.get("/jks/{path}")
def get_jks_by_path(path: str):
    entries = read_all_jks_entries()
    entry = next((entry for entry in entries if entry["path"] == path), None)
    if entry is None:
        raise HTTPException(status_code=404, detail="JKS entry not found")
    return entry

# UPDATE - Update a JKS entry by path
@app.put("/jks/{path}")
def update_jks_by_path(
    path: str,
    keyAlias: str = Query(),
    keyPass: str = Query(),
    storePass: str = Query()
):
    entries = read_all_jks_entries()
    index = next((i for i, entry in enumerate(entries) if entry["path"] == path), None)

    if index is None:
        raise HTTPException(status_code=404, detail="JKS entry not found")

    entries[index] = JksModel(
        path=path,
        keyAlias=keyAlias,
        keyPass=keyPass,
        storePass=storePass
    ).dict()
    save_all_jks_entries(entries)

    return {"message": "JKS entry updated successfully."}

# DELETE - Delete a JKS entry by path
@app.delete("/jks/{path}")
def delete_jks_by_path(path: str):
    entries = read_all_jks_entries()
    entries = [entry for entry in entries if entry["path"] != path]

    save_all_jks_entries(entries)
    delJksFile(path)
    return {"message": "JKS entry deleted successfully."}

def delJksFile(name):
    try:
        file_path = f"data/keys/{name}"
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"Error deleting file: {e}")