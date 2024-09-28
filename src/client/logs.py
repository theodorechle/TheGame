from module_infos import CLIENT_PATH
import os

LOG_FILE = os.path.join(CLIENT_PATH, 'client.log')

def write_log(message: str, is_err: bool=False) -> None:
    if is_err:
        message = 'Error: ' + message
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(message + '\n')
