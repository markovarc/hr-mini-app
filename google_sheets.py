import os
import json
import gspread
from google.oauth2.service_account import Credentials

scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Загружаем JSON-ключ из переменной окружения
json_key = os.environ.get("CLIENT_SECRET_JSON")
info = json.loads(json_key)

# Авторизация с помощью google-auth
creds = Credentials.from_service_account_info(info, scopes=scope)
client = gspread.authorize(creds)

# Подключение к таблицам
sheet_all = client.open("HR-All-Applications").sheet1
sheet_approved = client.open("HR-Approved-Only").sheet1

def add_to_all(data: list):
    sheet_all.append_row(data)

def add_to_approved(data: list):
    sheet_approved.append_row(data)
