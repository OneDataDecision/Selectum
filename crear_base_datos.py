import sqlite3

# Crear base de datos y tabla
conn = sqlite3.connect('selectum.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE despachos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_recepcion TEXT,
        documento_comercial TEXT,
        producto TEXT,
        unidades INTEGER,
        origen TEXT,
        destino TEXT,
        estado TEXT,
        fecha_entrega TEXT,
        dias_transito INTEGER,
        transportador TEXT,
        costo_estimado REAL,
        urgente TEXT,
        volumen_total TEXT,
        peso_total REAL
    )
''')

conn.commit()
conn.close()

print(\"Base de datos y tabla 'despachos' creadas correctamente.\")
