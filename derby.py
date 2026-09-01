import os
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)


TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = 7638946848

ORDERS_FILE = "orders.json"


PRODUCTS = {
    "godly": [
        ("Luger", 80),
        ("Bat", 470),
        ("Heartblade", 280),
        ("Candy", 290),
        ("Sweet", 480),
    ],

    "vintage": [
        ("Splitter", 22),
        ("Laser", 47),
        ("Phaser", 39),
    ],

    "legendary": [
        ("Bubbles", 7),
        ("Cupid", 10),
        ("Elite", 10),
    ],

    "chroma": [
        ("Candleflame", 200),
        ("Chroma Luger", 190),
        ("Chroma Laser", 170),
    ],

    "sets": [
        ("Batwing Set", 300),
        ("Ice Set", 350),
    ]
}


CATEGORY_NAMES = {
    "godly": "💎 ГОДЛИ",
    "vintage": "🕰 ВИНТАЖ",
    "legendary": "🔥 ЛЕГЕНДАРНЫЕ",
    "chroma": "🌈 ХРОМЫ",
    "sets": "📦 СЕТЫ"
}


def load_orders():

    if not os.path.exists(ORDERS_FILE):
        return {
            "last_order": 1000,
            "orders": []
        }

    try:
        with open(
            ORDERS_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except:
        return {
            "last_order": 1000,
            "orders": []
        }



def save_orders(data):

    with open(
        ORDERS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )



def create_order(product, price, user):

    data = load_orders()

    data["last_order"] += 1

    order_id = data["last_order"]


    order = {
        "id": order_id,
        "product": product,
        "price": price,
        "user_id": user.id,
        "username": user.username
    }


    data["orders"].append(order)

    save_orders(data)


    return order_id



def main_menu():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💎 Годли",
                callback_data="cat_godly"
            )
        ],
        [
            InlineKeyboardButton(
                "🕰 Винтаж",
                callback_data="cat_vintage"
            )
        ],
        [
            InlineKeyboardButton(
                "🔥 Легендарные",
                callback_data="cat_legendary"
            )
        ],
        [
            InlineKeyboardButton(
                "🌈 Хромы",
                callback_data="cat_chroma"
            )
        ],
        [
            InlineKeyboardButton(
                "📦 Сеты",
                callback_data="cat_sets"
            )
        ]
    ])



async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🔪 DERBY SHOP\n\n"
        "Добро пожаловать в магазин MM2!\n\n"
        "Выбери категорию:",
        reply_markup=main_menu()
    )



async def button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    data = query.data



    if data.startswith("cat_"):

        category = data.replace(
            "cat_",
            ""
        )


        keyboard = []


        for i, item in enumerate(PRODUCTS[category]):

            name, price = item

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"🔪 {name} — {price} ₽",
                        callback_data=f"product_{category}_{i}"
                    )
                ]
            )


        keyboard.append(
            [
                InlineKeyboardButton(
                    "⬅️ Назад",
                    callback_data="back"
                )
            ]
        )


        await query.edit_message_text(

            CATEGORY_NAMES[category] +
            "\n\nВыбери товар:",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )



    elif data.startswith("product_"):

        _, category, index = data.split("_")

        index = int(index)


        name, price = PRODUCTS[category][index]


        keyboard = [

            [
                InlineKeyboardButton(
                    "🛒 Купить",
                    callback_data=f"buy_{category}_{index}"
                )
            ],

            [
                InlineKeyboardButton(
                    "⬅️ Назад",
                    callback_data=f"cat_{category}"
                )
            ]

        ]


        await query.edit_message_text(

            f"🔪 {name}\n\n"
            f"💰 Цена: {price} ₽\n\n"
            "Нажми купить:",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )



    elif data.startswith("buy_"):

        _, category, index = data.split("_")

        index = int(index)


        name, price = PRODUCTS[category][index]


        user = query.from_user


        order_id = create_order(
            name,
            price,
            user
        )


        await query.edit_message_text(

            f"✅ Заказ #{order_id} создан!\n\n"
            f"🔪 {name}\n"
            f"💰 {price} ₽\n\n"
            "Ожидай связи с продавцом."
        )


        await context.bot.send_message(

            ADMIN_ID,

            f"🔔 Новый заказ #{order_id}\n\n"
            f"Товар: {name}\n"
            f"Цена: {price} ₽\n\n"
            f"Покупатель: {user.full_name}\n"
            f"ID: {user.id}"
        )



    elif data == "back":

        await query.edit_message_text(

            "🔪 DERBY SHOP\n\n"
            "Выбери категорию:",

            reply_markup=main_menu()
        )



async def error_handler(
    update,
    context
):

    print(
        "Ошибка:",
        context.error
    )



def main():

    print(
        "Derby Shop запускается..."
    )


    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )


    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    app.add_handler(
        CallbackQueryHandler(
            button
        )
    )


    app.add_error_handler(
        error_handler
    )


    print(
        "Derby Shop запущен!"
    )


    app.run_polling()



if __name__ == "__main__":
    main()