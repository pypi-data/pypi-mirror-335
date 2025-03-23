import os
import json
import zipfile


def LocalizePath(target_filename: str) -> str:
    matched_paths = []
    start_path = os.getcwd()

    for root, dirs, files in os.walk(start_path):
        if target_filename in files:
            matched_paths.append(os.path.abspath(root))

    if len(matched_paths) == 0:
        raise FileNotFoundError(f"'{target_filename}' was not found in the project structure.")
    elif len(matched_paths) > 1:
        raise RuntimeError(f"Multiple '{target_filename}' files found. Cannot determine root.")

    return matched_paths[0]


def LocalSearch(local_path: str, search_string: str, secure_search: bool = True) -> str:
    if not search_string.startswith("LP"):
        raise ValueError("Search string must start with 'LP'")

    if search_string.startswith("LP."):
        path_parts = search_string[3:].split('.')
        search_path = os.path.join(local_path, *path_parts)
    elif search_string.startswith("LP+"):
        path_parts = search_string[3:].split('+')
        search_path = os.path.join(os.path.dirname(local_path), *path_parts)
    else:
        raise ValueError("Invalid LP search string format")

    if os.path.exists(search_path):
        return search_path
    elif secure_search:
        raise FileNotFoundError(f"'{search_path}' was not found.")
    else:
        return ""


def LoadJson(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def JSEasySearch(json_data: dict, table_path: str, key, value_indices: str):
    try:
        table = json_data
        if table_path:
            for part in table_path.split('.'):
                if isinstance(table, list):
                    part = int(part) - 1
                table = table[part]

        if isinstance(key, int) or (isinstance(key, str) and key.isdigit()):
            keys = list(table.keys())
            key = keys[int(key) - 1]

        target = table[key]

        if isinstance(target, list):
            indices = [int(i) - 1 for i in value_indices.split('/') if i.isdigit()]
            return [target[i] for i in indices if 0 <= i < len(target)]
        else:
            return target

    except Exception as e:
        print(f"JSEasySearch Error: {e}")
        return None


def JSEasyChange(json_data: dict, table_path: str, key, index: int, new_value):
    try:
        table = json_data
        for part in table_path.split('.'):
            table = table[part]

        if isinstance(key, int) or (isinstance(key, str) and key.isdigit()):
            keys = list(table.keys())
            key = keys[int(key) - 1]

        if isinstance(table[key], list):
            table[key][index - 1] = new_value
        else:
            table[key] = new_value

    except Exception as e:
        print(f"JSEasyChange Error: {e}")


def JSEasyAdd(json_data: dict, table_path: str, key, new_value):
    try:
        table = json_data
        for part in table_path.split('.'):
            table = table[part]

        if isinstance(key, int) or (isinstance(key, str) and key.isdigit()):
            keys = list(table.keys())
            key = keys[int(key) - 1]

        current = table.get(key)
        if isinstance(current, list):
            current.append(new_value)
        elif isinstance(current, str):
            table[key] = [current, new_value]
        else:
            table[key] = [new_value]

    except Exception as e:
        print(f"JSEasyAdd Error: {e}")


def JSEasyRemove(json_data: dict, table_path: str, key, index: int):
    try:
        table = json_data
        for part in table_path.split('.'):
            table = table[part]

        if isinstance(key, int) or (isinstance(key, str) and key.isdigit()):
            keys = list(table.keys())
            key = keys[int(key) - 1]

        if isinstance(table[key], list):
            del table[key][index - 1]

    except Exception as e:
        print(f"JSEasyRemove Error: {e}")


def JSEasySave(json_data: dict, path: str):
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=4)
    except Exception as e:
        print(f"JSEasySave Error: {e}")


def JSEasyJsonCreate(path: str, filename: str):
    try:
        if not filename.endswith(".json"):
            filename += ".json"
        full_path = os.path.join(path, filename)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
    except Exception as e:
        print(f"EasyJsonCreate Error: {e}")


def EasyFileCreate(path: str, filename: str):
    try:
        if '.' not in filename:
            filename += ".txt"
        full_path = os.path.join(path, filename)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write("")
    except Exception as e:
        print(f"EasyFileCreate Error: {e}")


