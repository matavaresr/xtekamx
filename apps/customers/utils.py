from datetime import datetime

def obtener_fechas_bloqueadas(paquete):
    reservaciones = paquete.reservacion_set.all()
    return [
        {
            "from": r.fecha_inicio.isoformat(),
            "to": r.fecha_fin.isoformat()
        } for r in reservaciones
    ]

def optimizar_rangos_bloqueados(rangos, duracion_dias):
    if not rangos:
        return []

    # Convertir y ordenar
    parsed = sorted([
        {
            "from": datetime.strptime(r["from"], "%Y-%m-%d"),
            "to": datetime.strptime(r["to"], "%Y-%m-%d")
        }
        for r in rangos
    ], key=lambda r: r["from"])

    resultado = [parsed[0]]

    for actual in parsed[1:]:
        previo = resultado[-1]
        diferencia = (actual["from"] - previo["to"]).days

        if diferencia <= duracion_dias:
            previo["to"] = max(previo["to"], actual["to"])
        else:
            resultado.append(actual)

    return [
        {
            "from": r["from"].strftime("%Y-%m-%d"),
            "to": r["to"].strftime("%Y-%m-%d")
        } for r in resultado
    ]
