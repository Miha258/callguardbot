import requests
import wayforpay
import hmac
import hashlib

wayforpay.Api

merchant_account = 'test_merch_n1'
merchant_key = "flk3409refn54t54t*FNJRET"
merchant_domain = 'https://securitybot.ua'

generate_signature = lambda merchant_key, data_str: hmac.new(merchant_key.encode('utf-8'), data_str.encode('utf-8'), hashlib.md5).hexdigest()
signature_data = f"{merchant_account};{merchant_domain};3232235;1421412898;1;UAH;Виклик охорони;1;21.1"

body = {
    "transactionType": "CREATE_INVOICE",
    "merchantAccount": merchant_account,
    "merchantDomainName": merchant_domain,
    "merchantSignature": generate_signature(merchant_key, signature_data),
    "apiVersion": 1,
    "language": "ua",
    "serviceUrl": "https://securitybot.ua",
    "orderReference": "3232235",
    "orderDate": 1421412898,
    "amount": 1,
    "currency": "UAH",
    "orderTimeout": 86400,
    "productName": ["Виклик охорони"],
    "productPrice": [21.1],
    "productCount": [1]
}

r = requests.get('https://api.wayforpay.com/api', json = body)

