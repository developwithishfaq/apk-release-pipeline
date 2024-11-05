from fastapi import APIRouter, File, UploadFile, Query, HTTPException
from models.models import JksModel
import os
import json

app = APIRouter()
BASE_DIR = "data/keys"  # Set your base directory path
JKS_DATA_FILE = os.path.join("General", "jks_data_list.txt")

# Helper function to read entries from file
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

# CREATE - Upload JKS file and add entry
@app.post("/uploadJks")
async def upload_file(
    file: UploadFile = File(...),
    keyAlias: str = Query(),
    keyPass: str = Query(),
    storePass: str = Query()
):
    os.makedirs(BASE_DIR, exist_ok=True)
    file_path = os.path.join(BASE_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    jks_data = JksModel(
        path=file.filename,
        keyAlias=keyAlias,
        keyPass=keyPass,
        storePass=storePass
    )

    entries = read_all_jks_entries()
    entries.append(jks_data.dict())
    save_all_jks_entries(entries)

    return {"message": f"File '{file.filename}' saved successfully."}

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