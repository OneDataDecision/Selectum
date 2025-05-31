from flask import Flask, redirect, url_for, render_template
from routes.despachos import despachos_bp
from routes.facturas import facturas_bp

app = Flask(__name__)

app.config['DB_PATH'] = 'selectum.db'

@app.route("/")
def index():
    # Redirige al formulario de nuevo despacho
    return render_template("index.html")

@app.route("/nuevo")
def nuevo():
    return render_template("nuevo.html")

# Registrar blueprints
app.register_blueprint(despachos_bp)
app.register_blueprint(facturas_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
