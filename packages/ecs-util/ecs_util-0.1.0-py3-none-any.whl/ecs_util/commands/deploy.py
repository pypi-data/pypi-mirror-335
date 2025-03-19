import logging

import click

from ecs_util.aws.ecs import ECSService
from ecs_util.aws.eventbridge import EventBridgeSchedule

logging.basicConfig(level=logging.INFO)


@click.command()
@click.argument("task_definition")
@click.pass_context
def deploy(ctx, task_definition):
    app_config = ctx.obj["config"].app
    logging.info(
        "Deploying Task Definition %s to %s",
        task_definition,
        app_config.web_service_name,
    )
    ecs_service = ECSService(
        cluster_arn=app_config.cluster_arn, service_name=app_config.web_service_name
    )
    ecs_service.update_task_definition(task_definition)

    for schedule_task in app_config.scheduled_tasks:
        schedule = EventBridgeSchedule(schedule_task)
        schedule.update_task_definition(task_definition)
