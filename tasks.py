from celery import shared_task

@shared_task(ignore_result=False)
def shared_url():
    return "user shared url"