import requests
from .settings import GOOGLE_SHEETS_DB_ID
import pandas as pd

GOOGLE_SHEET = {}


def load_gsheet():
    print("LOADING GSHEET")
    # table = pd.ExcelFile("https://docs.google.com/spreadsheets/d/e/2PACX-1vTdjHXPqt5EhUDVwAwaFT8LVvg7StCAHJL8JwJJWJktyHXoz0ncLkgMDIrsE2Nc_ImT2Rt2jDJeb0tO/pub?output=xlsx")
    table = pd.ExcelFile("data.xlsx")

    for sheet in table.sheet_names:
        GOOGLE_SHEET[sheet] = table.parse(sheet_name=sheet)
    return GOOGLE_SHEET

def get_data_from_xlsx(sheet_name):
    return GOOGLE_SHEET[sheet_name]


load_gsheet()