# services/ocr_service.py

def extraer_dato(texto, campo):
    """
    Recorre el texto línea a línea buscando 'campo' y devuelve lo que está 
    después de ':' si lo encuentra, o "NO ENCONTRADO" en otro caso.
    """
    for linea in texto.splitlines():
        if campo.lower() in linea.lower():
            partes = linea.split(':', 1)
            if len(partes) > 1:
                return partes[1].strip()
    return "NO ENCONTRADO"
