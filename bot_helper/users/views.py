from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView, status
import users.serializers as serializers
import users.models as models


class UserView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        user = get_object_or_404(models.User, alice_user_id=request.data["alice_user_id"])
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        print(request.data)
        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        models.User.objects.all().delete()
        return Response(status=status.HTTP_200_OK)
