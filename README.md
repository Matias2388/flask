# flask
examen api flask
PENDIENTE:

1) Compra entre criptos
Ejemplo;

1er. Mov.:Compra  1 BTC con 1000 EUR       origen:1000EUR   destino:1 BTC
2do. Mov.: Compra 12 ETH con 0.5 BTC       origen:0.5 BTC   destino: 12 ETH
3er. Mov.: Compra  0.6 BTC con 10 ETH      origen:10 ETH    destino: 0.6 BTC
4to.Mov.: Compra 200 BNB con 2 ETH         origen: 2 ETH    destino: 200 BNB

*Saldo € invertidos: total € destino - total€ origen (invertido)    (-1000 € )
                      (0)                (1000)

*Valor actual para  cada cripto: total cripto destino - total cripto origen 
                                   (1BTC + 0.6BTC)          (0.5BTC)           
                                      (12ETH)             (10ETH + 2 ETH)
                                     (200 BNB)               (O BNB)


Valor actual para cada cripto  ---> conversión CoinAPI a Euro = inversion atrapada
         1.1 BTC                      x €
           O ETH                      x €
         200 BNB                      x €

En status:

- INVERTIDO: total € origen (invertido)

- VALOR ACTUAL: *Saldo € invertidos + total € origen (invertido) + *Valor actual para cada cripto

___________________________________________________________________________________________________________________

SOBRE ESTE PROGRAMA.

Aplicacion web con la cual se puede simular la compra/venta de criptomonedas. 

Especificaiones

- La aplicacion está creada en flask utilizando base de datos SQL. 
- Las consultas de valores relativos se realizan utilizando la api CoinAPI. Para la obtencion de la api key abrir
  archivo env-template. 

