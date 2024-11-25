class Task:
    def __init__(self, file_id: int, filename: str) -> None:
        self.file_id = file_id
        self.filename = filename
        self.progress = 0.0

    def __repr__(self) -> str:
        return f"file id: {self.file_id}; filename: {self.filename}; progress: {self.progress}"


class TaskManager:
    tasks = dict()

    @classmethod
    def add_task(cls, task: Task):
        cls.tasks[task.file_id] = task

    @classmethod
    def get_task(cls, file_id: str) -> Task:
        return cls.tasks.get(file_id)

    @classmethod
    def update_progress(cls, file_id: str, progress: float):
        if file_id in cls.tasks:
            cls.tasks[file_id].progress = progress

    @classmethod
    def complete_task(cls, file_id: str):
        if file_id in cls.tasks:
            return cls.tasks.pop(file_id)
