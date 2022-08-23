from flask import Flask,render_template,request,abort
from . import app
from.models import CriptoModel

@app.route('/')
def home():
    """
    Muestra la lista/tabla de movimientos cargados.
    """
    return render_template("nuevo.html")

@app.route('/compra',methods=['GET', 'POST'])
def compra():
    if request.method == "GET":
        return render_template("index.html")

    origen = request.form.get("origen")
    destino = request.form.get("destino")

    if not origen or not destino:
        abort(400)

    crypto = CriptoModel(origen, destino)
    crypto.consultar_cambio()

    return render_template("index.html", crypto=crypto.cambio)


@app.route('/estado')
def actualizar():
    return "Muestra el estado de la inversion"
