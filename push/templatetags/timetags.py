import datetime

from django import template


register = template.Library()


def print_api_timestamp(timestamp):
    # API sends timestamps in e notation
    ts = timestamp/1000000000
    try:
        ts = float(ts)
    except ValueError:
        return None
    return datetime.datetime.fromtimestamp(ts)

register.filter(print_api_timestamp)
