from aiogram import types
from ..database.classes.customer import Customer
from ..misc.utils.cities import get_cities
from bot.misc.bot import bot

async def account_markup(user_id: int) -> types.InlineKeyboardMarkup | None:
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
            [
                types.InlineKeyboardButton(text = "Редагування", callback_data = "edit_account"),
                types.InlineKeyboardButton(text = "Видалити акаунт", callback_data = "delete_account")
            ]
        ]
    )
    customer = await Customer.get(user_id)
    if customer:
        # if customer['activated']:
        keyboard_markup.inline_keyboard[0].append(types.InlineKeyboardButton(text = "Тривога", callback_data = "alarm"))
        # else:
        #     keyboard_markup.inline_keyboard[0].append(types.InlineKeyboardButton(text = "Отримати доступ до Охорони", callback_data = "get_guard_acces"))
    return keyboard_markup


def get_cities_markup():
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
        [types.InlineKeyboardButton(text = city, callback_data = city) for city in get_cities()]
    ])
    return keyboard_markup


async def close_alarm(user_id: int):
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
        [
            types.InlineKeyboardButton(text = f"Залишити відгук", callback_data = "leave_respond"),
        ]
    ])
    await bot.send_message(chat_id = user_id, text = 'Тепер ви можете залишити відгук:', reply_markup = keyboard_markup)


async def send_terms(message):
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
        [
            types.InlineKeyboardButton(text = "Так", callback_data = "accept_terms"),
            types.InlineKeyboardButton(text = "Ні", callback_data = "refuse_terms") 
        ]
    ])
    await message.answer("""<b>Ви приймаєте ці послуги\n?</b>Ви також визнаєте, що Послуги, доступні як варіанти замовлень і можуть надаватись: (i) окремими дочірніми компаніями або афілійованими особами EDOS; або (ii) незалежними сторонніми підрядниками.
        ПОСЛУГИ ТА КОНТЕНТ СТОРОННІХ ПОСТАЧАЛЬНИКІВ
        Послуги можуть бути доступні або надаватися шляхом використання послуг і контенту сторонніх постачальників (зокрема, рекламного характеру), які компанія EDOS не контролює. 
        Ви визнаєте, що до використання вами таких послуг і контенту сторонніх постачальників можуть застосовуватися різні умови використання та політики конфіденційності. Компанія EDOS не підтримує такі послуги й контент сторонніх постачальників і за жодних обставин не несе відповідальності за будь-які продукти або послуги таких сторонніх постачальників. 
        Крім того, корпорації Apple Inc., Google, Inc., Microsoft Corporation або Blackberry Limited і/або їхні відповідні міжнародні дочірні компанії й афілійовані особи виступають сторонніми бенефіціарами за умовами цього договору, якщо ви отримуєте доступ до Послуг за допомогою Додатків, розроблених відповідно для Apple iOS, Android і Microsoft Windows або мобільних пристроїв Blackberry. Ці сторонні бенефіціари не виступають сторонами за цим договором і в жодному разі не несуть відповідальності за надання або підтримку Послуг. Ваш доступ до Послуг із використанням цих пристроїв має здійснюватися відповідно до умов, викладених у відповідних правилах користування послугами сторонніх бенефіціарів.
        ФОРМА ВЛАСНОСТІ
        Послуги та всі права, викладені в цьому документі, виступають і залишаються власністю компанії EDOS або її ліцензіарів. Ні ці Умови, ні використання вами Послуг не передають і не надають вам прав: (i) на Послуги або пов’язані з ними права, крім обмеженої ліцензії, наданої вище; і (ii) на використання фірмового найменування, логотипів, найменувань продуктів або послуг, торговельних марок або знаків обслуговування EDOS чи її ліцензіарів або посилань на них.
        3. Користування Послугами
        ОБЛІКОВІ ЗАПИСИ КОРИСТУВАЧІВ
        Щоб використовувати Послуги в максимальному обсязі, ви маєте оформити підписку на чат-бот EDOS Security на платформі Telegram та заповнити всю необхідну інформацію про себе.  Ви можете оформити підписку, якщо вам виповнилося принаймні 18 років або ви досягли повноліття у своїй юрисдикції (якщо воно настає раніше). Під час реєстрації Рахунку ви маєте надати компанії EDOS певну особисту інформацію, а саме: своє повне ім’я, адресу, номер мобільного телефону та вік, а також вказати принаймні один дійсний спосіб оплати (реквізити кредитної картки або авторизованої платіжної служби). Ви погоджуєтеся забезпечити точність, повноту й актуальність даних. Якщо ви не в змозі забезпечити точність, повноту й актуальність даних, зокрема наявність дійсного способу оплати, це може призвести до припинення доступу до Послуг і їх використання або до розірвання компанією EDOS цієї Угоди з вами. Ви несете відповідальність за всі дії, що виконуються з вашого Облікового запису, і погоджуєтеся за жодних обставин не розголошувати свої ім’я користувача та пароль. Ви не можете володіти кількома Обліковими записами, якщо компанія EDOS не надала на це відповідного дозволу.
    """, reply_markup = keyboard_markup)