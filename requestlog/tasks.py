from celery import shared_task


@shared_task
def delete_old_requestlog_entries(keep_days: int = 30):
    """
    Schedule this task with celery beat to clean up old log entries
    :param keep_days int   number of days to keep the entries
    """
    from requestlog.utils import delete_old_entries
    delete_old_entries(older_than_days=keep_days)
