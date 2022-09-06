from .models import CriptoModel, Database, Transaccion
from flask import Flask, render_template, request, abort

APIKEY = "36EAEB03-5E48-4A18-9C93-1F2F16B9B9E5"

db = Database()
app = Flask(__name__)



# TODO
# Botón de compra en /consulta
# Guardar cantidad de moneda de origen gastada en /comprar en la tabla 'transacciones'
# Validar datos
# Manejar errores


@app.route('/')
def home():
    """
    Muestra la lista/tabla de movimientos cargados.
    """
    return render_template("index.html", transacciones=db.conseguir_transacciones())


@app.get('/consulta')
def consulta_inicio():
    origen = request.args.get("origen")
    destino = request.args.get("destino")
    cantidad_origen = request.args.get("cantidad")

    if origen and destino:
        crypto = CriptoModel(origen, destino)
        crypto.consultar_cambio()

        cambio = round(crypto.cambio, 5)

        if cantidad_origen:
            cantidad_origen = float(cantidad_origen)
            cantidad_destino = cantidad_origen * cambio
            return render_template("form.html",
                                   crypto=cambio,
                                   origen=origen,
                                   destino=destino,
                                   cantidad_origen=cantidad_origen,
                                   cantidad_destino=cantidad_destino)

        return render_template("form.html", crypto=cambio, origen=origen, destino=destino)

    return render_template("form.html")


@app.post('/compra')  # Guardando datos que provienen del Formulario
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

    tx = Transaccion(origen, destino, float(cantidad),
                     crypto.cambio)  # Guardando todos los valores en clase Transaccion
    db.guardar_transaccion(tx)  # Guardar datos en funcion guardar_transaccion" desde clase Database (db)

    return f"{origen} {destino} {cantidad}"


@app.route('/estado')
def actualizar():
    saldos = db.conseguir_cartera()

    euros = 0
    for saldo in saldos:
        crypto = CriptoModel(saldo.moneda, "EUR")
        crypto.consultar_cambio()

        euros += saldo.cantidad * crypto.cambio

    return render_template("estado.html", saldos=saldos, euros=round(euros, 2))
