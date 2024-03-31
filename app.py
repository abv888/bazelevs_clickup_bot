import asyncio
import os
from collections import defaultdict
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
import requests
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv, find_dotenv

from common.bot_command_list import private
from database.models import User
from middlewares.db import DataBaseSession

load_dotenv(find_dotenv())
from database.engine import drop_db, create_db, session_maker
from database.orm_query import orm_get_user, orm_add_user, orm_get_all_users

team_id = os.getenv("TEAM_ID")
meetings_id = os.getenv("MEETINGS_ID")
max_message_length = int(os.getenv("MAX_MESSAGE_LENGTH"))
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

session = session_maker()

def get_user_id(token):
    headers = {
        'Authorization': token,
    }
    response = requests.get(f'https://api.clickup.com/api/v2/user', headers=headers)
    if response.status_code == 200:
        user = response.json()['user']
        return user['id']
    return None


def get_all_tasks(token, assignee_id):
    headers = {
        'Authorization': token,
    }
    params = {
        # 'assignees[]': assignee_id
    }
    response = requests.get(f'https://api.clickup.com/api/v2/team/{team_id}/task', headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['tasks']
    else:
        return None


def get_today_tasks(token, assignee_id):
    headers = {
        'Authorization': token,
    }
    today_start = datetime.combine(datetime.today(), datetime.min.time())
    today_end = datetime.combine(datetime.today(), datetime.max.time())
    # Преобразуем в Unix time в миллисекундах
    today_start_unix = int(today_start.timestamp()) * 1000
    today_end_unix = int(today_end.timestamp()) * 1000
    # Формируем параметры запроса для фильтрации по дате и team_id
    params = {
        'due_date_gt': today_start_unix,
        'due_date_lt': today_end_unix
    }
    response = requests.get(f'https://api.clickup.com/api/v2/team/{team_id}/task', headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['tasks']
    else:
        print("ERRRRRRRR")
        return None


def get_tasks_for_week(token, assignee_id):
    headers = {
        'Authorization': token,
    }
    start_time = datetime.combine(datetime.today(), datetime.min.time())
    end_time = datetime.combine(start_time, datetime.max.time()) + timedelta(days=6)
    # Преобразуем время в Unix time в миллисекундах
    start_unix = int(start_time.timestamp()) * 1000
    end_unix = int(end_time.timestamp()) * 1000
    # Формируем параметры запроса для фильтрации по времени начала выполнения задачи
    params = {
        'due_date_gt': start_unix,
        'due_date_lt': end_unix,
        # 'assignees[]': assignee_id,
    }
    response = requests.get(f'https://api.clickup.com/api/v2/team/{team_id}/task', headers=headers, params=params)
    if response.status_code == 200:
        tasks = response.json()['tasks']
        # Группируем задачи по датам
        grouped_tasks = defaultdict(list)
        for task in tasks:
            if task['list']['id'] != meetings_id:
                due_date = datetime.fromtimestamp(int(task['due_date']) / 1000).date()
                grouped_tasks[due_date].append(task)
        return grouped_tasks
    else:
        return None


def get_meetings_for_week(token, assignee_id):
    headers = {
        'Authorization': token,
    }
    start_time = datetime.combine(datetime.today(), datetime.min.time())
    end_time = datetime.combine(start_time, datetime.max.time()) + timedelta(days=6)
    # Преобразуем время в Unix time в миллисекундах
    start_unix = int(start_time.timestamp()) * 1000
    end_unix = int(end_time.timestamp()) * 1000
    # Формируем параметры запроса для фильтрации по времени начала выполнения задачи
    params = {
        'due_date_gt': start_unix,
        'due_date_lt': end_unix,
        'list_ids[]': meetings_id,
        # 'assignees[]': assignee_id,
    }
    response = requests.get(f'https://api.clickup.com/api/v2/team/{team_id}/task', headers=headers, params=params)
    if response.status_code == 200:
        meetings = response.json()['tasks']
        # Группируем задачи по датам
        grouped_meetings = defaultdict(list)
        for meeting in meetings:
            due_date = datetime.fromtimestamp(int(meeting['due_date']) / 1000).date()
            grouped_meetings[due_date].append(meeting)
        return grouped_meetings
    else:
        return None


def get_overdue_tasks(token, assignee_id):
    headers = {
        'Authorization': token,
    }
    params = {
        'due_date_lt': int(datetime.now().timestamp() * 1000),
        # 'assignees[]': assignee_id,
    }
    response = requests.get(f'https://api.clickup.com/api/v2/team/{team_id}/task', headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['tasks']
    else:
        return None


def get_meetings(token, assignee_id):
    headers = {
        'Authorization': token,
    }
    params = {
        # 'assignees[]': assignee_id,
        'list_ids[]': meetings_id
    }
    response = requests.get(f'https://api.clickup.com/api/v2/team/{team_id}/task', headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['tasks']
    else:
        return None


def get_today_meetings(token, assignee_id):
    headers = {
        'Authorization': token,
    }
    today_start = datetime.combine(datetime.today(), datetime.min.time())
    today_end = datetime.combine(datetime.today(), datetime.max.time())
    # Преобразуем в Unix time в миллисекундах
    today_start_unix = int(today_start.timestamp()) * 1000
    today_end_unix = int(today_end.timestamp()) * 1000
    params = {
        'due_date_gt': today_start_unix,
        'due_date_lt': today_end_unix,
        # 'assignees[]': assignee_id,
        'list_ids[]': meetings_id
    }
    response = requests.get(f'https://api.clickup.com/api/v2/team/{team_id}/task', headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['tasks']
    else:
        return None


def format_task_message(task):
    formatted_due_date = "срок не указан"
    if task['due_date']:
        due_date = datetime.fromtimestamp(int(task['due_date']) / 1000)
        formatted_due_date = due_date.strftime('%d.%m.%Y')
    task_link = f"https://app.clickup.com/t/{task['id']}"
    return f"- [{task['name']}]({task_link}) - [{formatted_due_date}] \n"


def format_meeting_message(meeting):
    formatted_due_date = "срок не указан"
    if meeting['due_date']:
        due_date = datetime.fromtimestamp(int(meeting['due_date']) / 1000)
        formatted_due_date = due_date.strftime('%d.%m.%Y %H:%M')
    meeting_link = f"https://app.clickup.com/t/{meeting['id']}"
    return f"- [{meeting['name']}]({meeting_link}) - [{formatted_due_date}] \n"


def format_tasks_message(grouped_tasks):
    message = "Задачи на неделю:\n\n"
    today = datetime.today().date()
    for date, tasks in sorted(grouped_tasks.items()):
        if date == today:
            message += f"Сегодня:\n"
        elif date == today + timedelta(days=1):
            message += f"Завтра:\n"
        else:
            message += f"{date.strftime('%d.%m.%Y')}:\n"
        for task in tasks:
            task_link = f"https://app.clickup.com/t/{task['id']}"
            task_name = task['name']
            message += f"- [{task_name}]({task_link})\n"
        message += "\n"
        message += "\n"
    return message


def format_meetings_message(grouped_meetings):
    message = "Встречи на неделю:\n\n"
    today = datetime.today().date()
    for date, meetings in sorted(grouped_meetings.items()):
        if date == today:
            message += f"Сегодня:\n"
        elif date == today + timedelta(days=1):
            message += f"Завтра:\n"
        else:
            message += f"{date.strftime('%d.%m.%Y')}:\n"
        for meeting in meetings:
            formatted_due_date = "срок не указан"
            task_link = f"https://app.clickup.com/t/{meeting['id']}"
            task_name = meeting['name']
            if meeting['due_date']:
                due_date = datetime.fromtimestamp(int(meeting['due_date']) / 1000)
                formatted_due_date = due_date.strftime('%H:%M')
            message += f"- [{task_name}]({task_link}) - [{formatted_due_date}]\n"
        message += "\n"
        message += "\n"
    return message


async def send_tasks(user: User):
    tasks = get_all_tasks(token=user.clickup_api_token, assignee_id=user.clickup_id)
    if tasks:
        message = f"У вас {len(tasks)} задач:\n"
        for index, task in enumerate(tasks):
            message += format_task_message(task) + "\n"
            if index % 20 == 0 and index != 0:
                await bot.send_message(user.telegram_id, message, parse_mode="Markdown")
                message = ""
    else:
        await bot.send_message(user.telegram_id, "Нет задач")


async def send_meetings(user: User):
    meetings = get_meetings(token=user.clickup_api_token, assignee_id=user.clickup_id)
    if meetings:
        message = f"Запланировано встреч: {len(meetings)}\n"
        for meeting in meetings:
            print(meeting)
            message += format_meeting_message(meeting) + "\n"
        await bot.send_message(user.telegram_id, message, parse_mode="Markdown")
    else:
        await bot.send_message(user.telegram_id, "Нет встреч")


async def send_daily_meeting_report_notification(user: User):
    today_meetings = get_today_meetings(token=user.clickup_api_token, assignee_id=user.clickup_id)
    if today_meetings:
        message = f"Заполните контакт-репорты по встречам:\n"
        for meeting in today_meetings:
            meeting_link = f"https://app.clickup.com/t/{meeting['id']}"
            message += f"- [{meeting['name']}]({meeting_link})\n" + "\n"
        await bot.send_message(user.telegram_id, message, parse_mode="Markdown")
    else:
        pass


async def check_meetings_start():
    async with session:
        while True:
            all_users = await orm_get_all_users(session)
            if all_users:
                for user in all_users:
                    meetings = get_today_meetings(token=user.clickup_api_token, assignee_id=user.clickup_id)
                    if meetings:
                        now = datetime.now()
                        for meeting in meetings:
                            meeting_time = datetime.fromtimestamp(int(meeting['start_date']) / 1000)
                            if meeting_time - now <= timedelta(minutes=15):
                                if meeting_time - now == timedelta(minutes=0):
                                    await send_meeting_online_reminder(user_id=user.telegram_id, meeting=meeting)
                                else:
                                    await send_meeting_start_reminder(user_id=user.telegram_id, meeting=meeting)
                                    await asyncio.sleep((meeting_time - now).total_seconds())
                    else:
                        pass
            else:
                pass


async def send_meeting_start_reminder(user_id, meeting):
    meeting_link = f"https://app.clickup.com/t/{meeting['id']}"
    message = f"Через 15 минут начинается встреча [{meeting['name']}]({meeting_link})"
    await bot.send_message(user_id, message, parse_mode="Markdown")


async def send_meeting_online_reminder(user_id, meeting):
    meeting_link = f"https://app.clickup.com/t/{meeting['id']}"
    link = ""
    for custom_field in meeting['custom_fields']:
        if custom_field['name'] == "Ссылка или номер для подключения к звонку":
            link = custom_field['value']
    message = f"Встреча началась [{meeting['name']}]({meeting_link})\n" + f"Подключиться по ссылке: {link}"
    await bot.send_message(user_id, message, parse_mode="Markdown")


async def send_overdue_tasks_reminder(user: User):
    tasks = get_overdue_tasks(token=user.clickup_api_token, assignee_id=user.clickup_id)
    if tasks:
        message = f"У вас {len(tasks)} просроченных задач, пожалуйста, актуализируйте статус:\n"
        for task in tasks:
            # task_link = f"https://app.clickup.com/t/{task['id']}"
            message += format_task_message(task) + "\n"
        await bot.send_message(user.telegram_id, message, parse_mode="Markdown")
    else:
        await bot.send_message(user.telegram_id, "Нет просроченных задач")


async def send_today_tasks_reminder(user: User):
    tasks = get_today_tasks(token=user.clickup_api_token, assignee_id=user.clickup_id)
    if tasks:
        message = f"У вас {len(tasks)} задач на сегодня:\n"
        for task in tasks:
            task_link = f"https://app.clickup.com/t/{task['id']}"
            task_name = task['name']
            message += f"- [{task_name}]({task_link})\n"
        await bot.send_message(user.telegram_id, message, parse_mode="Markdown")
    else:
        await bot.send_message(user.telegram_id, "Нет задач на сегодня")


async def send_today_meetings_reminder(user: User):
    meetings = get_today_meetings(token=user.clickup_api_token, assignee_id=user.clickup_id)
    if meetings:
        message = f"У вас {len(meetings)} встреч на сегодня:\n"
        for meeting in meetings:
            meeting_link = f"https://app.clickup.com/t/{meeting['id']}"
            meeting_name = meeting['name']
            message += f"- [{meeting_name}]({meeting_link})\n"
        await bot.send_message(user.telegram_id, message, parse_mode="Markdown")
    else:
        await bot.send_message(user.telegram_id, "Сегодня нет встреч.")


async def send_daily_morning_notifications():
    async with session:
        all_users = await orm_get_all_users(session)
        if all_users:
            for user in all_users:
                if datetime.now().weekday() == 0:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=format_tasks_message(
                            get_tasks_for_week(
                                token=user.clickup_api_token,
                                assignee_id=user.clickup_id
                            )
                        ),
                        parse_mode="Markdown"
                    )
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=format_meetings_message(
                            get_meetings_for_week(
                                token=user.clickup_api_token,
                                assignee_id=user.clickup_id
                            )
                        ),
                        parse_mode="Markdown"
                    )
                else:
                    await send_today_tasks_reminder(user=user)
                    await send_today_meetings_reminder(user=user)
        else:
            pass


async def send_daily_evening_notifications():
    async with session:
        all_users = await orm_get_all_users(session)
        if all_users:
            for user in all_users:
                await send_overdue_tasks_reminder(user=user)
        else:
            pass


async def send_evening_meetings_report_notifications():
    async with session:
        all_users = await orm_get_all_users(session)
        if all_users:
            for user in all_users:
                await send_daily_meeting_report_notification(user=user)
        else:
            pass


@dp.message(Command('start'))
async def start_handler(message: types.Message, session: AsyncSession):
    user = await orm_get_user(session=session, user_id=message.from_user.id)
    if user:
        await message.answer("Добро пожаловать в бот. Вам доступен полный функционал")
    else:
        await message.answer("Нет доступа. Введите свой токен ClickUp API")


@dp.message(F.text.startswith('pk_'))
async def got_token_handler(message: types.Message, session: AsyncSession):
    clickup_id = get_user_id(message.text)
    if clickup_id:
        user = User(telegram_id=message.from_user.id, clickup_id=clickup_id, clickup_api_token=message.text)
        await orm_add_user(session=session, user=user)
        await message.answer("Добро пожаловать в бот. Вам доступен полный функционал")
    else:
        await message.answer("Ошибка авторизации. Неверный токен.")


@dp.message(Command('tasks'))
async def send_tasks_today_handler(message: types.Message, session: AsyncSession):
    user = await orm_get_user(session=session, user_id=message.from_user.id)
    if user:
        await send_tasks(user)
    else:
        await message.answer("Нет доступа.")


@dp.message(Command('tasks_week'))
async def send_tasks_week_handler(message: types.Message, session: AsyncSession):
    user = await orm_get_user(session=session, user_id=message.from_user.id)
    if user:
        await message.answer(
            format_tasks_message(get_tasks_for_week(token=user.clickup_api_token, assignee_id=user.clickup_id)),
            parse_mode="Markdown")
    else:
        await message.answer("Нет доступа.")


@dp.message(Command('overdued_tasks'))
async def send_tasks_overdue_handler(message: types.Message, session: AsyncSession):
    user = await orm_get_user(session=session, user_id=message.from_user.id)
    if user:
        # await send_tasks(user)
        await send_overdue_tasks_reminder(user)
    else:
        await message.answer("Нет доступа.")


@dp.message(Command('tasks_day'))
async def send_tasks_today_handler(message: types.Message, session: AsyncSession):
    user = await orm_get_user(session=session, user_id=message.from_user.id)
    if user:
        # await send_tasks(user)
        await send_today_tasks_reminder(user)
    else:
        await message.answer("Нет доступа.")


@dp.message(Command('meetings'))
async def send_meetings_handler(message: types.Message, session: AsyncSession):
    user = await orm_get_user(session=session, user_id=message.from_user.id)
    if user:
        await send_meetings(user=user)
    else:
        await message.answer("Нет доступа.")


@dp.message(Command('contract_report'))
async def send_daily_meeting_reports_handler(message: types.Message, session: AsyncSession):
    user = await orm_get_user(session=session, user_id=message.from_user.id)
    if user:
        await send_daily_meeting_report_notification(user)
    else:
        await message.answer("Нет доступа.")


async def on_startup(bot):
    scheduler.start()
    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    print('Bot shut down...')

scheduler = AsyncIOScheduler()
scheduler.add_job(send_daily_morning_notifications, "cron", day_of_week="mon-sun", hour=8, minute=0)
scheduler.add_job(send_daily_evening_notifications, "cron", day_of_week="mon-sun", hour=21, minute=0)
scheduler.add_job(send_evening_meetings_report_notifications, "cron", day_of_week="mon-sun", hour=22, minute=0)
# scheduler.add_job(check_meetings_start, 'interval', seconds=1)


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private)
    await dp.start_polling(bot)

asyncio.run(main())