def EasyFolderCreate(path: str, foldername: str):
    try:
        os.makedirs(os.path.join(path, foldername), exist_ok=True)
    except Exception as e:
        print(f"EasyFolderCreate Error: {e}")


def EasyZip(folder_path: str):
    try:
        if not os.listdir(folder_path):
            raise ValueError("Folder is empty; nothing to zip.")

        zip_path = folder_path.rstrip("\\/") + ".zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    abs_file = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_file, os.path.dirname(folder_path))
                    zipf.write(abs_file, arcname=rel_path)
    except Exception as e:
        print(f"EasyZip Error: {e}")

def EasyProjectTree(project_path: str, tree_file_name: str):
    try:
        if not tree_file_name.endswith(".txt"):
            tree_file_name += ".txt"
        full_path = os.path.join(project_path, tree_file_name)

        with open(full_path, "w", encoding="utf-8") as f:
            for root, dirs, files in os.walk(project_path):
                level = root.replace(project_path, "").count(os.sep)
                indent = "    " * level
                f.write(f"{indent}📁 {os.path.basename(root)}\n")
                sub_indent = "    " * (level + 1)
                for file in files:
                    f.write(f"{sub_indent}📄 {file}\n")
    except Exception as e:
        print(f"EasyProjectTree Error: {e}")

EasyProjectTree(LocalizePath("README.md"),"TreeForGPT")

import time

def EasyRandom():
    """
    Unique custom pseudo-random number generator (0-9) without using random/secrets modules.
    """
    t = time.time() * 1000000  # microseconds
    x = id(t) ^ int(t) ^ int((t % 7) * 1337)
    x = (x * 3141592653) & 0xFFFFFFFF
    return (x % 10)


def EasyRandomPlus(as_string: bool, amount: int):
    """
    Generates a custom list or string of pseudo-random numbers without any imports beyond time.
    
    Args:
        as_string (bool): True = return as string, False = return list of ints
        amount (int): How many digits to generate
    
    Returns:
        str or list[int]
    """
    results = []
    base = int(time.time() * 1000000)
    for i in range(amount):
        val = (id(base) ^ (base << i) ^ (base >> (i + 1))) * (i + 1337)
        digit = abs(val % 10)
        results.append(str(digit) if as_string else digit)
    return ''.join(results) if as_string else results
def EasyJSTable(json_data: dict, table_name: str):
    try:
        if table_name not in json_data:
            json_data[table_name] = {}
    except Exception as e:
        print(f"EasyJsTable Error: {e}")

def EasyJSKey(json_data: dict, table, key_or_bulk: str, values: str = None, is_multi: bool = False):
    try:
        # Resolve or create table
        if isinstance(table, str):
            if table not in json_data:
                json_data[table] = {}
            table_ref = json_data[table]
        elif isinstance(table, int):
            table_name = list(json_data.keys())[table - 1]
            if table_name not in json_data:
                json_data[table_name] = {}
            table_ref = json_data[table_name]
        elif isinstance(table, dict):
            table_ref = table
        else:
            raise ValueError("Table must be a string, number, or dict (EasyJsTable result).")

        # Multi-key mode
        if is_multi:
            entries = key_or_bulk.split(';')
            for entry in entries:
                if '=' in entry:
                    key, val_string = entry.split('=', 1)
                    parsed_vals = _parse_value_string(val_string)
                    table_ref[key.strip()] = parsed_vals if len(parsed_vals) > 1 else parsed_vals[0]
        else:
            parsed_vals = _parse_value_string(values)
            table_ref[key_or_bulk] = parsed_vals if len(parsed_vals) > 1 else parsed_vals[0]

    except Exception as e:
        print(f"EasyJSKey Error: {e}")


def _parse_value_string(value_string: str):
    parts = value_string.split('/')
    parsed = []
    for val in parts:
        val = val.strip()
        if val.lower() == "true":
            parsed.append(True)
        elif val.lower() == "false":
            parsed.append(False)
        elif val.isdigit():
            parsed.append(int(val))
        elif val.replace('.', '', 1).isdigit():
            parsed.append(float(val))
        elif val.startswith("[") and val.endswith("]"):
            try:
                parsed.append(eval(val)) 
            except:
                parsed.append(val)
        else:
            parsed.append(val)
    return parsed
