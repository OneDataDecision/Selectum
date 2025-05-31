import sqlite3

# Base de datos
DB_NAME = 'selectum.db'

# Tarifas de Veloenvíos con descuento, ejemplos (en mayúscula)
# 🔥 Aquí pondremos una muestra; luego metemos las 400+ ciudades si quieres.
tarifas_veloenvios = {
    "BOGOTÁ": 365,
    "CALI": 718,
    "MEDELLÍN": 718,
    "CARTAGENA": 1222,
    "BARRANQUILLA": 1158,
    "BUCARAMANGA": 718,
    "VILLAVICENCIO": 777,
    "PEREIRA": 718,
    "MANIZALES": 718,
    "ARMENIA": 777,
    "SANTA MARTA": 1549,
    "CÚCUTA": 1292
    # 🚛 Aquí irían todas las ciudades que me diste. Empecemos con estas y luego ampliamos.
}

# Conectamos
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Limpiar tabla (opcional)
c.execute("DELETE FROM tarifas")
conn.commit()

# Insertar tarifas de Veloenvíos
for ciudad, precio in tarifas_veloenvios.items():
    c.execute("INSERT INTO tarifas (transportador, ciudad, precio_x_kg) VALUES (?, ?, ?)",
              ("VELOENVÍOS", ciudad.upper(), precio))

# Insertar tarifas de Andino (30% más baratas)
for ciudad, precio in tarifas_veloenvios.items():
    precio_andino = round(precio * 0.7, 2)
    c.execute("INSERT INTO tarifas (transportador, ciudad, precio_x_kg) VALUES (?, ?, ?)",
              ("ANDINO", ciudad.upper(), precio_andino))

conn.commit()
conn.close()

print("🚛 Tarifas cargadas exitosamente.")
