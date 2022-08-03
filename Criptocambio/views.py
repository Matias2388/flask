from . import app

@app.route('/')
def home():
    """
    Muestra la lista/tabla de movimientos cargados.
    """
    return "Tabla de Movmientos"

@app.route('/compra')
def compra():
    return "Muestra el formulario"


@app.route('/estado')
def actualizar():
    return "Muestra el estado de la inversion"
