
from flask import render_template
from . import app


@app.route('/')
def home():
    """
    Muestra la lista/tabla de movimientos cargados.
    """
    return "Tabla con movimientos"

@app.route('/compra',methods=['GET', 'POST'])
def compra():
    return render_template ("index.html")


@app.route('/estado')
def actualizar():
    return "Muestra el estado de la inversion"
