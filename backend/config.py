import os
from pathlib import Path

# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'

# Configuración de Flask
class Config:
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
# Configuración del grafo
GRAPH_CONFIG = {
    'min_rating': 1,
    'max_rating': 5,
    'similarity_threshold': 0.1
}