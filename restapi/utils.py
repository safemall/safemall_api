from django.core.cache import cache
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle


def is_user_online(user_chat_id):
    return cache.get(f'user_online_{user_chat_id}') is not None



class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 30

    def get_paginated_response(self, data, extra_data=None):
        response_data = {
            'count': self.count,
            'next': self.get_next_link(),
            'previous':  self.get_previous_link(),
            'results': data
        }

        if extra_data:
            response_data.update(extra_data)
        
        return Response(response_data)
    



class CustomThrottle(UserRateThrottle):
    rate = '10/min'  # override global rate for this view


class UploadCustomThrottle(UserRateThrottle):
    rate = '20/min'
