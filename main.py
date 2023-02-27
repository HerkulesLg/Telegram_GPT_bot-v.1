import asyncio
import logging
import config
import openai
import user_save

from deep_translator import GoogleTranslator
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command

TOKEN = config.tg_token
openai.api_key = config.openai_token
chanel_url = config.chanel_url
bot = Bot(TOKEN, parse_mode='HTML')
router = Router()


# срабатывает когда пишут в ЛС боту команду /start
@router.message(Command(commands=['start']))
async def start(message):
    if message.chat.type == 'private':
        text = f'Рад тебя видеть {message.from_user.full_name}\nЯ инструмент для поиска ответов на твои вопросы.\n' \
               'Напиши мне свой вопрос или действие, а я дам на него ответ.\n\np.s. Только подписчики ' \
               f'<a href="{chanel_url}">моего канала</a> могут использовать бот.'

        user_save.add_data(message.from_user.username, message.from_user.id)  # мой собственный файл для сохранения в БД
        await bot.send_message(chat_id=message.chat.id, text=text)


# Так как GPT-бот лучше воспринимает команды на English, то функция переводит текст на заданный язык
# language == краткое наименование языка для перевода eu,ru
async def translate_message(text, language):
    return GoogleTranslator(source='auto', target=f'{language}').translate(text)


# само тело запроса в GPT бот
async def GPT_request(message):
    prompt = message
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=await translate_message(prompt, 'en'),
        temperature=0.5,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.0,
    )
    return await translate_message(response['choices'][0]['text'], 'ru')


# проверяет подписан ли пользователь на канал
async def check_sub(user_id):
    x = await bot.get_chat_member(chat_id=config.chanel_id, user_id=user_id)
    return x.status in ['creator', 'administrator', 'member']


# принимает все сообщения пользователя и генерирует ответ GPT на вопрос или действие
@router.message()
async def GPT_answer(message):
    print(message.from_user.username, message.text)
    if message.chat.type == 'private' and await check_sub(message.from_user.id):
        await bot.send_message(chat_id=message.chat.id, text='Думаю...\nСкоро напишу.')
        answer = await GPT_request(message.text)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id + 1)
        await bot.send_message(chat_id=message.chat.id, text=answer)
    else:
        text = 'Ошибка.\nЛибо ты написал не в ЛС.\nЛибо не подписался на канал.\nТолько подписчики ' \
               f'<a href="{chanel_url}">моего канала</a> могут использовать бот.'
        await bot.send_message(chat_id=message.chat.id, text=text)


# одобряет заявку на вступление в канал и пишет пользователю приветственное сообщение
@router.chat_join_request()
async def chat_join_request(update):
    await update.approve()
    text = f"Моё уважение, {update.from_user.full_name}!\n" \
           "Рад, что Ты теперь с Нами.\n" \
           "Буду рад, если Ты останешься с нами надолго.\n" \
           f"Теперь ты можешь пользоваться мной пока состоишь в <a href='{chanel_url}'>моем канале</a>.\n\n" \
           "p.s. Если не понимаешь о чем Я, то напиши команду /start"
    await bot.send_message(chat_id=update.from_user.id, text=text)


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
