from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView, status
from bs4 import BeautifulSoup
from bot_helper.utils import get_sheet_from_gsheets
import requests


class DiscountsView(APIView):
    def get(self, request, *args, **kwargs):
        page = requests.get("https://student.itmo.ru/ru/discounts/")
        if page.status_code != 200:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        soup = BeautifulSoup(page.text, "html.parser")
        discounts = soup.findAll('div', class_='card')
        response = []
        for discount in discounts:
            title = discount.find('h5', class_="card__info-heading")
            desc = discount.find('div', class_="card__info-text")
            title = title.text
            desc = desc.text
            title = title.replace("  ", "")
            title = title.replace("\n", "")
            desc = desc.replace("  ", "")
            desc = desc.replace("\n", "")
            response.append({"title": title, "desc": desc})
        return Response(response)


class SearchDiscount(APIView):
    def get(self, request, *args, **kwargs):
        if request.query_params:
            result = get_sheet_from_gsheets("discounts")[1]
            category = request.query_params.get('category')
            campus = request.query_params.get('campus')
            if campus:
                result = result[result["campus"] == campus]
            if category:
                result = result[result["category"] == category]
            result = result.drop_duplicates()
            return Response(result.to_dict(orient='records'))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SpreadsheetFilter(APIView):
    def get(self, request, sheet, *args, **kwargs):
        result = get_sheet_from_gsheets(sheet)[1]
        for param, value in request.query_params.items():
            try:
                if value[0] == "!":
                    value = value[1:]
                    result = result[result[param] != value]
                else:
                    result = result[result[param] == value]
            except KeyError:
                continue
        result = result.drop_duplicates()
        return Response(result.to_dict(orient='records'))
