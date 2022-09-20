import datetime
import random
import sqlite3
from typing import List
import dotenv
import requests

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
     
        
        cabeceras = {
            "X-CoinAPI-Key": dotenv.dotenv_values().get("APIKEY")
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
    def __init__(self, origen, destino, cantidad_destino, cambio):
        self.origen = origen
        self.destino = destino
        self.fecha = datetime.datetime.now()

        self.cantidad_moneda_destino = cantidad_destino
        self.cambio_origen_a_destino = cambio

        if cambio:
            self.cantidad_moneda_origen = round(cantidad_destino / cambio, 3)


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
            cantidad_origen integer,
            destino text,
            cantidad_destino integer,
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

        cur.execute(
            "INSERT INTO transacciones(origen, cantidad_origen, destino, cantidad_destino, fecha) VALUES (?, ?, ?, ?, ?)",
            (tx.origen, tx.cantidad_moneda_origen, tx.destino, tx.cantidad_moneda_destino, tx.fecha.timestamp()))

        self.db.commit()

    def conseguir_transacciones(self) -> List[Transaccion]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM transacciones")

        data = []
        for fila in cur.fetchall():
            tx = Transaccion(fila[1], fila[3], fila[4], 0)
            tx.fecha = datetime.datetime.fromtimestamp(float(fila[5]))
            tx.cantidad_moneda_origen = fila[2]

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

    def conseguir_suma_eur_origen(self):
        cur = self.db.cursor()
        cur.execute("SELECT cantidad_origen FROM transacciones WHERE origen='EUR'")

        suma = 0
        for fila in cur.fetchall():
            suma += fila[0]

        return suma

    def conseguir_suma_eur_destino(self):
        cur = self.db.cursor()
        cur.execute("SELECT cantidad_destino FROM transacciones WHERE destino='EUR'")

        suma = 0
        for fila in cur.fetchall():
            suma += fila[0]

        return suma
