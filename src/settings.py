import os
from re import TEMPLATE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_ROOT = os.path.join(BASE_DIR, "static")

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")