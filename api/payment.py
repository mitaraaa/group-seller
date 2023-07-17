import os
import requests


def create_pay_order(asset: str, amount: int) -> tuple[str, str, int]:
    url = "https://pay.crypt.bot/api/createInvoice"
    token = os.getenv("CRYPTO_PAY_TOKEN")
    headers = {"Crypto-Pay-API-Token": token}

    response = requests.post(url, headers=headers, data={"asset": asset, "amount": amount})

    data = response.json()
    return data["result"]["url_pay"], data["result"]["time_pay"], data["result"]["invoice_id"]


def check_pay_order(id: int) -> bool:
    url = "https://pay.crypt.bot/api/getInvoice"
    token = os.getenv("CRYPTO_PAY_TOKEN")
    headers = {"Crypto-Pay-API-Token": token}

    response = requests.get(url, headers=headers, data={"invoice_id": id})

    return 1 if response.json()["result"]["status"] == "paid" else 0
