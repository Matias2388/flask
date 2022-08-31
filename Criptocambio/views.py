from .models import CriptoModel, Database, Transaccion
from flask import Flask, render_template, request, abort

APIKEY = "36EAEB03-5E48-4A18-9C93-1F2F16B9B9E5"

db = Database()
app = Flask(__name__)


@app.route('/')
def home():
    """
    Muestra la lista/tabla de movimientos cargados.
    """
    return render_template("nuevo.html")


@app.get('/consulta')
def consulta_inicio():
    return render_template("index.html")


@app.post('/consulta')
def consulta_resultado():
    origen = request.form.get("origen")
    destino = request.form.get("destino")

    if not origen or not destino:
        abort(400)

    crypto = CriptoModel(origen, destino)
    crypto.consultar_cambio()

    cambio = round(crypto.cambio, 5)
    return render_template("index.html", crypto=cambio, origen=origen, destino=destino)


@app.post('/compra')
def compra():
    origen = request.form.get("origen")
    destino = request.form.get("destino")
    cantidad = request.form.get("cantidad")

    crypto = CriptoModel(origen, destino)
    crypto.consultar_cambio()

    db.guardar_transaccion(Transaccion(origen, destino, float(cantidad), crypto.cambio))
    # TODO Validar entradas

    return f"{origen} {destino} {cantidad}"


@app.get('/transacciones')
def transacciones():
    transacciones = db.conseguir_transacciones()

    s = ""
    for tx in transacciones:
        s += f"{tx.origen} {tx.destino} {tx.cantidad} {tx.fecha}\n"

    saldos = db.conseguir_transacciones()
    return render_template("transacciones.html", saldos=saldos)


@app.route('/estado')
def actualizar():
    saldos = db.conseguir_cartera()
    return render_template("estado.html", saldos=saldos)