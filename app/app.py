import os
import shutil
from random import shuffle
from typing import Annotated
import uuid
import asyncio
from contextlib import asynccontextmanager

from uvicorn import run as run_asgi
from fastapi import (
    FastAPI,
    UploadFile,
    BackgroundTasks,
    File,
    status,
    HTTPException,
    Depends,
    Request,
)

from utils import Task, TaskManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.task_manager = TaskManager()
    yield


app = FastAPI(lifespan=lifespan)
FILES_FOLDER = "./files_data"

os.makedirs(FILES_FOLDER, exist_ok=True)


async def file_analyse(
    file_id: str,
    filename: str,
    filecontent: Annotated[bytes, File()],
    task_manager: TaskManager,
):
    finished_file_path = os.path.join(FILES_FOLDER)
    total_length = len(filecontent)
    chunk_size = total_length // 10
    processed_length = 0

    task = Task(file_id=file_id, filename=filename)
    task_manager.add_task(task)

    with open(f"{finished_file_path}/{file_id}_{filename}", "ab") as file:
        for i in range(0, total_length, chunk_size):
            chunk = filecontent[i : i + chunk_size]

            if "banned_word".encode() in chunk:
                file.write("banned".encode())
            else:
                file.write(chunk.upper())

            processed_length += len(chunk)
            progress = (processed_length / total_length) * 100
            task_manager.update_progress(file_id, progress)
            print(f"File id: {file_id}, progress: {progress}")
            await asyncio.sleep(1)

    task_manager.complete_task(file_id)


@app.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_files(
    background_tasks: BackgroundTasks, request: Request, file: UploadFile = File(...)
):
    if not file.filename.endswith((".json", ".txt")):
        raise HTTPException(status_code=400, detail="Only .txt and .json are supported")

    file_id = str(uuid.uuid4())
    background_tasks.add_task(
        file_analyse,
        file_id=file_id,
        task_manager=request.app.state.task_manager,
        filename=file.filename,
        filecontent=file.file.read(),
    )
    return {"message": f"Файл {file.filename} завантажується та обробляється у фоні"}


@app.get("/file_status/{file_id}")
async def get_file_status(file_id, request: Request):
    task_manager = request.app.state.task_manager
    task = task_manager.get_task(file_id)

    if not task:
        for file in os.listdir(FILES_FOLDER):
            if file.startswith(file_id):
                return {"status": "File completed", "filename": file}
        return {"status": "File not found"}

    return task.__repr__()


if __name__ == "__main__":
    run_asgi(app=app)
