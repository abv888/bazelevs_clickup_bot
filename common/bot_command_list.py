from aiogram.types import BotCommand

private = [
    BotCommand(
        command='start',
        description='Запустить бота'
    ),
    BotCommand(
        command='help',
        description='Помощь'
    ),
    BotCommand(
            command='tasks',
            description='Получить список задач'
        ),
    BotCommand(
                command='overdued_tasks',
                description='Получить список просроченных задач'
            ),
    BotCommand(
                command='tasks_day',
                description='Получить список задач на день'
            ),
    BotCommand(
                command='tasks_week',
                description='Получить список задач на неделю'
            ),
    BotCommand(
                command='meetings',
                description='Получить список встреч'
            ),
    BotCommand(
                    command='contract_report',
                    description='Получить список встреч чтобы заполнить репорты'
                )
]
