import os
from collections import deque
from .LocalStore import LocalStore

class Param:
    def __init__(self, filePath=None, default=lambda: {}):
        self.filePath = filePath
        self.localStore = LocalStore(filePath) if filePath else None
        self.count = 0
        self.default = default() if callable(default) else default
        self.load()

    def load(self):
        data = self.localStore.getAll() if self.localStore else {}
        self.data = data if data else self.default
        self.count += 1 if not data else 0
        return self.data

    def has(self, key: str):
        return key in self.data

    def get(self, key=None, default=None):
        if key is None and default is None:
            return self.data

        keys = deque(key.split("/"))

        def extract(data):
            if not keys:
                return data
            attr = keys.popleft()
            try:
                attr = int(attr)
            except ValueError:
                pass
            return extract(data.get(attr, default)) if isinstance(data, (dict, list)) else default

        return extract(self.data)

    def set(self, key, value=None):
        self.count += 1
        if isinstance(key, (list, dict)):
            self.data = key
            return

        keys = deque(key.split("/"))
        data = self.data

        while len(keys) > 1:
            attr = keys.popleft()
            try:
                attr = int(attr)
            except ValueError:
                pass

            if attr not in data or not isinstance(data[attr], (dict, list)):
                data[attr] = {} if not keys[0].isdigit() else []
            data = data[attr]

        last_key = keys.popleft()
        try:
            last_key = int(last_key)
        except ValueError:
            pass
        data[last_key] = value

    def save(self, key=None, value=None):
        if key is not None:
            self.set(key, value)
        if self.count > 0:
            self.localStore.save(self.data)
            self.count = 0

    def delete(self, key, isSave=True):
        self.set(key, None)
        if isSave:
            self.save()

    def pathJoin(self, key, *args):
        return os.path.join(self.get(key), *args).replace("\\", "/")

    def clear(self):
        self.data = None

    def child(self, path=None, default=None):
        return Param(path, default)

    def walk(self, pick=None, check=None, type="all", path=""):
        def traverse(data, path):
            if isinstance(data, dict):
                check and check(path, data)
                for key, value in data.items():
                    traverse(value, f"{path}/{key}" if path else key)
            elif isinstance(data, list):
                for i, value in enumerate(data):
                    traverse(value, f"{path}/{i}" if path else str(i))
            else:
                pick and pick(path, data)

        if type in ("all", "dict"):
            traverse(self.data, path)
        else:
            print("错误的类型")
