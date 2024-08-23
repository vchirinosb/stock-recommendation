import re

import requests
import yfinance as yf
from bs4 import BeautifulSoup
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

    El balance general obtenido estará limitado a tres columnas (si es que
    tiene más de tres), y se eliminarán las filas con valores nulos.

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


@router.get("/recent-news/{ticker}")
def get_recent_stock_news(company_name):
    """
    Obtener las noticias recientes sobre una empresa.

    Args:
        company_name (str): nombre de la empresa para la cual buscar noticias.

    Returns:
        str: Contiene las principales noticias recientes.
    """

    def google_query(search_term):
        """
        Generar la URL de búsqueda de Google para el término dado.

        Args:
            search_term (str): Término de búsqueda.

        Returns:
            str: URL de búsqueda de Google.
        """
        if "news" not in search_term:
            search_term = search_term + " stock news"
        url = f"https://www.google.com/search?q={search_term}"
        url = re.sub(r"\s", "+", url)
        return url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/102.0.0.0 Safari/537.36'
    }
    g_query = google_query(company_name)

    try:
        res = requests.get(g_query, headers=headers)
        res.raise_for_status()  # Raise an error for bad responses
    except requests.RequestException as e:
        print(f"Error fetching data from Google: {e}")
        return "Error fetching data from Google."

    soup = BeautifulSoup(res.text, "html.parser")
    print("soup: ", soup)

    news = []
    # Adjust the selectors as needed based on the HTML structure of Google
    # search results.
    for n in soup.find_all("div", class_="n0jPhd ynAwRc tNxQIb nDgy9d"):
        news.append(n.get_text())
    for n in soup.find_all("div", class_="IJl0Z"):
        news.append(n.get_text())

    if len(news) > 6:
        news = news[:4]

    if not news:
        return "There is no news."

    news_string = ""
    for i, n in enumerate(news):
        news_string += f"{i + 1}. {n}\n"

    top5_news = "Recent news:\n\n" + news_string

    return top5_news
