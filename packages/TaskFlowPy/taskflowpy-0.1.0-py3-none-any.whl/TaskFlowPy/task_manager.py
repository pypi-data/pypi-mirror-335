import json
import os


class TaskManager:
    """
    Classe para gerenciar tarefas e armazená-las em um arquivo JSON.
    """
    def __init__(self, storage_file="tasks.json"):
        self.storage_file = storage_file
        self.tasks = self.load_tasks()

    def load_tasks(self):
        """Carrega as tarefas do arquivo JSON."""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def save_tasks(self):
        """Salva as tarefas no arquivo JSON."""
        with open(self.storage_file, "w", encoding="utf-8") as file:
            json.dump(self.tasks, file, indent=4)

    def add_task(self, title, description=""):
        """Adiciona uma nova tarefa."""
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "description": description,
            "completed": False
        }
        self.tasks.append(task)
        self.save_tasks()
        return task

    def list_tasks(self):
        """Lista todas as tarefas."""
        return self.tasks

    def remove_task(self, task_id):
        """Remove uma tarefa pelo ID."""
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.save_tasks()

    def complete_task(self, task_id):
        """Marca uma tarefa como concluída."""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                self.save_tasks()
                return task
        return None
