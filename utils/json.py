from json import load, dump
    
def json_creater(data, path = 'data.json'):
    with open(f'{path}', 'w+', encoding = 'UTF-8') as file:
        dump(data, file, indent = 4)  

def json_load(path = 'data.json'):
    with open(f'{path}', 'r', encoding = 'UTF-8') as file:
        return load(file)