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

ADMIN_ID = int(
    os.getenv("ADMIN_ID", "7638946848")
)

DATA_DIR = os.getenv(
    "DATA_DIR",
    "/app/data"
)

ORDERS_FILE = os.path.join(
    DATA_DIR,
    "orders.json"
)

PRODUCTS = {
    "godly": [
        ("Snowcannon", 2069),
        ("Harvester", 760),
        ("Snow Dagger", 632),
        ("Watergun", 547),
        ("Treat", 524),
        ("Sweet", 480),
        ("Bat", 470),
        ("Ornament", 360),
        ("Beach", 350),
        ("Sands", 340),
        ("Candy", 290),
        ("Heartblade", 280),
        ("Phantom", 135),
        ("Iceblaster", 132),
        ("Sugar", 131),
        ("Darkbringer", 130),
        ("Elderwood Revolver", 130),
        ("Lightbringer", 110),
        ("Plasmabeam", 110),
        ("Amerilaser", 106),
        ("Laser", 101),
        ("BattleAxe", 98),
        ("Vampire's Edge", 90),
        ("Plasmablade", 90),
        ("Shark", 88),
        ("Gemstone", 87),
        ("Old Glory", 86),
        ("Hallowgun", 84),
        ("BattleAxe II", 83),
        ("Pixel", 81),
        ("Luger", 80),
        ("Bioblade", 62),
        ("Xmas", 58),
        ("Purple Seer", 50),
        ("Seer", 30),
    ],

    "vintage": [
        ("Laser", 47),
        ("America", 47),
        ("Phaser", 39),
        ("Shadow", 34),
        ("Cowboy", 33),
        ("Golden", 31),
        ("Blood", 28),
        ("Ghost", 26),
        ("Splitter", 22),
        ("Prince", 22),
    ],

    "legendary": [
        ("Bunnies", 70),
        ("Palms", 11),
        ("Rune", 10.5),
        ("Shiny", 10.2),
        ("Cupid", 10),
        ("Elite", 10),
        ("Midnight", 9),
        ("Viper", 8),
        ("Bubbles", 7),
        ("Splash", 7),
    ],

    "chroma": [
        ("Candleflame", 200),
        ("Luger", 190),
        ("Laser", 170),
        ("Seer", 110),
        ("Saw", 93.2),
        ("Slasher", 90),
    ],

    "sets": [
        ("Ice Set", 350),
        ("Batwing Set", 300),
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
    os.makedirs(DATA_DIR, exist_ok=True)

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
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Неверный формат orders.json")

        data.setdefault("last_order", 1000)
        data.setdefault("orders", [])

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError
    ):
        return {
            "last_order": 1000,
            "orders": []
        }

def save_orders(data):
    os.makedirs(DATA_DIR, exist_ok=True)

    temporary_file = ORDERS_FILE + ".tmp"

    with open(
        temporary_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )

    os.replace(
        temporary_file,
        ORDERS_FILE
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
        "username": user.username,
        "name": user.full_name,
        "status": "Новый"
    }

    data["orders"].append(order)

    save_orders(data)

    return order_id

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                "💎 Годли",
                callback_data="cat:godly"
            )
        ],
        [
            InlineKeyboardButton(
                "🕰 Винтаж",
                callback_data="cat:vintage"
            )
        ],
        [
            InlineKeyboardButton(
                "🔥 Легендарные",
                callback_data="cat:legendary"
            )
        ],
        [
            InlineKeyboardButton(
                "🌈 Хромы",
                callback_data="cat:chroma"
            )
        ],
        [
            InlineKeyboardButton(
                "📦 Сеты",
                callback_data="cat:sets"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🔪 DERBY SHOP\n\n"
        "Добро пожаловать в наш магазин MM2!\n\n"
        "Выбери категорию:",
        reply_markup=main_menu()
    )

async def show_category(query, category):
    keyboard = []

    for index, (name, price) in enumerate(
        PRODUCTS[category]
    ):
        keyboard.append([
            InlineKeyboardButton(
                f"🔪 {name} — {price} ₽",
                callback_data=f"product:{category}:{index}"
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
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )

async def show_product(query, category, index):
    name, price = PRODUCTS[category][index]

    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 Купить",
                callback_data=f"buy:{category}:{index}"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data=f"cat:{category}"
            )
        ]
    ]

    await query.edit_message_text(
        f"🔪 {name}\n\n"
        f"💰 Цена: {price} ₽\n\n"
        "Нажми «Купить», чтобы оформить заказ.",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )

async def buy_product(
    query,
    context,
    category,
    index
):
    name, price = PRODUCTS[category][index]

    user = query.from_user

    order_id = create_order(
        name,
        price,
        user
    )

    await query.answer(
        "Заказ создан!"
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

    username = (
        f"@{user.username}"
        if user.username
        else "нет username"
    )

    try:
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

    except Exception as error:
        print(
            f"Не удалось отправить уведомление админу: {error}"
        )

async def button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    data = query.data

    try:
        if data.startswith("cat:"):
            category = data.split(":", 1)[1]

            if category not in PRODUCTS:
                await query.answer(
                    "Категория не найдена",
                    show_alert=True
                )
                return

            await query.answer()

            await show_category(
                query,
                category
            )

            return

        if data.startswith("product:"):
            parts = data.split(":")

            if len(parts) != 3:
                await query.answer(
                    "Ошибка товара",
                    show_alert=True
                )
                return

            category = parts[1]
            index = int(parts[2])

            if category not in PRODUCTS:
                await query.answer(
                    "Категория не найдена",
                    show_alert=True
                )
                return

            if not 0 <= index < len(PRODUCTS[category]):
                await query.answer(
                    "Товар не найден",
                    show_alert=True
                )
                return

            await query.answer()

            await show_product(
                query,
                category,
                index
            )

            return

        if data.startswith("buy:"):
            parts = data.split(":")

            if len(parts) != 3:
                await query.answer(
                    "Ошибка заказа",
                    show_alert=True
                )
                return

            category = parts[1]
            index = int(parts[2])

            if category not in PRODUCTS:
                await query.answer(
                    "Категория не найдена",
                    show_alert=True
                )
                return

            if not 0 <= index < len(PRODUCTS[category]):
                await query.answer(
                    "Товар не найден",
                    show_alert=True
                )
                return

            await buy_product(
                query,
                context,
                category,
                index
            )

            return

        if data == "back":
            await query.answer()

            await query.edit_message_text(
                "🔪 DERBY SHOP\n\n"
                "Добро пожаловать в наш магазин MM2!\n\n"
                "Выбери категорию:",
                reply_markup=main_menu()
            )

            return

        await query.answer(
            "Неизвестная кнопка",
            show_alert=True
        )

    except Exception as error:
        print(
            f"Ошибка кнопки: {error}"
        )

        try:
            await query.answer(
                "Произошла ошибка. Попробуй ещё раз.",
                show_alert=True
            )
        except Exception:
            pass

async def error_handler(
    update,
    context
):
    print(
        f"Ошибка бота: {context.error}"
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

    app.run_polling(
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()