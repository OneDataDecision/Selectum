from flask import Blueprint, render_template, request, redirect, url_for
from database.db import get_db
from services.transport_logic import seleccionar_transportador
from datetime import datetime

despachos_bp = Blueprint('despachos', __name__, url_prefix='/despachos')

@despachos_bp.route('/procesar', methods=['POST'])
def procesar():
    origen   = request.form.get('origen', '').strip()
    destino  = request.form.get('destino', '').strip()
    producto = request.form.get('producto', '').strip()

    try:
        unidades = int(request.form.get('unidades', 0))
    except ValueError:
        unidades = 0

    documento_comercial = request.form.get('documento_comercial', '').strip()

    try:
        peso = float(request.form.get('peso_total', 0))
    except ValueError:
        peso = 0.0

    try:
        volumen = float(request.form.get('volumen_total', 0))
    except ValueError:
        volumen = 0.0

    urgente = request.form.get('urgente', 'No').lower() == 'sí'

    operador, costo, salida, hora_solicitud = seleccionar_transportador(destino, peso, urgente)
    if operador is None:
        return f"Destino '{destino}' no cubierto. <a href='{url_for('nuevo')}'>Volver</a>"

    fecha_recepcion = datetime.now().strftime("%Y-%m-%d")

    return render_template(
        'orden_despacho.html',
        fecha_recepcion=fecha_recepcion,
        hora_solicitud=hora_solicitud,
        origen=origen,
        destino=destino,
        producto=producto,
        unidades=unidades,
        documento_comercial=documento_comercial,
        peso=peso,
        volumen=volumen,
        urgente='Sí' if urgente else 'No',
        operador=operador,
        costo_estimado=round(costo, 2),
        salida=salida
    )

