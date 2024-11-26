class Task:
    def __init__(self, file_id: str, filename: str) -> None:
        self.file_id = file_id
        self.filename = filename
        self.progress = 0.0

    def update_progress(self, progress: float):
        self.progress = progress

    def __repr__(self) -> str:
        return f"file id: {self.file_id}; filename: {self.filename}; progress: {self.progress}"


class TaskManager:
    def __init__(self):
        self.tasks = dict()

    def add_task(self, task: Task):
        self.tasks[task.file_id] = task

    def get_task(self, file_id: str) -> Task:
        return self.tasks.get(file_id)

    def update_progress(self, file_id: str, progress: float):
        if file_id in self.tasks:
            self.tasks[file_id].update_progress(progress)

    def complete_task(self, file_id: str):
        if file_id in self.tasks:
            return self.tasks.pop(file_id)
