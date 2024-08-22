import yfinance as yf
from fastapi import APIRouter

router = APIRouter()


@router.get("/stock-price/{ticker}")
def get_stock_price(ticker: str):
    """
    Obtiene el precio de cierre y el volumen de transacciones de un activo
    financiero durante el último año.

    Args:
        ticker (str): El símbolo del ticker del activo financiero.

    Returns:
        str: Cadena que representa un DataFrame con las fechas, precios de
        cierre, y volúmenes de transacciones del último año.

    Details:
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


@router.get("/financial-statement/{ticker}")
def get_financial_statements(ticker: str):
    """
    Obtener los estados financieros de una empresa.

    Recibe un símbolo bursátil (ticker) y devuelve el balance general de la
    empresa.
    Si el símbolo bursátil contiene un punto (.), se tomará solo la primera
    parte antes del punto.

    El balance general obtenido estará limitado a tres columnas (si es que tiene
    más de tres), y se eliminarán las filas con valores nulos.

    Args:
    - ticker (str): El símbolo bursátil de la empresa.

    Returns:
    - str: El balance general de la empresa en formato de cadena.
    """
    if "." in ticker:
        ticker = ticker.split(".")[0]
    else:
        ticker = ticker

    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet

    if balance_sheet.shape[1] > 3:
        balance_sheet = balance_sheet.iloc[:, :3]

    balance_sheet = balance_sheet.dropna(how="any")
    balance_sheet = balance_sheet.to_string()

    return balance_sheet
