import os
import unittest

from TaskFlowPy.storage import StorageManager
from TaskFlowPy.task_manager import TaskManager


class TestTaskManager(unittest.TestCase):
    """
    Testes unitários para o TaskManager com armazenamento JSON e SQLite.
    """
    def setUp(self):
        """Configuração inicial para os testes."""
        self.json_manager = TaskManager(storage_file="test_tasks.json")
        self.sqlite_manager = StorageManager(storage_type="sqlite", storage_file="test_tasks.db") # noqa501
        self.json_manager.tasks = []  # Resetar lista de tarefas
        self.json_manager.save_tasks()

    def test_add_task_json(self):
        """Testa se uma tarefa é adicionada corretamente no JSON."""
        task = self.json_manager.add_task("Tarefa de Teste", "Descrição de teste") # noqa501
        self.assertEqual(task["title"], "Tarefa de Teste")
        self.assertFalse(task["completed"])

    def test_list_tasks_json(self):
        """Testa se as tarefas são listadas corretamente no JSON."""
        self.json_manager.add_task("Nova Tarefa")
        tasks = self.json_manager.list_tasks()
        self.assertGreater(len(tasks), 0)

    def test_remove_task_json(self):
        """Testa se uma tarefa pode ser removida no JSON."""
        task = self.json_manager.add_task("Tarefa para Remover")
        self.json_manager.remove_task(task["id"])
        tasks = self.json_manager.list_tasks()
        self.assertNotIn(task, tasks)

    def test_add_task_sqlite(self):
        """Testa se uma tarefa é adicionada corretamente no SQLite."""
        task = {"title": "Tarefa no SQLite", "description": "Teste", "completed": False} # noqa501
        self.sqlite_manager.save_task(task)
        tasks = self.sqlite_manager.load_tasks()
        self.assertTrue(any(t["title"] == "Tarefa no SQLite" for t in tasks))

    def tearDown(self):
        """Remove os arquivos de teste após a execução dos testes."""
        if os.path.exists("test_tasks.json"):
            os.remove("test_tasks.json")
        if os.path.exists("test_tasks.db"):
            os.remove("test_tasks.db")


if __name__ == "__main__":
    unittest.main()
