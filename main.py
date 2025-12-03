from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime
import uuid

from aiogram_widgets.pagination import KeyboardPaginator
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    InlineKeyboardButton,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from NotifyLoader import *
from NotifyManager import *
from TemplateLoader import *
from DataTypes import *
from DateUtils import *

notifyLoader = NotifyLoader()
notifyManager = NotifyManager()
templateLoader = TemplateLoader()
userCommandContexts = {}
router = Router(name="router")

dp = Dispatcher()
bot: Bot

@dp.message(Command("start"))
async def start(message: Message):
    userCommandContexts[message.from_user.id] = {}
    user = message.from_user
    await message.answer(rf"Привет, {user.full_name}! Бот для управления месячными уведомлениями.")
    userInfo = notifyManager.GetUser(user.id)
    notifyLoader.Save(userInfo)

@dp.message(Command("list"))
async def list_notifications(message: Message):
    userInfo = notifyManager.GetUser(message.from_user.id)
    buttons = []
    for notify_id, notify in userInfo.notifies.items():
        notifyDay = ""
        if notify.day.isdigit():
            notifyDay = notify.day
        else:
            weekday = DateUtils.ConvertWeekDayEnToRu(notify.day)
            if weekday is None:
                notifyDay = "???"
            else:
                notifyDay = weekday
        buttons.append(InlineKeyboardButton(text=f"{notifyDay} | {notify.hour:02d}:{notify.minute:02d} | {notify.text}", callback_data=f"notify.{notify_id}"))
    paginator = KeyboardPaginator(
        data=buttons,
        router=router,
        per_page=5,
        per_row=1
    )

    await message.answer(text="list", reply_markup=paginator.as_markup())

@dp.message(Command("add"))
async def add_notification(message: Message):
    user_id = message.from_user.id
    userCommandContexts[user_id] = {}
    userInfo = notifyManager.GetUser(user_id)
    notify = Notify(str(uuid.uuid4()), "1", 12, 0, "Новое", None)
    userInfo.notifies[notify.notify_id] = notify
    notifyLoader.Save(userInfo)

@dp.message(Command("add_template"))
async def add_notification_via_template(message: Message):
    user_id = message.from_user.id
    userCommandContexts[user_id] = {}
    templateList = templateLoader.GetTemplates()
    buttons = []
    for template_id, template in templateList.templates.items():
        buttons.append(InlineKeyboardButton(text=f"{template.day} | {template.hour:02d}:{template.minute:02d} | {template.text}", callback_data=f"template.{template_id}"))
    paginator = KeyboardPaginator(
        data=buttons,
        router=router,
        per_page=5,
        per_row=1
    )

    await message.answer(text="Шаблоны", reply_markup=paginator.as_markup())

@dp.message(Command("cancel"))
async def list_notifications(message: Message):
    userCommandContexts[message.from_user.id] = {}

@dp.message()
async def text_handler(message: Message):
    if message.text is None:
        await message.answer(text="Стикеры не поддерживаются. Введите текст.")
        return
    user_id = message.from_user.id
    if not user_id in userCommandContexts:
        return
    userCommandCtx: UserCommandContext
    userCommandCtx = userCommandContexts[user_id]
    del userCommandContexts[user_id]
    if not userCommandCtx.waitCommand in ["day", "time", "text"]:
        return
    userInfo: UserInfo
    userInfo = notifyManager.GetUser(user_id)
    if userInfo is None:
        await message.answer(text="Не нашел такого пользователя.")
        return
    notifyInfo: Notify
    notifyInfo = userInfo.notifies[userCommandCtx.notify_id]
    if notifyInfo is None:
        await message.answer(text="Не нашел такое уведомление пользователя.")
        return
    if userCommandCtx.waitCommand == "day":
        dayStr = message.text.lower()
        if dayStr.isdigit():
            notifyInfo.day = dayStr
            notifyInfo.lastSentDate = None
        else:
            weekday = DateUtils.ConvertWeekDayRuToEn(dayStr)
            if weekday is None:
                await message.answer(text=f"Не понял ваш ответ {message.text}. Формат дня: 1-31, е, пн, вт, ср, чт, пт, сб, вс")
                return
            else:
                notifyInfo.day = weekday
                notifyInfo.lastSentDate = None
    elif userCommandCtx.waitCommand == "time":
        splittedText = message.text.split(":")
        notifyInfo.hour = int(splittedText[0])
        notifyInfo.minute = int(splittedText[1])
        notifyInfo.lastSentDate = None
    elif userCommandCtx.waitCommand == "text":
        notifyInfo.text = message.text
    notifyLoader.Save(userInfo)

@dp.callback_query(lambda c: "template." in c.data)
async def add_template_as_notify(callback_query: types.CallbackQuery):
    splittedData = callback_query.data.split(".")
    template_id = splittedData[1]
    userInfo = notifyManager.GetUser(callback_query.from_user.id)
    await callback_query.answer()
    template: Template
    template = templateLoader.GetTemplates().templates[template_id]
    notify = Notify(str(uuid.uuid4()), template.day, template.hour, template.minute, template.text, None)
    userInfo.notifies[notify.notify_id] = notify
    notifyLoader.Save(userInfo)
    await callback_query.message.answer("Добавлено")

