import datetime
import requests
import hmac
import hashlib


merchant_account = 'github_com5'
merchant_key = "04c61da8bb18e75913da311989924be68beaf404"
merchant_domain = 'edossecurity.com'  
generate_signature = lambda merchant_key, data_str: hmac.new(merchant_key.encode('utf-8'), data_str.encode('utf-8'), hashlib.md5).hexdigest()


def get_invoice_url(user_id: int) -> str:
    order_date = str(round(datetime.datetime.now().timestamp()))
    signature_data = f"{merchant_account};{merchant_domain};{order_date}:{user_id};1421412898;1;UAH;Виклик охорони;1;1"
   
    body = {
        "transactionType": "CREATE_INVOICE",
        "merchantAccount": merchant_account,
        "merchantDomainName": merchant_domain,
        "merchantSignature": generate_signature(merchant_key, signature_data),
        "apiVersion": 1,
        "language": "ua",
        "serviceUrl": "https://44be-194-44-56-49.eu.ngrok.io",
        "orderReference": f"{order_date}:{user_id}",
        "orderDate": 1421412898,
        "amount": 1, 
        "currency": "UAH",
        "orderTimeout": 86400,
        "productName": ["Виклик охорони"],
        "productPrice": [1],
        "productCount": [1],
    }

    r = requests.get('https://api.wayforpay.com/api', json = body)
    data = r.json()
    return data["invoiceUrl"]


