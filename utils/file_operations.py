import os

def list_files_and_directories(path):
    """
    List all files and directories in the given path
    Returns a list of dictionaries containing name, type, and full path
    """
    items = []
    try:
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            item_type = 'folder' if os.path.isdir(full_path) else 'file'
            items.append({
                'name': item,
                'type': item_type,
                'path': full_path
            })
        return sorted(items, key=lambda x: (x['type'] == 'file', x['name'].lower()))
    except PermissionError:
        return []
    except Exception as e:
        return []
