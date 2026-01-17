import json
from pathlib import Path

FILE_PATH = Path('registered_qr.json')

def read_from(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data

def write_to(file_path, data):
    with open(file_path, 'w') as file:
        data[new_key] = new_id
        json.dump(data, file, indent=4)
        return data

if __name__ == '__main__':
    new_key = '960a41002dc23d329f84272b4eabd754d6405e8b6fbbb267539934aa03915f27'
    new_id = 'A123F0025'
    rfile = read_from(FILE_PATH)
    wfile = write_to(FILE_PATH, rfile)
    for item, val in wfile.items():
        print(item, val)