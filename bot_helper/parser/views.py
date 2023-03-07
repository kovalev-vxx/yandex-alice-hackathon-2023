from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView, status
from bs4 import BeautifulSoup
from bot_helper.utils import get_sheet_from_gsheets
import requests


class NewsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(get_sheet_from_gsheets("discounts")[0])


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
