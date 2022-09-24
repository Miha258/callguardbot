from aiogram import types
from validator import *
from aiogram import Router
from aiogram import F
from aiogram import types
from config import PROVIDER_TOKEN

paynaments_router = Router()

@paynaments_router.callback_query(F.data == 'get_guard_acces')
async def get_guard_acces_handler(query: types.CallbackQuery):
    await query.message.answer_invoice(
        title = 'Оплата охорони',
        description = 'Після оплати ви отрмаєте доступ до кнопки \"Тривога\" і зможете викликати охорону',
        payload = 'guard_paynament',
        start_parameter = 'guards',
        prices = [types.LabeledPrice(label = 'Послуги охорони', amount = 2000)],
        photo_url = 'https://kolecs.lviv.ua/wp-content/uploads/2020/12/orhanizatsiia-fizychnoi-okhorony.jpg',
        photo_height = '512',
        photo_width = '512',
        photo_size = '512',
        provider_token = PROVIDER_TOKEN,
        currency = 'uah',
        need_phone_number = True,
        is_flexible = True
    )



@paynaments_router.shipping_query()
async def shipping_procces(shipping_query: types.ShippingQuery):
    if shipping_query.shipping_address.country_code != 'UA':
        return await shipping_query.answer(ok = False, error_message = 'Послуги охоронців доступні тільки в Україні')
    else:
        return await shipping_query.answer(ok = True, shipping_options = [[
            types.ShippingOption(id = 'guard_service', title = 'Послуги охорони', prices = [types.LabeledPrice(label = 'Послуги охорони', amount = 2000)]    )
        ]])

@paynaments_router.pre_checkout_query()
async def pre_checkout_query_procces(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok = True)


# @paynaments_router.message()
# async def succesful_paynament(message: types.Message):
#     user_id = message.from_user.id

#     await Customer.set_activated(user_id, True)
#     await message.answer('Ви успішно опалтили послуги охоронців')