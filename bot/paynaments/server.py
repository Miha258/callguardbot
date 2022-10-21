from .wayforpay import generate_signature, merchant_key, merchant_account
from aiohttp.web_request import Request
from aiohttp.web_response import json_response, StreamResponse
from bot.misc.bot import bot
from ..keyboards.inline import account_markup
from ..database.classes.customer import Customer


async def handle_paynament(request: Request):
    data = await request.json() 

    if data:
        user_id = data["orderReference"].split(':')[1]
        
        if data["transactionStatus"] == "Approved":
            await bot.send_message(text = 'Оплата <b>успішна!</b>', chat_id = user_id)
            await Customer.set_activated(int(user_id), True)
            
            keyboard_markup = await account_markup(int(user_id))
            await bot.send_message(text = "Ваш кабінет:", chat_id = user_id, reply_markup = keyboard_markup)
     
        signature_string = f"{data['orderReference']};accept;1415379863"
        return json_response({
            "orderReference": data["orderReference"], 
            "status": 'accept',
            "time": 1415379863,
            "signature": generate_signature(merchant_key, signature_string)
        })
    return StreamResponse(status = 400, reason = 'Invalid body')
