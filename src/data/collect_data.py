import gspread
from google.oauth2.service_account import Credentials
from src.utils import SPREADSHEET_ID
import pandas as pd

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

try:
    creds = Credentials.from_service_account_file(r'src/data/credentials.json', scopes=SCOPES)
except:
    creds = Credentials.from_service_account_file(r'../src/data/credentials.json', scopes=SCOPES)
client = gspread.authorize(creds)

def read_google_spreadsheet(sheet_name):
    # Definir el libro
    workbook = client.open_by_key(SPREADSHEET_ID)
    # Definir la hoja
    sheet = workbook.worksheet(sheet_name)
    # Convertir los registros en un dataframe
    df = pd.DataFrame(sheet.get_all_records())
    return df
