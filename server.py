import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

DATA_FILE = "tasks.txt"

class TodoItem:
    _next_id = 1

    def __init__(self, title, priority, done=False, id=None):
        self.id = id if id is not None else TodoItem._next_id
        if id is None:
            TodoItem._next_id += 1
        else:
            TodoItem._next_id = max(TodoItem._next_id, id + 1)
        self.title = title
        self.priority = priority
        self.done = done

    def serialize(self):
        return {"id": self.id, "title": self.title, "priority": self.priority, "isDone": self.done}

class TodoList:
    def __init__(self):
        self.items = []
        self.load_from_file()

    def load_from_file(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    raw_items = json.load(f)
                    for entry in raw_items:
                        item = TodoItem(
                            title=entry["title"],
                            priority=entry["priority"],
                            done=entry["isDone"],
                            id=entry["id"]
                        )
                        self.items.append(item)
            except json.JSONDecodeError:
                self.items = []

    def save_to_file(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([item.serialize() for item in self.items], f, indent=2)

    def add(self, title, priority):
        item = TodoItem(title, priority)
        self.items.append(item)
        self.save_to_file()
        return item

    def all_items(self):
        return [item.serialize() for item in self.items]

    def mark_done(self, task_id):
        for item in self.items:
            if item.id == task_id:
                item.done = True
                self.save_to_file()
                return True
        return False

todo_list = TodoList()

class TodoHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if data is not None:
            self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path == "/tasks":
            self._send_json(todo_list.all_items())
        else:
            self._send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        if self.path == "/tasks":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw)
                title = payload.get("title")
                priority = payload.get("priority")
                if not title or not priority:
                    self._send_json({"error": "Missing title or priority"}, status=400)
                    return
                item = todo_list.add(title, priority)
                self._send_json(item.serialize())
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, status=400)

        elif self.path.startswith("/tasks/") and self.path.endswith("/complete"):
            parts = self.path.strip("/").split("/")
            if len(parts) == 3 and parts[2] == "complete":
                try:
                    task_id = int(parts[1])
                    if todo_list.mark_done(task_id):
                        self._send_json(None, status=200)
                    else:
                        self._send_json({"error": "Task not found"}, status=404)
                except ValueError:
                    self._send_json({"error": "Invalid task ID"}, status=400)
            else:
                self._send_json({"error": "Not found"}, status=404)
        else:
            self._send_json({"error": "Not found"}, status=404)

def run_server(host="0.0.0.0", port=8080):
    server = HTTPServer((host, port), TodoHandler)
    print(f"Сервер запущен и работает на http://{host}:{port}/tasks")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
