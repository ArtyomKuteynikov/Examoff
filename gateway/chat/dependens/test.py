import time

from celery_module import generate_report_task

# To send the tasks for execution
generate_report_task.delay('arg1_value', 'arg2_value')

print(generate_report_task)
