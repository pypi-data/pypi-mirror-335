import contextlib
import logging
import signal
import subprocess

import click

from ecs_util.aws.ecs import ECSService

logging.basicConfig(level=logging.INFO)


@contextlib.contextmanager
def ignore_user_entered_signals():
    """
    Ignores user entered signals to avoid process getting killed.

    Borrowed from https://github.com/hreeder/assh/issues/3#issuecomment-865436486
    """
    signal_list = [signal.SIGINT, signal.SIGQUIT, signal.SIGTSTP]
    actual_signals = []
    for user_signal in signal_list:
        actual_signals.append(signal.signal(user_signal, signal.SIG_IGN))
    try:
        yield
    finally:
        for sig, user_signal in enumerate(signal_list):
            signal.signal(user_signal, actual_signals[sig])


@click.command()
@click.pass_context
def exec(ctx):
    app_config = ctx.obj["config"].app
    ecs_service = ECSService(
        cluster_arn=app_config.cluster_arn,
        service_name=app_config.web_service_name,
    )
    task_arn = ecs_service.get_active_tasks()[0]
    with ignore_user_entered_signals():
        subprocess.run(
            (
                f"aws ecs execute-command --cluster {ecs_service.cluster_arn} --task"
                f" {task_arn} --container {app_config.run_task_container_name} --interactive"
                " --command /bin/bash"
            ),
            shell=True,
        )
