from django.core.cache import cache


def is_user_online(user_chat_id):
    return cache.get(f'user_online_{user_chat_id}') is not None