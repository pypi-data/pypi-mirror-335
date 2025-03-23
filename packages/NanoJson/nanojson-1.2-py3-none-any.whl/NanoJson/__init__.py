import json, os, traceback

class NanoJson:
  def __init__(self, path, indent=2):
    self.path = path
    self.indent = indent
    self._ensure_file_exists()

  def _ensure_file_exists(self):
    if not os.path.exists(self.path):
      self.write_json({})

  def _handle_exception(self, error):
    error_type = type(error).__name__
    tb = traceback.extract_tb(error.__traceback__)
    line = tb[-1].lineno
    return f"{error_type} at line {line}: {str(error)}"

  def read_json(self, pretty=False):
    try:
      with open(self.path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return json.dumps(data, indent=self.indent, ensure_ascii=False) if pretty else data
    except Exception as e:
      return self._handle_exception(e)

  def write_json(self, data):
    try:
      with open(self.path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=self.indent, ensure_ascii=False)
      return True
    except Exception as e:
      return self._handle_exception(e)

  def update_json(self, key, value):
    data = self.read_json()
    if isinstance(data, dict):
      data[key] = value
      return self.write_json(data)
    return False

  def delete_key(self, key):
    data = self.read_json()
    if isinstance(data, dict) and key in data:
      del data[key]
      return self.write_json(data)
    return False

  def search_key(self, key):
    data = self.read_json()
    return data.get(key) if isinstance(data, dict) else None

  def append_to_list(self, key, value):
    data = self.read_json()
    if isinstance(data, dict):
      if key not in data:
        data[key] = []
      if isinstance(data[key], list):
        data[key].append(value)
        return self.write_json(data)
    return False

  def remove_from_list(self, key, value):
    data = self.read_json()
    if isinstance(data, dict) and key in data and isinstance(data[key], list):
      if value in data[key]:
        data[key].remove(value)
        return self.write_json(data)
    return False

  def deep_search(self, key, data=None):
    if data is None:
      data = self.read_json()
    if isinstance(data, dict):
      if key in data:
        return data[key]
      for sub_key in data:
        result = self.deep_search(key, data[sub_key])
        if result is not None:
          return result
    elif isinstance(data, list):
      for item in data:
        result = self.deep_search(key, item)
        if result is not None:
          return result
    return None

  def merge_json(self, new_data):
    data = self.read_json()
    if isinstance(data, dict) and isinstance(new_data, dict):
      data.update(new_data)
      return self.write_json(data)
    return False

  def clear_json(self):
    return self.write_json({})

  def get_keys(self):
    data = self.read_json()
    return list(data.keys()) if isinstance(data, dict) else []

  def has_key(self, key):
    data = self.read_json()
    return key in data if isinstance(data, dict) else False

  def get_size(self):
    try:
      return os.path.getsize(self.path)
    except Exception as e:
      return self._handle_exception(e)

  def rename_key(self, old_key, new_key):
    data = self.read_json()
    if isinstance(data, dict) and old_key in data:
      data[new_key] = data.pop(old_key)
      return self.write_json(data)
    return False

  def backup_json(self, backup_path):
    try:
      with open(self.path, 'r', encoding='utf-8') as file:
        data = file.read()
      with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(data)
      return True
    except Exception as e:
      return self._handle_exception(e)

  def restore_backup(self, backup_path):
    try:
      with open(backup_path, 'r', encoding='utf-8') as file:
        data = file.read()
      with open(self.path, 'w', encoding='utf-8') as file:
        file.write(data)
      return True
    except Exception as e:
      return self._handle_exception(e)

  def set_default(self, key, default_value):
    data = self.read_json()
    if isinstance(data, dict) and key not in data:
      data[key] = default_value
      return self.write_json(data)
    return False

  def sort_list(self, key, reverse=False):
    data = self.read_json()
    if isinstance(data, dict) and key in data and isinstance(data[key], list):
      try:
        data[key].sort(reverse=reverse)
        return self.write_json(data)
      except Exception as e:
        return self._handle_exception(e)
    return False

  def search_by_path(self, path):
    try:
      keys = path.split(".")
      data = self.read_json()
      for key in keys:
        if isinstance(data, dict) and key in data:
          data = data[key]
        else:
          return None
      return data
    except Exception as e:
      return self._handle_exception(e)

__all__ = ['NanoJson']