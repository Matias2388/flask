from email import message
from tokenize import Intnumber
from .models import CriptoModel, Database, Transaccion
from flask import Flask, render_template, request, abort, redirect
APIKEY = "36EAEB03-5E48-4A18-9C93-1F2F16B9B9E5"

db = Database()
app = Flask(__name__)


# TODO
# Centrar tabla estados

@app.route('/')
def home():
    """
    Muestra la lista/tabla de movimientos cargados.
    """
    transacciones = db.conseguir_transacciones()
    transacciones.reverse()

    return render_template("index.html", transacciones=transacciones)


@app.get('/consulta')
def consulta_inicio():
    try:
        origen = request.args.get("origen")
        destino = request.args.get("destino")
        cantidad_origen = request.args.get("cantidad")

        if origen and destino:
            if origen == destino:
                raise APIError("La moneda de origen debe ser distinta a la de destino")

            if origen == "EUR" and destino != "BTC":
                raise APIError("Solo se permite comprar BTC con EUR")

            if destino == "EUR" and origen != "BTC":
                raise APIError("Solo se permite comprar EUR con BTC")

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
    except ValueError:
        return render_template("error.html", mensaje="Valor invalido: Error de conversión")
    except APIError as e:
        return render_template("error.html", mensaje=str(e))
    except Exception:
        return render_template("error.html", mensaje="Error desconocido")


@app.post('/compra')  # Guardando datos que provienen del Formulario
def compra():
    try:
        origen = request.form.get("origen")
        destino = request.form.get("destino")
        cantidad = request.form.get(
            "cantidad")  # cantidad = Intnumber("Cantidad", validators=[DataRequired(message="Debes especificar un número")])

        if not origen or not destino or not cantidad:
            raise APIError("Transacción inválida")

        if origen == destino:
            raise APIError("La moneda de origen debe ser distinta a la de destino")

        if origen == "EUR" and destino != "BTC":
            raise APIError("Solo se permite comprar BTC con EUR")

        if destino == "EUR" and origen != "BTC":
            raise APIError("Solo se permite comprar EUR con BTC")

        crypto = CriptoModel(origen, destino)
        crypto.consultar_cambio()

        tx = Transaccion(origen, destino, float(cantidad),
                         crypto.cambio)  # Guardando todos los valores en clase Transaccion
        db.guardar_transaccion(tx)  # Guardar datos en funcion guardar_transaccion" desde clase Database (db)

        return redirect("/")
    except Exception as e:
        return render_template("error.html", mensaje=f"Error desconocido: {str(e)}")


@app.route('/estado')
def actualizar():
    try:
        saldos = db.conseguir_cartera()

        # Valor de la inversión en EUR
        inversion_atrapada_eur = 0
        for saldo in saldos:
            crypto = CriptoModel(saldo.moneda, "EUR")
            crypto.consultar_cambio()

            inversion_atrapada_eur += saldo.cantidad * crypto.cambio

        # Cantidad de EUR invertidos
        inversion_eur = db.conseguir_suma_eur_origen()

        # Cantidad de EUR retornados
        retorno_eur = db.conseguir_suma_eur_destino()

        ganancia = retorno_eur - inversion_eur

        # Valor actual: será Total de euros invertidos + Saldo de euros invertidos (ganancia/
        # perdida) + Valor de euros de nuestras criptos (inversión atrapada)

        valor_actual = inversion_eur + ganancia + inversion_atrapada_eur

        return render_template("estado.html",
                               saldos=saldos,
                               inversion_atrapada_eur=round(inversion_atrapada_eur, 3),
                               inversion_eur=inversion_eur,
                               retorno_eur=retorno_eur,
                               ganancia=ganancia,
                               valor_actual=round(valor_actual, 3))
    except Exception as e:
        return render_template("error.html", mensaje=f"Error desconocido: {str(e)}")


@app.errorhandler(Exception)
def error(e):
    # No funciona sin sacar try-catch en los endpoints!
    render_template("error.html", mensaje=f"Error desconocido: {str(e)}")
