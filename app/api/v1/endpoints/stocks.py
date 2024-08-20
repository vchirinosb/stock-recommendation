import yfinance as yf
from fastapi import FastAPI

app = FastAPI()


@app.get("/stocks/{ticker}")
def get_stock_price(ticker: str):
    """
    Obtiene el precio de cierre y el volumen de transacciones de un activo
    financiero durante el último año.

    Args:
        ticker (str): El símbolo del ticker del activo financiero.

    Returns:
        str: Una cadena que representa un DataFrame con las fechas, precios de
        cierre, y volúmenes de transacciones del último año.

    Detalles:
        - Si el símbolo del ticker contiene un punto ('.'), se eliminará la
          parte después del punto.
        - El DataFrame devuelto contiene las columnas "Close" (precio de
          cierre) y "Volume" (volumen).
        - Las fechas en el índice del DataFrame se formatean como cadenas.
    """
    if "." in ticker:
        ticker = ticker.split(".")[0]
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    df = df[["Close", "Volume"]]
    df.index = [str(x).split()[0] for x in list(df.index)]
    df.index.rename("Date", inplace=True)

    print(df)

    return df.to_string()
