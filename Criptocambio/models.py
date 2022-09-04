import datetime
import random
import sqlite3
from typing import List

import requests

from .import APIKEY
#APIKEY = "36EAEB03-5E48-4A18-9C93-1F2F16B9B9E5"


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
    def __init__(self, origen, destino, cantidad, cambio):
        self.origen = origen
        self.destino = destino
        self.cantidad_moneda_destino = cantidad
        self.fecha = datetime.datetime.now()
        self.cambio_origen_a_destino = cambio


class Saldo:
    def __init__(self, moneda, cantidad):
        self.moneda = moneda
        self.cantidad = cantidad

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

        self.db.execute("""
        CREATE TABLE IF NOT EXISTS cartera (
            id integer PRIMARY KEY,
            moneda text,
            cantidad integer
        );
        """)

    def guardar_transaccion(self, tx: Transaccion):
        cur = self.db.cursor()

        cur.execute("SELECT * FROM cartera WHERE moneda=?", (tx.origen,))
        if tx.origen != "EUR":
            fila_origen = cur.fetchone()
            if fila_origen:
                saldo_origen = fila_origen[2]

                cantidad_venta_origen = tx.cantidad_moneda_destino * tx.cambio_origen_a_destino
                saldo_origen -= cantidad_venta_origen

                if saldo_origen < 0:
                    raise APIError(
                        "Moneda de origen sin saldo"
                    )

                cur.execute("UPDATE cartera SET cantidad=? WHERE moneda=?", (saldo_origen, tx.origen))
            else:
                raise APIError(
                    "Moneda de origen no registrada"
                )

        cur.execute("SELECT * FROM cartera WHERE moneda=?", (tx.destino,))
        fila_dest = cur.fetchone()
        if fila_dest:
            saldo_origen = fila_dest[2]
            saldo_origen += tx.cantidad_moneda_destino

            cur.execute("UPDATE cartera SET cantidad=? WHERE moneda=?", (saldo_origen, tx.destino))
        else:
            cur.execute("INSERT INTO cartera(moneda, cantidad) VALUES (?, ?)", (tx.destino, tx.cantidad_moneda_destino))

        cur.execute("INSERT INTO transacciones(origen, destino, cantidad, fecha) VALUES (?, ?, ?, ?)",
                    (tx.origen, tx.destino, tx.cantidad_moneda_destino, tx.fecha.timestamp()))

        self.db.commit()

    def conseguir_transacciones(self) -> List[Transaccion]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM transacciones")

        data = []
        for fila in cur.fetchall():
            tx = Transaccion(fila[1], fila[2], fila[3], 0)
            tx.fecha = datetime.datetime.fromtimestamp(float(fila[4]))

            data.append(tx)

        return data

    def conseguir_cartera(self) -> List[Saldo]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM cartera")

        data = []
        for fila in cur.fetchall():
            saldo = Saldo(fila[1], fila[2])
            data.append(saldo)

        return data