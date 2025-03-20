import requests

def get_currency_data(currency_code: str):
    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{currency_code.lower()}.json"
    response = requests.get(url)
    return response.json()

def convert(currency_from: str, currency_to: str, amount: float):
    rates = get_currency_data(currency_from)
    rate = rates[currency_from][currency_to]
    converted_amount = amount * rate
    return converted_amount 