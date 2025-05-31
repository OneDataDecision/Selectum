import sqlite3
import os

# Ruta de la base (cae en variable de entorno o usa el fichero por defecto)
DB_PATH = os.getenv('DB_PATH', 'selectum.db')

def init_db():
    """
    Inicializa la base de datos creando las tablas necesarias.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Tabla despachos
    c.execute("""
    CREATE TABLE IF NOT EXISTS despachos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_recepcion TEXT,
        hora_solicitud TEXT,
        origen TEXT,
        destino TEXT,
        producto TEXT,
        unidades INTEGER,
        documento_comercial TEXT,
        peso REAL,
        volumen REAL,
        urgente TEXT,
        operador_logistico TEXT,
        costo_estimado REAL,
        dia_salida_estimada TEXT,
        estado TEXT,
        fecha_entrega TEXT,
        dias_transito INTEGER,
        evidencia_entrega TEXT,
        observaciones TEXT
    )
    """)

    # Tabla tarifas
    c.execute("""
    CREATE TABLE IF NOT EXISTS tarifas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transportador TEXT,
        ciudad TEXT,
        precio_x_kg REAL
    )
    """)

    conn.commit()
    conn.close()
    print("Base de datos inicializada en:", DB_PATH)

if __name__ == "__main__":
    init_db()
