import os
import shutil
from random import shuffle
from typing import Annotated
import uuid
import asyncio

from uvicorn import run as run_asgi
from fastapi import FastAPI, UploadFile, BackgroundTasks, File, status, HTTPException

from utils import Task, TaskManager


app = FastAPI()
FILES_FOLDER = "./files_data"

os.makedirs(FILES_FOLDER, exist_ok=True)


async def file_analyse(
    file_id: str, filename: str, filecontent: Annotated[bytes, File()]
):
    finished_file_path = os.path.join(FILES_FOLDER)
    total_length = len(filecontent)
    chunk_size = total_length // 10
    processed_length = 0

    task = Task(file_id=file_id, filename=filename)
    TaskManager.add_task(task)

    with open(f"{finished_file_path}/{file_id}_{filename}", "ab") as file:
        for i in range(0, total_length, chunk_size):
            chunk = filecontent[i : i + chunk_size]

            if "banned_word".encode() in chunk:
                file.write("banned".encode())
            else:
                file.write(chunk.upper())

            processed_length += len(chunk)
            progress = (processed_length / total_length) * 100
            TaskManager.update_progress(file_id, progress)
            print(f"File id: {file_id}, progress: {progress}")
            await asyncio.sleep(1)

    TaskManager.complete_task(file_id)


@app.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_files(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith((".json", ".txt")):
        raise HTTPException(status_code=400, detail="Only .txt and .json are supported")

    file_id = str(uuid.uuid4())
    background_tasks.add_task(
        file_analyse,
        file_id=file_id,
        filename=file.filename,
        filecontent=file.file.read(),
    )
    return {"message": f"Файл {file.filename} завантажується та обробляється у фоні"}


@app.get("/file_status/{file_id}")
async def get_file_status(file_id):
    task = TaskManager.get_task(file_id)

    if not task:
        for file in os.listdir(FILES_FOLDER):
            if file.startswith(file_id):
                return {"status": "File completed", "filename": file}
        return {"status": "File not found"}

    return task.__repr__()


if __name__ == "__main__":
    run_asgi(app=app)
