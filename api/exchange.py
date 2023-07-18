import requests


def get_exchange_rate(
    currency: str = "USD",
    currencys_to: list[str] = ["BTC", "ETH", "TON", "USDT", "RUB"],
) -> dict[str, float]:
    exchange_rate: dict[str, float] = {}
    response = requests.get(
        f"https://api.cryptomus.com/v1/exchange-rate/{currency}/list"
    )

    for crypto in response.json()["result"]:
        if crypto["to"] in currencys_to:
            exchange_rate[crypto["to"]] = float(crypto["course"])

    return exchange_rate


def convert_many(
    price: float,
    currency: str = "USD",
    currencys_to: list[str] = ["BTC", "ETH", "TON", "USDT", "RUB"],
) -> dict[str, float]:
    rates: dict[str, float] = get_exchange_rate(
        currency=currency,
        currencys_to=currencys_to,
    )

    converted = {}
    for currency_to, rate in rates.items():
        converted[currency_to] = price * rate

    return converted


def convert(price: float, to: str, currency: str = "USD") -> float:
    rate: dict[str, float] = get_exchange_rate(
        currency=currency,
        currencys_to=[to],
    )
    return price * rate[to]
