import datetime
import random
import sqlite3
from typing import List

import requests

# from .import APIKEY
APIKEY = "36EAEB03-5E48-4A18-9C93-1F2F16B9B9E5"


class APIError(Exception):
    pass


class CriptoModel:
    """
    - moneda origen
    - moneda destino
    - cambio
    - consultar cambio (método)
    """

    def __init__(self, origen, destino):
        """
        Construye un objeto con las monedas origen y destino
        y el cambio obtenido desde CoinAPI inicializado a cero.
        """
        self.moneda_origen = origen
        self.moneda_destino = destino
        self.cambio = 0.0

    def consultar_cambio(self):
        """
        Consulta el cambio entre la moneda origen y la moneda destino
        utilizando la API REST CoinAPI.
        """

        self.cambio = random.random()
        return

        cabeceras = {
            "X-CoinAPI-Key": APIKEY
        }

        url = f"http://rest.coinapi.io/v1/exchangerate/{self.moneda_origen}/{self.moneda_destino}"
        respuesta = requests.get(url, headers=cabeceras)

        if respuesta.status_code == 200:
            # guardo el cambio obtenido
            self.cambio = respuesta.json()["rate"]
        else:
            raise APIError(
                "Ha ocurrido un error {} {} al consultar la API.".format(
                    respuesta.status_code, respuesta.reason
                )
            )


class Transaccion:
    def __init__(self, origen, destino, cantidad):
        self.origen =  origen
        self.destino = destino
        self.cantidad = cantidad
        self.fecha = datetime.datetime.now()

class Database:
    def __init__(self):
        self.db = sqlite3.connect("database.db", check_same_thread=False)
        self.db.execute("""CREATE TABLE IF NOT EXISTS transacciones (
            id integer PRIMARY KEY,
            origen text,
            destino text,
            cantidad integer,
            fecha text
        );""")

    def guardar_transaccion(self, tx: Transaccion):
        cur = self.db.cursor()
        cur.execute("INSERT INTO transacciones(origen, destino, cantidad, fecha) VALUES (?, ?, ?, ?)",
                    (tx.origen, tx.destino, tx.cantidad, tx.fecha.timestamp()))

        self.db.commit()

    def conseguir_transacciones(self) -> List[Transaccion]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM transacciones")

        data = []
        for fila in cur.fetchall():
            tx = Transaccion(fila[1], fila[2], fila[3])
            tx.fecha = datetime.datetime.fromtimestamp(float(fila[4]))

            data.append(tx)

        return data
