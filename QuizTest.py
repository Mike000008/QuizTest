from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = '6545215360:AAFzT6PdlQ7lqVdRy6gIQKTvnrAsyzCZpPM'
TARGET_USER_ID = 581758740

# Словарь для хранения состояния пользователей и их сообщений
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_data[user_id] = {'stage': 'awaiting_team_name'}
    await update.message.reply_text('Напишите название вашей команды:')

async def handle_team_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in user_data and user_data[user_id].get('stage') == 'awaiting_team_name':
        team_name = update.message.text
        user_data[user_id]['team_name'] = team_name
        user_data[user_id]['stage'] = 'awaiting_option'

        keyboard = [
            [InlineKeyboardButton("Ответить на вопрос", callback_data='Ответить на вопрос')],
            [InlineKeyboardButton("Закончить игру", callback_data='Закончить игру')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f'Название вашей команды: {team_name}. Пожалуйста, выберите опцию:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id in user_data and user_data[user_id].get('stage') == 'awaiting_option':
        if query.data == 'Ответить на вопрос':
            user_data[user_id]['selected_option'] = query.data
            user_data[user_id]['stage'] = 'awaiting_message'

            await query.edit_message_text(text=f"Выбрана опция: {query.data}")
            await query.message.reply_text('Введите текст для отправки:')
        elif query.data == 'Закончить игру':
            await query.edit_message_text(text="Спасибо за игру!")
            del user_data[user_id]
            await query.message.reply_text('Начните игру снова, нажав /start')

async def handle_team_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in user_data:
        if user_data[user_id].get('stage') == 'awaiting_team_name':
            await handle_team_name(update, context)
        elif user_data[user_id].get('stage') == 'awaiting_message':
            user_message = update.message.text
            team_name = user_data[user_id].get('team_name', 'Неизвестная команда')

            # Отправляем сообщение целевому пользователю
            await context.bot.send_message(chat_id=TARGET_USER_ID, text=f"Ответ команды '{team_name}': {user_message}")
            # Уведомляем отправителя о том, что сообщение было отправлено
            await update.message.reply_text('Ваше сообщение отправлено ведущему')

            # Очищаем данные пользователя
            user_data[user_id]['stage'] = 'awaiting_option'

            # Предлагаем снова выбрать опцию
            keyboard = [
                [InlineKeyboardButton("Ответить на вопрос", callback_data='Ответить на вопрос')],
                [InlineKeyboardButton("Закончить игру", callback_data='Закончить игру')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text('Пожалуйста, выберите опцию:', reply_markup=reply_markup)

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_team_message))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
