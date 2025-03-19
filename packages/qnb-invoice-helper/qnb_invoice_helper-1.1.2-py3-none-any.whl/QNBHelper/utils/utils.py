


import datetime


def edm_action_date(datetime: datetime.datetime) -> str:
    return datetime.strftime("%Y-%m-%dT%H:%M:%S")