@despachos_bp.route('/confirmar_despacho', methods=['POST'])
def confirmar_despacho():
    fecha_recepcion      = request.form.get('fecha_recepcion') or datetime.now().strftime("%Y-%m-%d")
    hora_solicitud       = request.form.get('hora_solicitud') or datetime.now().strftime("%H:%M")
    origen               = request.form.get('origen', '').strip()
    destino              = request.form.get('destino', '').strip()
    producto             = request.form.get('producto', '').strip()

    try:
        unidades = int(request.form.get('unidades', 0))
    except ValueError:
        unidades = 0

    documento_comercial  = request.form.get('documento_comercial', '').strip()

    try:
        peso = float(request.form.get('peso', 0))
    except ValueError:
        peso = 0.0

    try:
        volumen = float(request.form.get('volumen', 0))
    except ValueError:
        volumen = 0.0

    urgente              = request.form.get('urgente', 'No')
    operador_logistico   = request.form.get('operador_logistico', 'Por definir')

    try:
        costo_estimado = float(request.form.get('costo_estimado', 0))
    except ValueError:
        costo_estimado = 0.0

    salida               = request.form.get('salida') or datetime.now().strftime("%Y-%m-%d")

    if not origen or not destino:
        return redirect(url_for('nuevo'))

    db = get_db()
    c = db.cursor()
    c.execute('''
        INSERT INTO despachos (
            fecha_recepcion, hora_solicitud, origen, destino, producto,
            unidades, documento_comercial, peso, volumen, urgente,
            operador_logistico, costo_estimado, dia_salida_estimada, estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
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
        salida,
        'Pendiente de guía'
    ))
    db.commit()
    return redirect(url_for('despachos.seguimiento'))
@despachos_bp.route('/actualizar_guia/<int:id>', methods=['POST'])
def actualizar_guia(id):
    """
    Recibe POST con 'numero_guia' desde el formulario en seguimiento.html.
    Actualiza la fila con ese id: pone numero_guia y cambia estado a 'En tránsito'.
    Luego redirige a /despachos/seguimiento.
    """
    # 1) Recoger número de guía del form
    numero_guia = request.form.get('numero_guia', '').strip()
    if not numero_guia:
        # Si quedó vacío, simplemente volvemos al seguimiento sin modificar nada.
        return redirect(url_for('despachos.seguimiento'))

    # 2) Conectar a la BD y actualizar:
    db = get_db()
    c = db.cursor()
    c.execute(
        """
        UPDATE despachos
        SET numero_guia = ?, estado = 'En tránsito'
        WHERE id = ?
        """,
        (numero_guia, id)
    )
    db.commit()

    # 3) Regresar a la lista de seguimiento
    return redirect(url_for('despachos.seguimiento'))
    
@despachos_bp.route('/seguimiento', methods=['GET'])
def seguimiento():
    db = get_db()
    c = db.cursor()
    c.execute('''
        SELECT id, origen, destino, producto, documento_comercial, operador_logistico,
               costo_estimado, dia_salida_estimada, estado, observaciones
        FROM despachos
        ORDER BY id DESC
    ''')
    despachos = c.fetchall()
    return render_template('seguimiento.html', despachos=despachos)

@despachos_bp.route('/dashboard', methods=['GET'])
def dashboard():
    db = get_db()
    c = db.cursor()

    c.execute("SELECT COUNT(*) FROM despachos")
    total_despachos = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM despachos WHERE estado = 'Entregado'")
    entregados = c.fetchone()[0]

    en_curso = total_despachos - entregados

    c.execute("""
        SELECT AVG(dias_transito)
        FROM despachos
        WHERE estado = 'Entregado' AND dias_transito IS NOT NULL
    """)
    promedio_transito = c.fetchone()[0] or 0
    promedio_transito = round(promedio_transito, 2)

    c.execute("""
        SELECT operador_logistico, COUNT(*)
        FROM despachos
        GROUP BY operador_logistico
    """)
    datos_transportadores = c.fetchall()
    transportadores = [fila[0] for fila in datos_transportadores]
    conteos         = [fila[1] for fila in datos_transportadores]

    return render_template(
        'dashboard.html',
        total_despachos=total_despachos,
        entregados=entregados,
        en_curso=en_curso,
        promedio_transito=promedio_transito,
        transportadores=transportadores,
        conteos=conteos
    )

@despachos_bp.route('/borrar_despachos', methods=['POST'])
def borrar_despachos():
    db = get_db()
    c = db.cursor()
    c.execute("DELETE FROM despachos")
    db.commit()
    return redirect(url_for('nuevo'))

@despachos_bp.route('/subir_evidencia/<int:id>', methods=['GET'])
def subir_evidencia(id):
    return render_template('subir_evidencia.html', id=id)

@despachos_bp.route('/guardar_evidencia/<int:id>', methods=['POST'])
def guardar_evidencia(id):
    archivo = request.files.get('evidencia')
    observaciones = request.form.get('observaciones', '')

    if archivo:
        filename = archivo.filename
        extension = filename.rsplit('.', 1)[-1]

        db = get_db()
        c = db.cursor()
        c.execute("SELECT documento_comercial, dia_salida_estimada FROM despachos WHERE id = ?", (id,))
        resultado = c.fetchone()
        if resultado:
            documento_comercial, salida_estimada = resultado
            nuevo_nombre = f"{documento_comercial}_evidencia.{extension}"
            ruta_guardado = f"static/evidencias/{nuevo_nombre}"
            archivo.save(ruta_guardado)

            fecha_entrega = datetime.now().strftime('%Y-%m-%d')
            salida_dt  = datetime.strptime(salida_estimada, '%Y-%m-%d')
            entrega_dt = datetime.strptime(fecha_entrega, '%Y-%m-%d')
            dias_transito = (entrega_dt - salida_dt).days

            c.execute('''
                UPDATE despachos
                SET estado = 'Entregado',
                    fecha_entrega = ?,
                    dias_transito = ?,
                    evidencia_entrega = ?,
                    observaciones = ?
                WHERE id = ?
            ''', (fecha_entrega, dias_transito, ruta_guardado, observaciones, id))
            db.commit()

    return redirect(url_for('despachos.seguimiento'))

@despachos_bp.route('/rechazar_despacho_factura', methods=['POST'])
def rechazar_despacho_factura():
    nombre_cliente      = request.form.get('nombre_cliente', '')
    direccion_cliente   = request.form.get('direccion_cliente', '')
    orden_compra        = request.form.get('orden_compra', '')
    referencia_producto = request.form.get('referencia_producto', '')
    cantidad            = request.form.get('cantidad', '')
    bodega              = request.form.get('bodega', '')
    valor               = request.form.get('valor', '')
    motivo              = request.form.get('motivo', 'Sin motivo especificado')

    db = get_db()
    c = db.cursor()
    c.execute('''
        INSERT INTO despachos (
            fecha_recepcion, hora_solicitud, origen, destino, producto, unidades,
            documento_comercial, peso, volumen, urgente, operador_logistico, costo_estimado,
            dia_salida_estimada, estado, observaciones
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%Y-%m-%d"),
        datetime.now().strftime("%H:%M"),
        bodega.upper(),
        direccion_cliente.upper(),
        referencia_producto,
        int(cantidad) if cantidad.isdigit() else 0,
        orden_compra,
        0,
        0,
        "No",
        "Por definir",
        float(valor.replace(",", "").replace("$", "")) if valor else 0,
        datetime.now().strftime("%Y-%m-%d"),
        "Rechazado",
        motivo
    ))
    db.commit()
    return redirect(url_for('despachos.seguimiento'))
