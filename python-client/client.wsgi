import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from client import app as application
