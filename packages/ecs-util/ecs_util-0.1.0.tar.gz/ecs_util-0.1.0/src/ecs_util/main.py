import click

from ecs_util.commands import (
    create_task_definition,
    db_snapshot,
    deploy,
    exec,
    migrate,
    run,
)
from ecs_util.config import ConfigSchema


@click.group
@click.option("--app", type=click.STRING, required=True)
@click.pass_context
def cli(ctx, app):
    ctx.ensure_object(dict)
    ctx.obj["config"] = ConfigSchema.from_parameter_store(app)


cli.add_command(migrate)
cli.add_command(deploy)
cli.add_command(create_task_definition)
cli.add_command(exec)
cli.add_command(db_snapshot)
cli.add_command(run)

if __name__ == "__main__":
    cli()
