import os

MODULE_PATH = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir)
CLIENT_PATH = os.path.join(MODULE_PATH, 'client')
RESOURCES_PATH = os.path.join(CLIENT_PATH, 'resources')
GUI_PATH = os.path.join(CLIENT_PATH, 'gui')
SERVER_PATH = os.path.join(CLIENT_PATH, os.pardir, 'server')