@dp.callback_query(lambda c: "notify." in c.data)
async def edit_notify(callback_query: types.CallbackQuery):
    splittedData = callback_query.data.split(".")
    notify_id = splittedData[1]
    userInfo = notifyManager.GetUser(callback_query.from_user.id)
    notify = userInfo.notifies[notify_id]
    await callback_query.answer()
    notifyDay = ""
    if notify.day.isdigit():
        notifyDay = notify.day
    else:
        weekday = DateUtils.ConvertWeekDayEnToRu(notify.day)
        if weekday is None:
            notifyDay = "???"
        else:
            notifyDay = weekday

    editBuilder = InlineKeyboardBuilder()
    editBuilder.row(
        InlineKeyboardButton(text=f"День: {notifyDay}", callback_data=f"edit.day.{notify_id}"),
        InlineKeyboardButton(text=f"Время: {notify.hour:02d}:{notify.minute:02d}", callback_data=f"edit.time.{notify_id}"),
    )
    editBuilder.row(
        InlineKeyboardButton(text=f"Текст: {notify.text}", callback_data=f"edit.text.{notify_id}"),
        InlineKeyboardButton(text="Удалить", callback_data=f"edit.delete.{notify_id}"),
    )
    lastDateInfo = ""
    if not notify.lastSentDate is None:
        lastDateInfo = f"Было отправлено {notify.lastSentDate.year}.{notify.lastSentDate.month}.{notify.lastSentDate.day}"

    await callback_query.message.answer(f"Редактирование.{lastDateInfo}", reply_markup=editBuilder.as_markup())

@dp.callback_query(lambda c: "edit.day" in c.data)
async def edit_day(callback_query: types.CallbackQuery):
    splittedData = callback_query.data.split(".")
    notify_id = splittedData[2]
    user_id = callback_query.from_user.id
    userCommandCtx = UserCommandContext(user_id, notify_id, "day")
    userCommandContexts[user_id] = userCommandCtx

    await callback_query.answer()
    await callback_query.message.answer("Введите новое значение дня.\nФормат: 1-31, е, пн, вт, ср, чт, пт, сб, вс.")

@dp.callback_query(lambda c: "edit.time" in c.data)
async def edit_time(callback_query: types.CallbackQuery):
    splittedData = callback_query.data.split(".")
    notify_id = splittedData[2]
    user_id = callback_query.from_user.id
    userCommandCtx = UserCommandContext(user_id, notify_id, "time")
    userCommandContexts[user_id] = userCommandCtx

    await callback_query.answer()
    await callback_query.message.answer("Введите новое значение времени.\nФормат чч:мм.")

@dp.callback_query(lambda c: "edit.text" in c.data)
async def edit_text(callback_query: types.CallbackQuery):
    splittedData = callback_query.data.split(".")
    notify_id = splittedData[2]
    user_id = callback_query.from_user.id
    userCommandCtx = UserCommandContext(user_id, notify_id, "text")
    userCommandContexts[user_id] = userCommandCtx

    await callback_query.answer()
    await callback_query.message.answer("Введите новое значение текста")

@dp.callback_query(lambda c: "edit.delete" in c.data)
async def edit_delete(callback_query: types.CallbackQuery):
    splittedData = callback_query.data.split(".")
    notify_id = splittedData[2]
    user_id = callback_query.from_user.id
    if user_id in userCommandContexts:
        del userCommandContexts[user_id]
    userInfo = notifyManager.GetUser(user_id)
    if notify_id in userInfo.notifies:
        del userInfo.notifies[notify_id]
        notifyLoader.Save(userInfo)

    await callback_query.answer()
    await callback_query.message.answer("Удалено")

async def timerFunc(bot: Bot):
    while True:
        await check_and_send_notifications(bot)
        await asyncio.sleep(60)

async def check_and_send_notifications(bot: Bot):
    now = datetime.now()
    current_hour = int(now.strftime("%H"))
    current_minute = int(now.strftime("%M"))

    users = notifyManager.GetUsers()
    for user_id, user in users.items():
        apply = False
        for notify_id, notification in user.notifies.items():
            if notification.day.isdigit():
                notification_day = int(notification.day)
                if notification_day != now.day:
                    continue
            else:
                if notification.day != DateUtils.EveryDay():
                    weekday = DateUtils.DayStrToNumberEn(notification.day)
                    if weekday != now.weekday():
                        continue

            if notification.lastSentDate != None:
                if notification.lastSentDate.year == now.year and notification.lastSentDate.month == now.month and notification.lastSentDate.day == now.day:
                    continue
            if current_hour > notification.hour or (current_hour == notification.hour and current_minute >= notification.minute):
                await bot.send_message(chat_id=user_id, text=notification.text)
                apply = True
                notification.lastSentDate = SentDate(now.year, now.month, now.day, now.weekday())
        if apply:
            notifyLoader.Save(user)

async def main() -> None:
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if BOT_TOKEN is None:
        print("Please add file .env with field BOT_TOKEN.")
        return
    print("Found bot token and begun work.")
    global bot
    bot = Bot(token=BOT_TOKEN)
    commands = [
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/add", description="Добавить уведомление"),
        BotCommand(command="/list", description="Получить список уведомлений (удалить, править)"),
        BotCommand(command="/add_template", description="Добавить уведомление из шаблона"),
        BotCommand(command="/cancel", description="Отменить ожидание ввода"),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
    dp.include_router(router)
    await asyncio.gather(asyncio.create_task(timerFunc(bot)), dp.start_polling(bot))

# @MonthNotifyBot
if __name__ == "__main__":
    templateLoader.Setup("./Templates.json")
    templateLoader.LoadAll()
    notifyLoader.Setup("../NotifyBotData")
    notifyManager.SetUsers(notifyLoader.LoadAll())

    asyncio.run(main())
