import asyncio
import random
import urllib.parse
import uuid

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InputTextMessageContent,
    InlineQueryResultArticle,
    ReplyKeyboardMarkup,
    KeyboardButton
)
import transliterate

from config import BOT_TOKEN
favorite_links = {}
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------------------
# Хранилище данных
# ---------------------
user_favorites = {}
user_history = {}
user_progress = {}
user_training_state = {}

# ---------------------
# Главное меню кнопок
# ---------------------
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start"), KeyboardButton(text="/learn")],
        [KeyboardButton(text="/help")]
    ],
    resize_keyboard=True
)

# ---------------------
# Популярные песни
# ---------------------
POPULAR_SONGS = [
    "Nirvana Smells Like Teen Spirit",
    "Metallica Enter Sandman",
    "Queen Bohemian Rhapsody",
    "Oasis Wonderwall",
    "Кино Группа крови",
    "Wonderwall  Oasis",
    "Knocking on Heaven's Door  Bob Dylan",
    "Sweet Home Alabama  Lynyrd Skynyrd",
    "Hey There Delilah  Plain White Tys",
    "Shape of You  Ed Sheeran",
    "Counting Stars OneRepublic",
    "Perfect  Ed Sheeran",
    "Somebody That I Used to Know  Gotye",
    "Smash Mouth  All Star",
    "Hello  Adele",
    "Let It Be  The Beatles",
    "Yesterday  The Beatles",
    "House of the Rising Sun  The Animals",
    "Imagine John Lennon",
    "Hotel California  Eagles",
    "Stairway to Heaven  Led Zeppelin",
    "Wish You Were Here  Pink Floyd",
    "Blackbird  The Beatles",
    "Time of Your Life (Good Riddance)  Green Day",
    "Paradise  Coldplay",
    "Demons  Imagine Dragons",
    "Bad Moon Rising  Creedence Clearwater Revival",
    "Stand By Me  Ben E. King",
    "Love Me Do  The Beatles",
    "You Really Got a Hold on Me  The Beatles" ,
    "Let Her Go  Passenger",
    "Counting Stars  OneRepublic",
    "She Will Be Loved  Maroon 5",
    "Zombie The Cranberries",
    "Smells Like Teen Spirit  Nirvana",
    "Boulevard of Broken Dreams  Green Day",
    "Wonder  Shawn Mendes",
    "I'm Yours  Jason Mraz",
    "Cheap Thrills  Sia",
    "Shelter Rider -Riptide  Vance Joy",
    "Stressed Out  Twenty One Pilots",
    "photograph  Ed Sheeran",
    "Stand By Me  Ben E. King",
    "Morning Has Broken  Cat Stevens",
    "You Are So Beautiful  Joe Cocker",
    "Can't Help Falling in Love  Elvis Presley",
    "Halo  Beyoncé",
    "Let It Go  Idina Menzel",
    "All of Me  John Legend",
    "Shallow  Lady Gaga & Bradley Cooper",
    "Thinking Out Loud  Ed Sheeran",
]
POPULAR_SONGS_BY_ARTIST = {
    "Nirvana": ["Smells Like Teen Spirit", "Come As You Are"],
    "Metallica": ["Enter Sandman", "Nothing Else Matters"],
    "Queen": ["Bohemian Rhapsody", "We Will Rock You"],
    "Oasis": ["Wonderwall"],
    "Кино": ["Группа крови"]
}

