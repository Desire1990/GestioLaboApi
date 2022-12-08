from django.db import connection, transaction, IntegrityError
from datetime import datetime, timedelta, date
from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework import status
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from rest_framework import viewsets, generics, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
# third party
from collections import OrderedDict
from rest_framework import viewsets, filters
from .models import *
from .serializers import *
from .permissions import *
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
transaction
# for sending emails

from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail  
from django.db.models import Q
