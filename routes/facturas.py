from flask import Blueprint, render_template, request, redirect, url_for
from database.db import get_db
from datetime import datetime
import io
from pdfminer.high_level import extract_text

facturas_bp = Blueprint('facturas', __name__, url_prefix='/facturas')

@facturas_bp.route('/cargar_factura', methods=['GET', 'POST'])
def cargar_factura():
    if request.method == 'POST':
        archivo = request.files.get('archivo')
        if not archivo or archivo.filename == '':
            return "No se seleccionó archivo. <a href='/facturas/cargar_factura'>Volver</a>", 400

        # Leer contenido del PDF en memoria
        try:
            contenido_pdf = archivo.read()
            texto = extract_text(io.BytesIO(contenido_pdf))
        except Exception as e:
            return f"Error procesando PDF: {str(e)}"

        # Extraer datos del texto (puedes ajustar las palabras claves según tu factura)
        def extraer_dato(texto, campo):
            for linea in texto.splitlines():
                if campo.lower() in linea.lower():
                    partes = linea.split(':')
                    if len(partes) > 1:
                        return partes[1].strip()
            return "No encontrado"

        nombre_cliente       = extraer_dato(texto, "Nombre de Cliente")
        direccion_cliente    = extraer_dato(texto, "Dirección de cliente")
        orden_compra         = extraer_dato(texto, "Numero Orden de compra")
        referencia_producto  = extraer_dato(texto, "Referencia de Producto")
        cantidad             = extraer_dato(texto, "Cantidad")
        bodega               = extraer_dato(texto, "Bodega de despacho")
        valor                = extraer_dato(texto, "Valor")

        return render_template(
            'confirmar_factura.html',
            nombre_cliente=nombre_cliente,
            direccion_cliente=direccion_cliente,
            orden_compra=orden_compra,
            referencia_producto=referencia_producto,
            cantidad=cantidad,
            bodega=bodega,
            valor=valor,
            error=None
        )

    # GET: mostrar formulario de carga de factura
    return render_template('cargar_factura.html')

@facturas_bp.route('/confirmar_factura', methods=['POST'])
def confirmar_factura():
    # Recoger datos enviados desde el formulario de confirmación
    nombre_cliente       = request.form.get('nombre_cliente', '').strip()
    direccion_cliente    = request.form.get('direccion_cliente', '').strip()
    orden_compra         = request.form.get('orden_compra', '').strip()
    referencia_producto  = request.form.get('referencia_producto', '').strip()
    cantidad             = request.form.get('cantidad', '0').strip()
    bodega               = request.form.get('bodega', '').strip()
    valor                = request.form.get('valor', '0').strip()

    # Validar que no vengan vacíos campos esenciales
    if not (nombre_cliente and direccion_cliente and orden_compra and referencia_producto and bodega):
        return render_template(
            'confirmar_factura.html',
            nombre_cliente=nombre_cliente,
            direccion_cliente=direccion_cliente,
            orden_compra=orden_compra,
            referencia_producto=referencia_producto,
            cantidad=cantidad,
            bodega=bodega,
            valor=valor,
            error="Todos los campos obligatorios deben llenarse."
        ), 400

    # Convertir cantidad y valor a tipo numérico
    try:
        unidades = int(cantidad) if cantidad.isdigit() else 0
    except ValueError:
        unidades = 0

    try:
        costo_estimado = float(valor.replace(",", "").replace("$", "")) if valor else 0.0
    except ValueError:
        costo_estimado = 0.0

    # Guardar en la tabla de despachos
    db = get_db()
    c = db.cursor()
    c.execute('''
        INSERT INTO despachos (
            fecha_recepcion,
            hora_solicitud,
            origen,
            destino,
            producto,
            unidades,
            documento_comercial,
            peso,
            volumen,
            urgente,
            operador_logistico,
            costo_estimado,
            dia_salida_estimada,
            estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%Y-%m-%d"),      # fecha_recepcion
        datetime.now().strftime("%H:%M"),         # hora_solicitud
        bodega.upper(),                           # origen ← usamos la bodega como origen
        direccion_cliente.upper(),                # destino ← dirección del cliente
        referencia_producto,                      # producto
        unidades,                                 # unidades
        orden_compra,                             # documento_comercial
        0.0,                                      # peso (desconocido en este momento)
        0.0,                                      # volumen (desconocido)
        "No",                                     # urgente (por defecto)
        "Por definir",                            # operador_logistico (se definirá luego)
        costo_estimado,                           # costo_estimado
        datetime.now().strftime("%Y-%m-%d"),      # dia_salida_estimada
        "En curso"                                # estado inicial
    ))
    db.commit()

    # Redirigir al seguimiento de despachos
    return redirect(url_for('despachos.seguimiento'))