# ---------------------
# База аккордов
# ---------------------
CHORD_LESSONS = {
    "Am": {
        "diagram": "E|0\nB|1\nG|2\nD|2\nA|0\nE|x",
        "fingers": [
            "1 — 1 лад, 2 струна (B)",
            "2 — 2 лад, 4 струна (D)",
            "3 — 2 лад, 3 струна (G)"
        ],
        "tip": "Не играем 6 струну."
    },
    "C": {
        "diagram": "E|0\nB|1\nG|0\nD|2\nA|3\nE|x",
        "fingers": [
            "1 — 1 лад, 2 струна (B)",
            "2 — 2 лад, 4 струна (D)",
            "3 — 3 лад, 5 струна (A)"
        ],
        "tip": "Ставь пальцы ближе к ладу."
    },
    "G": {
        "diagram": "E|3\nB|3\nG|0\nD|0\nA|2\nE|3",
        "fingers": [
            "2 — 3 лад, 6 струна",
            "1 — 2 лад, 5 струна",
            "3 — 3 лад, 1 струна"
        ],
        "tip": "Следи за открытыми струнами."
    },
    "Em": {
        "diagram": "E|0\nB|0\nG|0\nD|2\nA|2\nE|0",
        "fingers": [
            "1 — 2 лад, 5 струна",
            "2 — 2 лад, 4 струна"
        ],
        "tip": "Самый простой аккорд 👍"
    }
    # ===== МАЖОРНЫЕ =====
    ,
    "A": {
        "diagram": "E|0\nB|2\nG|2\nD|2\nA|0\nE|x",
        "fingers": [
            "1 — 2 лад, 4 струна (D)",
            "2 — 2 лад, 3 струна (G)",
            "3 — 2 лад, 2 струна (B)"
        ],
        "tip": "Не играем 6 струну."
    },
    "C": {
        "diagram": "E|0\nB|1\nG|0\nD|2\nA|3\nE|x",
        "fingers": [
            "1 — 1 лад, 2 струна",
            "2 — 2 лад, 4 струна",
            "3 — 3 лад, 5 струна"
        ],
        "tip": "Большой палец держи за грифом."
    },
    "D": {
        "diagram": "E|2\nB|3\nG|2\nD|0\nA|x\nE|x",
        "fingers": [
            "1 — 2 лад, 3 струна",
            "2 — 2 лад, 1 струна",
            "3 — 3 лад, 2 струна"
        ],
        "tip": "Играем только 4 нижние струны."
    },
    "E": {
        "diagram": "E|0\nB|0\nG|1\nD|2\nA|2\nE|0",
        "fingers": [
            "1 — 1 лад, 3 струна",
            "2 — 2 лад, 5 струна",
            "3 — 2 лад, 4 струна"
        ],
        "tip": "Все струны звучат."
    },
    "F": {
        "diagram": "E|1\nB|1\nG|2\nD|3\nA|3\nE|1",
        "fingers": [
            "1 — баррэ на 1 ладу",
            "2 — 2 лад, 3 струна",
            "3 — 3 лад, 5 струна",
            "4 — 3 лад, 4 струна"
        ],
        "tip": "Сильно прижимай баррэ указательным пальцем."
    },
    "G": {
        "diagram": "E|3\nB|3\nG|0\nD|0\nA|2\nE|3",
        "fingers": [
            "2 — 3 лад, 6 струна",
            "1 — 2 лад, 5 струна",
            "3 — 3 лад, 1 струна"
        ],
        "tip": "Следи за чистотой открытых струн."
    },
    # ===== МИНОРНЫЕ =====
    "Am": {
        "diagram": "E|0\nB|1\nG|2\nD|2\nA|0\nE|x",
        "fingers": [
            "1 — 1 лад, 2 струна",
            "2 — 2 лад, 4 струна",
            "3 — 2 лад, 3 струна"
        ],
        "tip": "Не играем 6 струну."
    },
    "Dm": {
        "diagram": "E|1\nB|3\nG|2\nD|0\nA|x\nE|x",
        "fingers": [
            "1 — 1 лад, 1 струна",
            "2 — 2 лад, 3 струна",
            "3 — 3 лад, 2 струна"
        ],
        "tip": "Аккуратно играй только 4 струны."
    },
    "Em": {
        "diagram": "E|0\nB|0\nG|0\nD|2\nA|2\nE|0",
        "fingers": [
            "1 — 2 лад, 5 струна",
            "2 — 2 лад, 4 струна"
        ],
        "tip": "Отличный аккорд для начала."
    },
    "Bm": {
        "diagram": "E|2\nB|3\nG|4\nD|4\nA|2\nE|x",
        "fingers": [
            "1 — баррэ на 2 ладу",
            "2 — 3 лад, 2 струна",
            "3 — 4 лад, 4 струна",
            "4 — 4 лад, 3 струна"
        ],
        "tip": "Это минорное баррэ."
    },
    # ===== СЕПТАККОРДЫ =====
    "A7": {
        "diagram": "E|0\nB|2\nG|0\nD|2\nA|0\nE|x",
        "fingers": [
            "1 — 2 лад, 4 струна",
            "2 — 2 лад, 2 струна"
        ],
        "tip": "Добавляет блюзовый оттенок."
    },
    "D7": {
        "diagram": "E|2\nB|1\nG|2\nD|0\nA|x\nE|x",
        "fingers": [
            "1 — 1 лад, 2 струна",
            "2 — 2 лад, 1 струна",
            "3 — 2 лад, 3 струна"
        ],
        "tip": "Часто используется в роке."
    },
    "E7": {
        "diagram": "E|0\nB|0\nG|1\nD|0\nA|2\nE|0",
        "fingers": [
            "1 — 1 лад, 3 струна",
            "2 — 2 лад, 5 струна"
        ],
        "tip": "Популярен в блюзе."
    },
    "G7": {
        "diagram": "E|1\nB|0\nG|0\nD|0\nA|2\nE|3",
        "fingers": [
            "1 — 1 лад, 1 струна",
            "2 — 2 лад, 5 струна",
            "3 — 3 лад, 6 струна"
        ],
        "tip": "Используется в фолке и кантри."
    },
    # ===== ДОБАВОЧНЫЕ =====
    "Cadd9": {
        "diagram": "E|3\nB|3\nG|0\nD|2\nA|3\nE|x",
        "fingers": [
            "1 — 2 лад, 4 струна",
            "2 — 3 лад, 5 струна",
            "3 — 3 лад, 2 струна",
            "4 — 3 лад, 1 струна"
        ],
        "tip": "Очень популярен в поп-музыке."
    },
}

