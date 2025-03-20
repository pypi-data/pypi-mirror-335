import requests
import pandas as pd

class CefimData:
    """
    This class holds all the API URLs and queries them for the user. Each method
    is specialized.
    """
    _eip = "54.232.94.108"

    def __init__(self):
        self._url_ntnb = f"http://{self._eip}/api/ntnb"
        self._url_titulos_publicos = f"http://{self._eip}/api/titulospublicos"

    def titulos_publicos(self):
        """
        Returns the full database of secondary market data for
        brazilian public bonds

        Returns
        -------
        df: pandas.DataFrame
        """
        response = requests.get(self._url_titulos_publicos)

        if not response.ok:
            msg = "Unable to get data from database"
            raise ConnectionError(msg)

        df = pd.DataFrame(response.json())
        df['reference_date'] = pd.to_datetime(df['reference_date'], unit="ms")
        df['emission_date'] = pd.to_datetime(df['emission_date'], unit="ms")
        df['maturity_date'] = pd.to_datetime(df['maturity_date'], unit="ms")
        return df

    def ntnb(self):
        """
        Returns the secondary market data for NTN-Bs

        Returns
        -------
        df: pandas.DataFrame
        """
        response = requests.get(self._url_ntnb)

        if not response.ok:
            msg = "Unable to get data from database"
            raise ConnectionError(msg)

        df = pd.DataFrame(response.json())
        df['reference_date'] = pd.to_datetime(df['reference_date'], unit="ms")
        df['emission_date'] = pd.to_datetime(df['emission_date'], unit="ms")
        df['maturity_date'] = pd.to_datetime(df['maturity_date'], unit="ms")
        return df
