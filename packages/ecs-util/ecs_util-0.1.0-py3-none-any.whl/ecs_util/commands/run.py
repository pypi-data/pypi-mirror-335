import logging

import click

from ecs_util.aws.ecs import ECSService

logging.basicConfig(level=logging.INFO)


@click.command()
@click.argument("command", nargs=-1)
@click.pass_context
def run(ctx, command):
    app_config = ctx.obj["config"].app
    ecs_service = ECSService(
        cluster_arn=app_config.cluster_arn, service_name=app_config.web_service_name
    )
    task = ecs_service.run_task(
        task_definition=app_config.web_task_definition_name,
        container_name=app_config.run_task_container_name,
        command=command,
    )
    task.wait()