# ---------------------
# Вспомогательные функции
# ---------------------
def translit_ru_to_en(text: str) -> str:
    try:
        return transliterate.translit(text, reversed=True)
    except Exception:
        return text

def make_search_url(query: str) -> str:
    query = translit_ru_to_en(query)
    encoded = urllib.parse.quote_plus(query)
    return f"https://www.songsterr.com/?pattern={encoded}"

def get_keyboard(url: str) -> InlineKeyboardMarkup:
    key = str(uuid.uuid4())  # создаем уникальный ключ
    favorite_links[key] = url  # сохраняем URL под этим ключем
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎶 Открыть аккорды", url=url)],
            [InlineKeyboardButton(text="⭐ Добавить в избранное", callback_data=f"fav:{key}")]
        ]
    )
# ---------------------
# Команды
# ---------------------
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎸Привет, меня зовут Гитароша! Я автоматизированный телеграм бот, созданный многоуважаемым @Lykysha. Скинь мне название песни, а я постараюсь найти слова и аккорды.\n\n"
        "Также я умею такие команды:\n"
        "/learn — обучение аккордам\n"
        "/random — случайная песня\n"
        "/favorites — избранное\n"
        "/history — история\n"
        "/about — о боте\n"
        "/help — помощь",
        reply_markup=main_menu
    )

@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "📖 Команды:\n"
        "/learn — обучение аккордам\n"
        "/progress — мой прогресс\n"
        "/random — случайная песня\n"
        "/favorites — избранное\n"
        "/clear — очистить избранное\n"
        "/history — история\n"
        "/about — о боте",
        reply_markup=main_menu
    )

@dp.message(Command("about"))
async def about_command(message: types.Message):
    await message.answer(
        "🎸Гитароша - это бот для поиска и обучения гитарным аккордам.\n"
        "Подсказки: Для более удобного взаимодейстивия с ботом мной продумана панель команд (кнопка меню рядом с полем ввода) в ней я предусматрел лишь самые важные команды.\n"
        "Рекомендации: Из-за замедления телеграма в России ссылка может не открываться, поэтому советую использовать ВПН.\n"
        "Примечания: Большая просьба не ругаться на Гитарошу! Если у вас возникли какие-либо проблемы или ошибки, пишите мне в личку и я постараюсь уладить всё в кротчайшие сроки.\n" \
        "Это мой первый проект, и в дальнейшем Гитароша будет расти и совершенствоваться.\n"
        "Автор: Лукин Никита",
        reply_markup=main_menu
    )

# ---------------------
# Обучение
# ---------------------
@dp.message(Command("learn"))
async def learn_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=chord, callback_data=f"learn:{chord}")]
            for chord in CHORD_LESSONS.keys()
        ]
    )
    await message.answer("🎸 Выбери аккорд:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("learn:"))
async def start_learning(callback: types.CallbackQuery):
    chord = callback.data.split(":")[1]
    user_training_state[callback.from_user.id] = {"chord": chord, "step": 0}
    await show_step(callback)

async def show_step(callback):
    state = user_training_state[callback.from_user.id]
    chord = state["chord"]
    step = state["step"]
    data = CHORD_LESSONS[chord]

    if step < len(data["fingers"]):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➡ Далее", callback_data="next_step")]
            ]
        )

        await callback.message.answer(
            f"🎸 {chord}\n\n<pre>{data['diagram']}</pre>\n\n"
            f"👉 Шаг {step+1}:\n{data['fingers'][step]}",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🧠 Пройти тест", callback_data="quiz")]
            ]
        )

        await callback.message.answer(
            f"✅ Аккорд {chord} изучен!\n💡 {data['tip']}",
            reply_markup=keyboard
        )

