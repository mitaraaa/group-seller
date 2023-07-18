from datetime import datetime
import os
import requests
import dataclasses

token = os.getenv("CRYPTO_PAY_TOKEN")
headers = {"Crypto-Pay-API-Token": token}


@dataclasses.dataclass
class Invoice:
    id: int
    pay_url: str
    time_pay: datetime


def check_status(invoice_id: int) -> bool:
    url = "https://testnet-pay.crypt.bot/api/getInvoices"

    response = requests.get(
        url, headers=headers, data={"invoice_id": invoice_id}
    )
    for invoice in response.json()["result"]["items"]:
        if int(invoice["invoice_id"]) == invoice_id:
            return invoice["status"] == "paid"

    return False


def create_invoice(
    asset: str, amount: float, expiration_date: datetime, group_id: str
) -> Invoice:
    url = "https://testnet-pay.crypt.bot/api/createInvoice"

    response = requests.post(
        url,
        headers=headers,
        data={
            "asset": asset,
            "amount": amount,
            "expiration_date": expiration_date,
            "allow_comments": False,
            "allow_anonymous": False,
        },
    )

    data = response.json()["result"]
    return Invoice(
        data["invoice_id"],
        data["pay_url"],
        datetime.fromisoformat(data["created_at"]),
    )
