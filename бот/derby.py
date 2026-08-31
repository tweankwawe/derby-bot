import os
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)



TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = 7638946848
ORDERS_FILE = "orders.json"


PROCESSED_CALLBACKS = set()


PRODUCTS = {
    "godly": [
        ("Luger", 80),
        ("Bat", 470),
        ("Heartblade", 280),
        ("Candy", 290),
        ("Sweet", 480),
        ("Icecream", 560),
        ("Sands", 340),
        ("Beach", 350),
        ("Treat", 524),
        ("Elderwood Revolver", 130),
        ("Iceblaster", 132),
    ],

    "vintage": [
        ("Splitter", 22),
        ("Laser", 47),
        ("Phaser", 39),
        ("Golden", 31),
        ("Shadow", 34),
        ("Cowboy", 33),
        ("Ghost", 26),
        ("America", 47),
        ("Blood", 28),
        ("Prince", 22),
    ],

    "legendary": [
        ("Bubbles", 7),
        ("Splash", 7),
        ("Cupid", 10),
        ("Elite", 10),
        ("Palms", 11),
        ("Viper", 8),
        ("Midnight", 9),
        ("Rune", 10.5),
        ("Predator", 25),
        ("Bunnies", 70),
        ("Shiny", 10.2),
    ],

    "chroma": [
        ("Candleflame", 200),
        ("Luger", 190),
        ("Laser", 170),
        ("Slasher", 90),
        ("Seer", 110),
        ("Saw", 93.2),
    ],

    "sets": [
        ("Batwing Set", 300),
        ("Ice Set", 350),
        ("Ginger Set", 100),
    ],
}


CATEGORY_NAMES = {
    "godly": "💎 ГОДЛИ",
    "vintage": "🕰 ВИНТАЖ",
    "legendary": "🔥 ЛЕГЕНДАРНЫЕ",
    "chroma": "🌈 ХРОМЫ",
    "sets": "📦 СЕТЫ",
}


def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return {
            "last_order": 1000,
            "orders": []
        }

    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {
            "last_order": 1000,
            "orders": []
        }


def save_orders(data):
    with open(ORDERS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


def create_order(name, price, user):
    data = load_orders()

    data["last_order"] += 1
    order_id = data["last_order"]

    order = {
        "id": order_id,
        "product": name,
        "price": price,
        "user_id": user.id,
        "username": user.username,
        "name": user.full_name,
        "status": "Новый"
    }

    data["orders"].append(order)

    save_orders(data)

    return order_id



def main_menu():
    keyboard = [
        [InlineKeyboardButton("💎 Годли", callback_data="cat_godly")],
        [InlineKeyboardButton("🕰 Винтаж", callback_data="cat_vintage")],
        [InlineKeyboardButton("🔥 Легендарные", callback_data="cat_legendary")],
        [InlineKeyboardButton("🌈 Хромы", callback_data="cat_chroma")],
        [InlineKeyboardButton("📦 Сеты", callback_data="cat_sets")],
    ]

    return InlineKeyboardMarkup(keyboard)




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔪 DERBY SHOP\n\n"
        "Добро пожаловать в наш магазин MM2!\n\n"
        "Выбери категорию:",
        reply_markup=main_menu()
    )




async def show_category(update, context):
    query = update.callback_query
    await query.answer()

    category = query.data.replace("cat_", "")

    keyboard = []

    for i, (name, price) in enumerate(PRODUCTS[category]):
        keyboard.append([
            InlineKeyboardButton(
                f"🔪 {name} — {price} ₽",
                callback_data=f"product_{category}_{i}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data="back"
        )
    ])

    await query.edit_message_text(
        f"{CATEGORY_NAMES[category]}\n\n"
        "Выбери товар:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_product(update, context):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")

    category = parts[1]
    index = int(parts[2])

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
        ],
    ]

    await query.edit_message_text(
        f"🔪 {name}\n\n"
        f"💰 Цена: {price} ₽\n\n"
        "Нажми «Купить», чтобы оформить заказ.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def buy_product(update, context):
    query = update.callback_query

    # Уникальный ID нажатия
    callback_id = query.id

    # Если это же нажатие уже обработано — ничего не делаем
    if callback_id in PROCESSED_CALLBACKS:
        return

    PROCESSED_CALLBACKS.add(callback_id)

    await query.answer("Заказ оформляется...")

    parts = query.data.split("_")

    category = parts[1]
    index = int(parts[2])

    name, price = PRODUCTS[category][index]

    user = query.from_user

    # Создаём только один заказ
    order_id = create_order(
        name,
        price,
        user
    )

    username = (
        f"@{user.username}"
        if user.username
        else "нет username"
    )


    await query.edit_message_text(
        f"🛒 ЗАКАЗ #{order_id}\n\n"
        f"🔪 Товар: {name}\n"
        f"💰 Цена: {price} ₽\n\n"
        "✅ Заказ создан!\n"
        "📩 Ожидай связи с продавцом.",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ В магазин",
                    callback_data="back"
                )
            ]
        ])
    )


    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🔔 НОВЫЙ ЗАКАЗ #{order_id}\n\n"
            f"🔪 Товар: {name}\n"
            f"💰 Цена: {price} ₽\n\n"
            f"👤 Покупатель: {user.full_name}\n"
            f"📱 Username: {username}\n"
            f"🆔 Telegram ID: {user.id}\n\n"
            "📌 Статус: Новый"
        )
    )

async def button(update, context):
    query = update.callback_query

    if query.data.startswith("cat_"):
        await show_category(update, context)

    elif query.data.startswith("product_"):
        await show_product(update, context)

    elif query.data.startswith("buy_"):
        await buy_product(update, context)

    elif query.data == "back":
        await query.answer()

        await query.edit_message_text(
            "🔪 DERBY SHOP\n\n"
            "Выбери категорию:",
            reply_markup=main_menu()
        )


def main():
    print("Derby Shop запускается...")

    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(button)
    )

    print("Derby Shop запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()