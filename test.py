# from clickupython import client
#
# API_KEY = 'pk_82679754_UJ6M844015UM2BEC43VL0FSGYTJLA1XB'
# client = client.ClickUpClient(API_KEY)
#
# team_name = client.get_teams().teams[0].name
# team_id = client.get_teams().teams[0].id
# # print(client.get_team_tasks(team_Id=team_id))
# print(client.default_space)
# for task in client.get_team_tasks(team_Id=team_id):
#     print(task.assignees)
# from datetime import datetime
#
# import requests
#
# api_token = 'pk_82679754_UJ6M844015UM2BEC43VL0FSGYTJLA1XB'
# list_id = '901500543364'
#
# headers = {
#     'Authorization': api_token,
# }
#
#
# # Функция для получения id assignee по user_id
# def get_user_id():
#     headers = {
#         'Authorization': api_token,
#     }
#     response = requests.get(f'https://api.clickup.com/api/v2/user', headers=headers)
#     if response.status_code == 200:
#         user = response.json()['user']
#         return user['id']
#     return None
#
# # После получения id assignee вы можете использовать его для получения списка задач
# # assignee_id = get_assignee_id(user_id)
# # if assignee_id:
# #     tasks = get_tasks(assignee_id)
# #     if tasks:
# #         # Обработка списка задач
# #     else:
# #         print("Ошибка при получении списка задач")
# # else:
# #     print("Ошибка при получении id assignee")
#
#
# user_id = get_user_id()
# print(user_id)
#
# # Получаем задачи, где вы являетесь исполнителем
# response = requests.get(f'https://api.clickup.com/api/v2/list/{list_id}/task?assignees[]={user_id}', headers=headers)
#
# if response.status_code == 200:
#     tasks = response.json()['tasks']
#     for task in tasks:
#         pass
#         print(task)
# else:
#     print(f"Ошибка: {response.status_code}")
#
#
# # Get overdue tasks
# def get_overdue_tasks(assignee_id):
#     headers = {
#         'Authorization': api_token,
#     }
#     response = requests.get(
#         f'https://api.clickup.com/api/v2/list/{list_id}/task?assignees[]={user_id}&due_date_lt={int(datetime.now().timestamp() * 1000)}',
#         headers=headers)
#     if response.status_code == 200:
#         return response.json()['tasks']
#     else:
#         return None
#
#
# def send_overdue_tasks_reminder(user_id):
#     tasks = get_overdue_tasks(user_id)
#     if tasks:
#         message = f"У вас {len(tasks)} просроченных задач, пожалуйста, актуализируйте статус:\n"
#         for task in tasks:
#             task_link = f"https://app.clickup.com/t/{task['id']}"
#             message += f"- [{task['name']}]({task_link})\n"
#             print(task['assignees'])
#         print(message)
#
#
# send_overdue_tasks_reminder(user_id)
