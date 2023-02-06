import datetime

from celery import shared_task

from tradetracking.congressional_tracking import CongressionalData


@shared_task
def update_congressional_data():
    year = datetime.datetime.now().year
    method = CongressionalData()
    path = method.request_file(year)
    normalized_data = method.parse_xml(path)
    return method.send_congressional_data_to_db(normalized_data)
