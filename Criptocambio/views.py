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
    return render_template("index.html", transacciones=db.conseguir_transacciones())


@app.get('/consulta')
def consulta_inicio():
    return render_template("form.html")


@app.post('/consulta')
def consulta_resultado():
    origen = request.form.get("origen")
    destino = request.form.get("destino")

    if not origen or not destino:
        abort(400)

    crypto = CriptoModel(origen, destino)
    crypto.consultar_cambio()

    cambio = round(crypto.cambio, 5)
    return render_template("form.html", crypto=cambio, origen=origen, destino=destino)


@app.post('/compra')
def compra():
    # TODO Validar entradas
    origen = request.form.get("origen")
    destino = request.form.get("destino")
    cantidad = request.form.get("cantidad")

    # TODO Validar que sea EUR->BTC, BTC->Crypto, Crypto->BTC o BTC->EUR
    if origen == "EUR" and destino != "BTC":
        APIError("Solo se permite comprar BTC con EUR")

    if destino == "EUR" and origen != "BTC":
        APIError("Solo se permite comprar EUR con BTC")

    crypto = CriptoModel(origen, destino)
    crypto.consultar_cambio()

    tx = Transaccion(origen, destino, float(cantidad), crypto.cambio)
    db.guardar_transaccion(tx)

    return f"{origen} {destino} {cantidad}"


@app.get('/transacciones')
def transacciones():
    transacciones = db.conseguir_transacciones()

    s = ""
    for tx in transacciones:
        s += f"{tx.origen} {tx.destino} {tx.cantidad_moneda_destino} {tx.fecha}\n"

    saldos = db.conseguir_transacciones()
    return render_template("transacciones.html", saldos=saldos)


@app.route('/estado')
def actualizar():
    saldos = db.conseguir_cartera()

    euros = 0
    for saldo in saldos:
        crypto = CriptoModel(saldo.moneda, "EUR")
        crypto.consultar_cambio()

        euros += saldo.cantidad * crypto.cambio

    return render_template("estado.html", saldos=saldos, euros=round(euros, 2))