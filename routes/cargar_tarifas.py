import sqlite3

# Ruta a tu BD (mismo valor que configuras en app.config['DB_PATH'])
DB_PATH = 'selectum.db'

# Listado completo de ciudades destino (puedes agregar o quitar según tu cobertura)
CIUDADES = [
    'BOGOTA',
    'CALI',
    'MEDELLIN',
    'CARTAGENA',
    'BARRANQUILLA',
    'BUCARAMANGA',
    'PEREIRA',
    'IBAGUE',
    'ARMENIA',
    'CARTAGO',
    'TUNJA',
    'MANIZALES',
    'PASTO',
    'NEIVA',
    'VILLAVICENCIO',
    'CARTAGENA',
    'RIOHACHA'
    # … añade aquí cualquier otra ciudad que cubras …
]

# Tarifas base para Veloenvíos (ejemplo; ajusta valores reales)
TARIFAS_VELO = {
    'BOGOTA': 365,
    'CALI': 718,
    'MEDELLIN': 718,
    'CARTAGENA': 1222,
    'BARRANQUILLA': 950,
    'BUCARAMANGA': 880,
    'PEREIRA': 805,
    'IBAGUE': 780,
    'ARMENIA': 820,
    'CARTAGO': 790,
    'TUNJA': 860,
    'MANIZALES': 830,
    'PASTO': 970,
    'NEIVA': 900,
    'VILLAVICENCIO': 875,
    'RIOHACHA': 1020
}

# Descuento del 30% para Andino
TARIFAS_ANDINO = {ciudad: round(valor * 0.7, 2) for ciudad, valor in TARIFAS_VELO.items()}

# (Opcional) Si quieres añadir un tercer transportador:
# TARIFAS_COOR = {ciudad: round(valor * 0.9, 2) for ciudad, valor in TARIFAS_VELO.items()}

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Crear tabla tarifas si no existe (debería ya existir tras init_db.py)
    c.execute('''
        CREATE TABLE IF NOT EXISTS tarifas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transportador TEXT,
            ciudad TEXT,
            precio_x_kg REAL
        )
    ''')

    # Borrar datos previos
    c.execute('DELETE FROM tarifas')

    # Insertar Veloenvíos
    for ciudad, precio in TARIFAS_VELO.items():
        c.execute('INSERT INTO tarifas (transportador, ciudad, precio_x_kg) VALUES (?, ?, ?)',
                  ('Veloenvíos', ciudad, precio))

    # Insertar Andino
    for ciudad, precio in TARIFAS_ANDINO.items():
        c.execute('INSERT INTO tarifas (transportador, ciudad, precio_x_kg) VALUES (?, ?, ?)',
                  ('Andino', ciudad, precio))

    # (Opcional) Insertar Coordinadora
    # for ciudad, precio in TARIFAS_COOR.items():
    #     c.execute('INSERT INTO tarifas (transportador, ciudad, precio_x_kg) VALUES (?, ?, ?)',
    #               ('Coordinadora', ciudad, precio))

    conn.commit()
    conn.close()
    print("✅ Tabla tarifas poblada correctamente.")

if __name__ == "__main__":
    main()
