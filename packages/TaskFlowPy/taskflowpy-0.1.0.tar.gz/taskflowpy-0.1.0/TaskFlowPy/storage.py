import json
import os
import sqlite3


class StorageManager:
    """
    Gerencia o armazenamento de tarefas em diferentes formatos: JSON e SQLite.
    """
    def __init__(self, storage_type="json", storage_file="tasks.json"):
        self.storage_type = storage_type
        self.storage_file = storage_file

        if self.storage_type == "sqlite":
            self._initialize_sqlite()

    def _initialize_sqlite(self):
        """Cria a tabela de tarefas no banco de dados SQLite."""
        with sqlite3.connect(self.storage_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    completed BOOLEAN DEFAULT 0
                )
            ''')
            conn.commit()

    def load_tasks(self):
        """Carrega as tarefas do armazenamento selecionado."""
        if self.storage_type == "json":
            return self._load_from_json()
        elif self.storage_type == "sqlite":
            return self._load_from_sqlite()
        return []

    def _load_from_json(self):
        """Carrega as tarefas de um arquivo JSON."""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def _load_from_sqlite(self):
        """Carrega as tarefas do banco de dados SQLite."""
        with sqlite3.connect(self.storage_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, description, completed FROM tasks") # noqa501
            tasks = cursor.fetchall()
            return [{"id": row[0], "title": row[1], "description": row[2], "completed": bool(row[3])} for row in tasks] # noqa501

    def save_task(self, task):
        """Salva uma nova tarefa no armazenamento selecionado."""
        if self.storage_type == "json":
            return self._save_to_json(task)
        elif self.storage_type == "sqlite":
            return self._save_to_sqlite(task)

    def _save_to_json(self, task):
        """Salva uma nova tarefa em um arquivo JSON."""
        tasks = self._load_from_json()
        tasks.append(task)
        with open(self.storage_file, "w", encoding="utf-8") as file:
            json.dump(tasks, file, indent=4)

    def _save_to_sqlite(self, task):
        """Salva uma nova tarefa no banco de dados SQLite."""
        with sqlite3.connect(self.storage_file) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)", # noqa501
                           (task["title"], task.get("description", ""), task["completed"])) # noqa501
            conn.commit()

    def delete_task(self, task_id):
        """Remove uma tarefa pelo ID."""
        if self.storage_type == "json":
            tasks = self._load_from_json()
            tasks = [task for task in tasks if task["id"] != task_id]
            with open(self.storage_file, "w", encoding="utf-8") as file:
                json.dump(tasks, file, indent=4)
        elif self.storage_type == "sqlite":
            with sqlite3.connect(self.storage_file) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
