import sqlite3

DB_PATH = 'selectum.db'

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Verificar si la columna ya existe (opcional, prevenir error si ya la agregaste manualmente)
    c.execute("PRAGMA table_info(despachos);")
    columnas = [row[1] for row in c.fetchall()]
    if 'numero_guia' in columnas:
        print("La columna 'numero_guia' ya existe en la tabla 'despachos'.")
    else:
        # Agregar la columna numero_guia (TEXT) y mantener NULL si no se ha ingresado aún
        c.execute("ALTER TABLE despachos ADD COLUMN numero_guia TEXT;")
        print("✅ Columna 'numero_guia' agregada a la tabla 'despachos'.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
