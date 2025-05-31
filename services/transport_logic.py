# services/transport_logic.py

tarifas_veloenvios = {
    'BOGOTA': 365,
    'CALI': 718,
    'MEDELLIN': 718,
    'CARTAGENA': 1222
    # …otras ciudades…
}

# Generar tarifas Andino
tarifas_andino = {ciudad: round(v * 0.7, 2)
                  for ciudad, v in tarifas_veloenvios.items()}

def seleccionar_transportador(destino: str, peso: float, urgente: bool):
    """
    Devuelve (operador, costo_estimado, fecha_salida, hora_solicitud)
    según la lógica de tarifas y urgencia.
    """
    from datetime import datetime, timedelta

    # Normalizar destino
    dest = destino.upper()
    velo = tarifas_veloenvios.get(dest)
    andi = tarifas_andino.get(dest)

    if velo is None or andi is None:
        return None, None, None, None

    costo_velo = velo * peso
    costo_andino = andi * peso

    ahora = datetime.now()
    hora_solicitud = ahora.strftime('%H:%M')
    limite = ahora.replace(hour=14, minute=0, second=0, microsecond=0)

    if urgente:
        operador = 'Veloenvíos'
        costo = costo_velo
        salida = ahora.date().isoformat() if ahora <= limite else (ahora + timedelta(days=1)).date().isoformat()
    else:
        if costo_andino < costo_velo:
            operador = 'Andino'
            costo = costo_andino
            salida = (ahora + timedelta(days=1)).date().isoformat()
        else:
            operador = 'Veloenvíos'
            costo = costo_velo
            salida = ahora.date().isoformat() if ahora <= limite else (ahora + timedelta(days=1)).date().isoformat()

    return operador, round(costo, 2), salida, hora_solicitud

