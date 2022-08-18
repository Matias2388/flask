from typing_extensions import Self
import requests

from .import APIKEY

class APIError(Exception):
    pass


class CriptoModel:
    """
    - moneda origen
    - moneda destino
    - cambio
    - consultar cambio (método)
    """
Criptocambio=CriptoModel()

    def __init__ (self,origen,destino):
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
            "X-CoinAPI-Key": APIKEY
        }
        url = f"http://rest.coinapi.io/v1/exchangerate/{self.moneda_origen}/{self.moneda_destino}"
        respuesta = requests.get(url, headers=cabeceras)

        if respuesta.status_code == 200:
            # guardo el cambio obtenido
            self.cambio = self.respuesta.json()["rate"]
        else:
            raise APIError(
                "Ha ocurrido un error {} {} al consultar la API.".format(
                    respuesta.status_code, respuesta.reason
                )
            )

