import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

json_key = os.environ.get("CLIENT_SECRET_JSON")
info = json.loads(json_key)
creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
client = gspread.authorize(creds)

sheet_all = client.open("HR-All-Applications").sheet1
sheet_approved = client.open("HR-Approved-Only").sheet1

def add_to_all(data: list):
    sheet_all.append_row(data)

def add_to_approved(data: list):
    sheet_approved.append_row(data)
