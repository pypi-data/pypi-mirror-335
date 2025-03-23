import os
import toml
import json
import pickle
import base64
import uuid
import hashlib
from filelock import FileLock

class TomlDB:
    def __init__(self, filename='db.toml', store_to_fs=True):
        self.filename = filename
        self.lockfile = f"{filename}.lock"
        self.lock = FileLock(self.lockfile)
        self.store_to_fs = store_to_fs
        self.pickle_dir = f".{os.path.splitext(filename)[0]}_tdbdata"
        if self.store_to_fs:
            os.makedirs(self.pickle_dir, exist_ok=True)
        self._load_database()

    def _load_database(self):
        """Load the database from a TOML file."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.data = toml.load(f)
        else:
            self.data = {}

    def _save_database(self):
        """Save the database to a TOML file."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            toml.dump(self.data, f)

    def _serialize_value(self, value):
        """Serialize the value to a JSON-compatible format if possible, else use pickle."""
        try:
            return json.dumps(value), 'json'
        except (TypeError, OverflowError):
            if self.store_to_fs:
                # 序列化对象并计算其 SHA-1 哈希值
                pickled_value = pickle.dumps(value)
                sha1_hash = hashlib.sha1(pickled_value).hexdigest()
                # 使用 UUID 和 SHA-1 生成唯一的文件名
                pickle_filename = f"{sha1_hash}tdbdata"
                pickle_path = os.path.join(self.pickle_dir, pickle_filename)
                with open(pickle_path, 'wb') as pf:
                    pf.write(pickled_value)
                return pickle_filename, 'file'
            else:
                base64_value = base64.b64encode(pickle.dumps(value)).decode('utf-8')
                return base64_value, 'pickle'

    def _deserialize_value(self, value, value_type):
        """Deserialize the value based on its storage type."""
        if value_type == 'json':
            return json.loads(value)
        elif value_type == 'pickle':
            pickled_value = base64.b64decode(value.encode('utf-8'))
            return pickle.loads(pickled_value)
        elif value_type == 'file':
            pickle_path = os.path.join(self.pickle_dir, value)
            with open(pickle_path, 'rb') as pf:
                return pickle.load(pf)
        else:
            raise ValueError("Unsupported value type")

    def set(self, key, value):
        """Set a key-value pair in the database."""
        with self.lock:
            self._load_database()
            
            # 检查旧值是否存在且为文件类型，并删除对应的文件
            if key in self.data and self.data[key]['type'] == 'file':
                old_entry = self.data[key]
                old_file_path = os.path.join(self.pickle_dir, old_entry['value'])
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            serialized_value, value_type = self._serialize_value(value)
            self.data[key] = {'value': serialized_value, 'type': value_type}
            self._save_database()


    def get(self, key, default=None):
        """Get a value by key from the database, with an optional default value."""
        with self.lock:
            self._load_database()
            entry = self.data.get(key, None)
            if entry is None:
                return default
            try:
                return self._deserialize_value(entry['value'], entry['type'])
            except (json.JSONDecodeError, pickle.UnpicklingError, TypeError, ValueError):
                return default


    def delete(self, key):
        """Delete a key-value pair from the database."""
        with self.lock:
            self._load_database()
            if key in self.data:
                entry = self.data[key]
                if entry['type'] == 'file':
                    os.remove(os.path.join(self.pickle_dir, entry['value']))
                del self.data[key]
                self._save_database()

    def exists(self, key):
        """Check if a key exists in the database."""
        with self.lock:
            self._load_database()
            return key in self.data

    def keys(self):
        """Return all keys in the database."""
        with self.lock:
            self._load_database()
            return list(self.data.keys())

    def __contains__(self, key):
        """Check if a key exists in the database using 'in' operator."""
        return self.exists(key)

# 示例使用
if __name__ == '__main__':
    # 创建数据库实例时，指定是否将 pickle 数据存储到文件系统
    db = TomlDB(store_to_fs=True)

    db.set('user', {'name': 'Alice', 'age': 30, 'emails': ['alice@example.com', 'a.smith@example.com']})

    # 使用 'in' 运算符检查键是否存在
    if 'user' in db:
        print('user key exists in the database.')

    if 'nonexistent' not in db:
        print('nonexistent key does not exist in the database.')
