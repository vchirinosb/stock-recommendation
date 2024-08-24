from unittest.mock import patch

import pandas as pd
import pytest
import yfinance as yf
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestStockEndpoint:

    @pytest.fixture
    def stock_data(self):
        """
        Fixture that provides mock stock data for testing.
        """
        data = {
            "Close": [150.75, 153.31],
            "Volume": [50000, 60000]
        }
        index = pd.to_datetime(["2023-08-01", "2023-08-02"])
        return pd.DataFrame(data, index=index)

    def test_get_stock_price_valid_ticker(self, stock_data):
        """
        Test to verify the endpoint returns correct data for a valid ticker.
        """
        # Mock the yfinance Ticker object's history method to return the
        # fixture data
        with patch.object(yf.Ticker, 'history', return_value=stock_data):
            response = client.get("/api/v1/stock-price/AAPL")

        assert response.status_code == 200
        assert "2023-08-01" in response.text
        assert "150.75" in response.text
        assert "50000" in response.text
