import logging
from datetime import datetime
from urllib.parse import urlparse

import boto3
import click

from ecs_util.aws.ecs import ECSAgent

logging.basicConfig(level=logging.INFO)


@click.command()
@click.option("--out", default="db.sql")
@click.pass_context
def db_snapshot(ctx, out):
    click.echo("Snapshotting database to S3...")
    dump_name = datetime.now().strftime("%Y%m%d-%H%M%S") + ".sql"
    environment = ctx.obj["environment"]
    ecs_agent = ECSAgent(app_name=environment.app_name)
    database_url = ecs_agent.get_parameter("database-url")
    s3_destination = ecs_agent.get_parameter("database-snapshot-s3-destination")
    full_s3_path = f"s3://{s3_destination}{dump_name}"
    ecs_agent.run_task(
        command=[
            "/agent/copy-db-to-s3.sh",
            "--database",
            database_url,
            "--destination",
            full_s3_path,
        ],
    ).wait()

    click.echo(f"Downloading snapshot to {out}...")
    parsed_destination = urlparse(full_s3_path)
    bucket = parsed_destination.netloc
    key = parsed_destination.path[1:]
    dump_object = boto3.resource("s3").Object(bucket, key)
    # Sometimes the file is not ready for download straight away.
    dump_object.wait_until_exists()
    dump_object.download_file(out)
