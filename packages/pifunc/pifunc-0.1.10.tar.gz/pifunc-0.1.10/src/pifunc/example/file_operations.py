import os
import json
import csv
import pickle
import shutil
from typing import Any, List, Dict
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml
from contextlib import contextmanager

@contextmanager
def safe_open_file(path: str, mode: str = 'r'):
    """Safely open and automatically close a file."""
    file = None
    try:
        file = open(path, mode)
        yield file
    finally:
        if file:
            file.close()

def read_json_file(filepath: str) -> Dict:
    """Read and parse a JSON file."""
    with safe_open_file(filepath, 'r') as file:
        return json.load(file)

def write_json_file(filepath: str, data: Dict, pretty: bool = True) -> None:
    """Write data to a JSON file."""
    with safe_open_file(filepath, 'w') as file:
        json.dump(data, file, indent=4 if pretty else None)

def read_csv_to_dict(filepath: str) -> List[Dict]:
    """Read CSV file into list of dictionaries."""
    with safe_open_file(filepath, 'r', newline='') as file:
        reader = csv.DictReader(file)
        return list(reader)

def write_dict_to_csv(filepath: str, data: List[Dict]) -> None:
    """Write list of dictionaries to CSV file."""
    if not data:
        return
    
    fieldnames = data[0].keys()
    with safe_open_file(filepath, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def serialize_object(obj: Any, filepath: str) -> None:
    """Serialize an object to a file using pickle."""
    with safe_open_file(filepath, 'wb') as file:
        pickle.dump(obj, file)

def deserialize_object(filepath: str) -> Any:
    """Deserialize an object from a file using pickle."""
    with safe_open_file(filepath, 'rb') as file:
        return pickle.load(file)

def create_directory_if_not_exists(directory: str) -> None:
    """Create a directory if it doesn't exist."""
    Path(directory).mkdir(parents=True, exist_ok=True)

def copy_file_with_backup(src: str, dst: str) -> None:
    """Copy a file and create a backup if destination exists."""
    if os.path.exists(dst):
        backup_path = f"{dst}.bak"
        shutil.copy2(dst, backup_path)
    shutil.copy2(src, dst)

def get_file_info(filepath: str) -> Dict:
    """Get detailed information about a file."""
    stat = os.stat(filepath)
    return {
        'size': stat.st_size,
        'created': stat.st_ctime,
        'modified': stat.st_mtime,
        'accessed': stat.st_atime,
        'is_file': os.path.isfile(filepath),
        'is_dir': os.path.isdir(filepath),
        'extension': os.path.splitext(filepath)[1],
    }

def read_xml_file(filepath: str) -> Dict:
    """Read and parse XML file to dictionary."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    def element_to_dict(element):
        result = {}
        for child in element:
            if len(child) == 0:
                result[child.tag] = child.text
            else:
                result[child.tag] = element_to_dict(child)
        return result
    
    return element_to_dict(root)

def write_xml_file(filepath: str, data: Dict) -> None:
    """Write dictionary to XML file."""
    def dict_to_element(parent: ET.Element, data: Dict):
        for key, value in data.items():
            child = ET.SubElement(parent, key)
            if isinstance(value, dict):
                dict_to_element(child, value)
            else:
                child.text = str(value)
    
    root = ET.Element('root')
    dict_to_element(root, data)
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding='utf-8', xml_declaration=True)

def read_yaml_file(filepath: str) -> Dict:
    """Read and parse YAML file."""
    with safe_open_file(filepath, 'r') as file:
        return yaml.safe_load(file)

def write_yaml_file(filepath: str, data: Dict) -> None:
    """Write dictionary to YAML file."""
    with safe_open_file(filepath, 'w') as file:
        yaml.safe_dump(data, file, default_flow_style=False)

def find_files_by_extension(directory: str, extension: str) -> List[str]:
    """Find all files with specific extension in directory and subdirectories."""
    matches = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(extension):
                matches.append(os.path.join(root, filename))
    return matches

def get_directory_size(directory: str) -> int:
    """Calculate total size of a directory in bytes."""
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size
