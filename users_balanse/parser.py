import requests


def get_exchange_rates():

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "X-Requested-With": "XMLHttpRequest",
    }

    url = "https://cbr.ru/Queries/AjaxDataSource/112805"

    data_usd = {"DT": "", "val_id": "R01235", "_": "1667219511852"}
    data_eur = {"DT": "", "val_id": "R01239", "_": "1667219511853"}

    response_dollar = requests.get(url=url, headers=headers, params=data_usd).json()[-1]
    response_euro = requests.get(url=url, headers=headers, params=data_eur).json()[-1]

    return response_dollar, response_euro


# print(f'Дата: {usd_resp["data"][:10]}')
# print(f'Курс USD: {usd_resp["curs"]} рублей')
# print(f'Курс EUR: {eur_resp["curs"]} рублей')
