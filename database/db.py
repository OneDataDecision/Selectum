import sqlite3
from flask import g, current_app

def get_db():
    """
    Devuelve una conexión SQLite almacenada en el contexto de Flask (g).
    Si no existe, la crea usando la ruta en current_app.config['DB_PATH'].
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DB_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    Cierra la conexión SQLite al terminar la petición.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()
