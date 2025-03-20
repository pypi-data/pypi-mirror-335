import requests
import pandas as pd

class CefimData:
    """
    This class holds all the API URLs and queries them for the user. Each method is specialized.
    """

    _url_ntnb = "http://52.204.73.41/api/ntnb"  # TODO update address
    _url_titulos_publicos = "http://52.204.73.41/api/titulospublicos"  # TODO update address

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
