import logging

import click

from ecs_util.aws.ecs import ECSTaskDefinition

logging.basicConfig(level=logging.INFO)


@click.command
@click.argument("image")
@click.pass_context
def create_task_definition(ctx, image):
    app_config = ctx.obj["config"].app
    logging.info(
        "Creating new Task Definition based on %s",
        app_config.web_task_definition_template_name,
    )
    task_definition = ECSTaskDefinition.from_name(app_config.web_task_definition_template_name)
    task_definition.update_family(app_config.web_task_definition_name)
    task_definition.update_image(app_config.web_container_name, image)
    task_definition.set_environment_variable(app_config.web_container_name, "TASK_IMAGE", image)
    task_definition_arn = task_definition.register_task_definition()
    click.echo(task_definition_arn)
