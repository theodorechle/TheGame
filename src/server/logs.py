from module_infos import SERVER_PATH
import os

LOG_FILE = os.path.join(SERVER_PATH, 'server.log')

def write_log(message: str, is_err: bool=False) -> None:
    if is_err:
        message = 'Error: ' + message
    with open(LOG_FILE, 'a') as f:
        f.write(message + '\n')
