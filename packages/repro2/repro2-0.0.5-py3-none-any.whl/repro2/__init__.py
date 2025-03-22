import importlib.metadata
import os

MODELS_ROOT = f"{os.path.dirname(os.path.abspath(__file__))}/models/_models"
VERSION = importlib.metadata.version("repro2")
