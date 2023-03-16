import requests
from .settings import GOOGLE_SHEETS_DB_ID
import pandas as pd


def get_data_from_xlsx(sheet_name):
    df = pd.read_excel("gsheet.xlsx", sheet_name=sheet_name)
    return df

# def get_sheet_from_gsheets(sheet_name):
#     # link = f"https://tools.aimylogic.com/api/googlesheet2json?sheet={sheet_name}&id={GOOGLE_SHEETS_DB_ID}"
#     link = f"https://opensheet.elk.sh/{GOOGLE_SHEETS_DB_ID}/{sheet_name}"
#     response = requests.get(link).json()
#     return response, pd.DataFrame(response)
