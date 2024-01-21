from datetime import datetime, date
from .models import Tag


def validate_due_date(due_date):
    format = "%Y-%m-%d"
    today = str(date.today().strftime(format))
    if datetime.strptime(due_date, format) < datetime.strptime(today, format):
        return today
    else:
        return due_date


def get_instance_with_tags(todo_instance, tags):
    new_todo_instance = todo_instance
    for tag in tags:
        tag, _ = Tag.objects.get_or_create(title=tag)
        new_todo_instance.tags.add(tag)
    return new_todo_instance
