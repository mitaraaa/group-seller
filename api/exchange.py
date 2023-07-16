import requests


def get_exchange_rate(
    currency_from: str = "USD",
    currencys_to: list[str] = ["BTC", "ETH", "LTC", "USDT", "RUB"],
):
    exchange_rate = {}
    response = requests.get(
        f"https://api.cryptomus.com/v1/exchange-rate/{currency_from}/list"
    )

    for crypto in response.json()["result"]:
        if crypto["to"] in currencys_to:
            exchange_rate[crypto["to"]] = crypto["course"]

    return exchange_rate


def convert(price: float, to: str, currency: str = "USD"):
    rate = get_exchange_rate(
        currency=currency,
        currencys_to=[to],
    )
    return price * rate[to]