@dp.callback_query(lambda c: c.data == "next_step")
async def next_step(callback: types.CallbackQuery):
    user_training_state[callback.from_user.id]["step"] += 1
    await show_step(callback)
    await callback.answer()

# ---------------------
# Тест
# ---------------------
@dp.callback_query(lambda c: c.data == "quiz")
async def quiz(callback: types.CallbackQuery):
    state = user_training_state[callback.from_user.id]
    chord = state["chord"]

    options = list(CHORD_LESSONS.keys())
    random.shuffle(options)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=o, callback_data=f"answer:{o}")]
            for o in options
        ]
    )

    state["quiz"] = chord

    await callback.message.answer(
        f"❓ Какой это аккорд?\n\n<pre>{CHORD_LESSONS[chord]['diagram']}</pre>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("answer:"))
async def answer(callback: types.CallbackQuery):
    selected = callback.data.split(":")[1]
    state = user_training_state[callback.from_user.id]
    correct = state["quiz"]

    progress = user_progress.setdefault(callback.from_user.id, {"learned": set(), "score": 0})

    if selected == correct:
        progress["score"] += 10
        progress["learned"].add(correct)
        await callback.message.answer("✅ Правильно! +10 очков")
    else:
        await callback.message.answer(f"❌ Неверно. Это был {correct}")

    await callback.answer()

# ---------------------
# Прогресс
# ---------------------
@dp.message(Command("progress"))
async def progress(message: types.Message):
    progress = user_progress.get(message.from_user.id, {"learned": set(), "score": 0})

    await message.answer(
        f"📊 Выучено аккордов: {len(progress['learned'])}\n"
        f"Очки: {progress['score']}"
    )

# ---------------------
# Остальной функционал (поиск, избранное, история, inline)
# ---------------------
@dp.callback_query(lambda c: c.data.startswith("fav:"))
async def add_to_favorites(callback: types.CallbackQuery):
    key = callback.data[4:]  # извлекаем ключ
    url = favorite_links.get(key)
    if url:
        favs = user_favorites.setdefault(callback.from_user.id, [])
        if url not in favs:
            favs.append(url)
        await callback.answer("⭐ Добавлено!")
    else:
        await callback.answer("Произошла ошибка, попробуйте снова.", show_alert=True)

@dp.message(Command("favorites"))
async def favorites(message: types.Message):
    favs = user_favorites.get(message.from_user.id, [])
    if not favs:
        await message.answer("⭐ Избранного нет")
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎶 Открыть", url=url)]
            for url in favs
        ]
    )

    await message.answer("⭐ Твоё избранное:", reply_markup=keyboard)

@dp.message(Command("clear"))
async def clear(message: types.Message):
    user_favorites[message.from_user.id] = []
    await message.answer("🗑 Избранное очищено!")

@dp.message(Command("history"))
async def history(message: types.Message):
    hist = user_history.get(message.from_user.id, [])
    if not hist:
        await message.answer("📜 История пуста")
        return
    await message.answer("\n".join(hist))

@dp.message(Command("random"))
async def random_song(message: types.Message):
    query = random.choice(POPULAR_SONGS)
    url = make_search_url(query)
    await message.answer(f"🎲 {query}", reply_markup=get_keyboard(url))

@dp.message()
async def search(message: types.Message):
    query = message.text.strip()
    if not query.startswith("/"):
        hist = user_history.setdefault(message.from_user.id, [])
        if query not in hist:
            hist.append(query)
            if len(hist) > 10:
                hist.pop(0)

        url = make_search_url(query)
        await message.answer("🎸 Вот что я нашёл:", reply_markup=get_keyboard(url))

@dp.inline_query()
async def inline_search(inline_query: InlineQuery):
    query = inline_query.query.strip()
    if not query:
        return

    url = make_search_url(query)

    result = InlineQueryResultArticle(
        id=str(uuid.uuid4()),
        title=f"🎸 Открыть аккорды: {query}",
        input_message_content=InputTextMessageContent(
            message_text=f"🎸 Аккорды для: {query}\n{url}"
        ),
        reply_markup=get_keyboard(url)
    )

    await bot.answer_inline_query(inline_query.id, results=[result], cache_time=0)

# ---------------------
# Запуск
# ---------------------
async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())