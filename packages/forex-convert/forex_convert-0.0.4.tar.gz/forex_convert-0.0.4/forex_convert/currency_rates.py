import requests

class CurrencyRates:
    BASE_URL = "http://localhost:8080/rate"

    def __init__(self):
        pass

    def converter(self, from_currency: str, to_currency:str , amount: float) -> float:
        """
        Convert an amount from one currency to another using the conversion API.
        :param from_currency: Source currency code (e.g., "usd").
        :param to_currency: Destination currency code (e.g., "eur").
        :param amount: Amount to convert.
        :return: Converted amount in the destination currency.
        """

        params = {
            "from": from_currency.lower(),
            "to": to_currency.lower(),
            "amount": amount
        }

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if "result" in data:
                return data["result"]
            else:
                raise ValueError(f"Invalid response: {data}")
        except requests.RequestException as e:
            raise ValueError(f"Failed to connect to the API: {e}")
        
        except ValueError as e:
            raise ValueError(f"Invalid response: {e}")