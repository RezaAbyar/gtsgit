import logging

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from .utils import string_assets, exception_helper
from .authentications import APIAuthentication


logger = logging.getLogger(__name__)


class CoreAPIView(APIView):
    authentication_classes = (APIAuthentication,)  # specify this authentication class in your view
    validator_serializer_class = None

    @classmethod
    def get_data(cls, data):
        if serializer_class := cls.validator_serializer_class:
            serializer: Serializer = serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            return serializer.validated_data
        return data

class BaseAPIView(APIView):
    validator_serializer_class = None

    @classmethod
    def get_data(cls, data):
        if serializer_class := cls.validator_serializer_class:
            serializer: Serializer = serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            return serializer.validated_data
        return data

