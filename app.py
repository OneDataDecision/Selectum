from flask import Flask, redirect, url_for, render_template
from routes.despachos import despachos_bp
from routes.facturas import facturas_bp
from database.init_db import init_db   # <--- Importar la función de inicialización
import os

app = Flask(__name__)

# Le decimos a Flask dónde estará la base SQLite
app.config['DB_PATH'] = 'selectum.db'


# *******************************
# AQUI INVOCAMOS init_db() UNA VEZ
# *******************************
# Debe ocurrir antes de registrar blueprints, dentro del contexto de la aplicación
with app.app_context():
    init_db()


# Ruta principal: muestra un índice (por ejemplo, logo+menú lateral)
@app.route("/")
def index():
    return render_template("index.html")


# Ruta para formulario “Nuevo Despacho”
@app.route("/nuevo")
def nuevo():
    return render_template("nuevo.html")


# Registrar blueprints con prefijos
app.register_blueprint(despachos_bp, url_prefix='/despachos')
app.register_blueprint(facturas_bp,   url_prefix='/facturas')


if __name__ == '__main__':
    # En local se ejecuta así. En Render, se usará gunicorn desde el Procfile
    app.run(debug=True, port=5001)
