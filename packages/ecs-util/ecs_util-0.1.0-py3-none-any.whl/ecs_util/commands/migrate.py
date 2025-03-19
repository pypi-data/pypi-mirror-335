import logging

import click

from ecs_util.aws.ecs import ECSService

logging.basicConfig(level=logging.INFO)


@click.command()
@click.argument("task_definition")
@click.pass_context
def migrate(ctx, task_definition):
    app_config = ctx.obj["config"].app
    ecs_service = ECSService(
        cluster_arn=app_config.cluster_arn, service_name=app_config.web_service_name
    )
    task = ecs_service.run_task(
        task_definition=task_definition,
        container_name=app_config.run_task_container_name,
        command=["python", "manage.py", "migrate", "--noinput"],
    )
    task.wait()
