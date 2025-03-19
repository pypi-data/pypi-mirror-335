import json

import boto3

from ecs_util.aws.parameter_store import ParameterStore


class ECSTask:
    """Wraps ECS run_task allowing for waiting on the task to complete"""

    def __init__(self, *, cluster: str, **kwargs):
        self.task_kwargs = kwargs
        self.cluster = cluster
        self.ecs = boto3.client("ecs")
        self.task_arn = None

    def run(self) -> "ECSTask":
        response = self.ecs.run_task(cluster=self.cluster, **self.task_kwargs)
        task_arn = response["tasks"][0]["taskArn"]
        self.task_arn = task_arn
        return self

    def wait(self):
        if not self.task_arn:
            raise ValueError("Can't wait for a task until run() has been executed")

        waiter = self.ecs.get_waiter("tasks_running")
        waiter.wait(
            cluster=self.cluster,
            tasks=[self.task_arn],
        )


class ECSTaskDefinition:
    """
    Simple wrapper around a Task Definition providing tools to update and
    register updated versions
    """

    def __init__(self, task_definition: dict):
        self.task_definition = task_definition
        self.client = boto3.client("ecs")

    @classmethod
    def from_name(cls, name: str) -> "ECSTaskDefinition":
        """
        Given a task definition name, return an instance of this class wrapping
        a 'copy' of that task definition.

        AWS returns various metadata fields that are stripped out at this point as
        they aren't used when registering a new definition.
        """
        client = boto3.client("ecs")
        response = client.describe_task_definition(taskDefinition=name)
        task_definition = response["taskDefinition"]
        for key in [
            "taskDefinitionArn",
            "registeredBy",
            "registeredAt",
            "compatibilities",
            "requiresAttributes",
            "status",
            "revision",
        ]:
            task_definition.pop(key)
        return cls(task_definition)

    def register_task_definition(self) -> str:
        """Register this task definition with AWS. Not idempotent."""
        response = self.client.register_task_definition(**self.task_definition)
        task_arn = response["taskDefinition"]["taskDefinitionArn"]
        task_name = task_arn.split("/")[-1]
        return task_name

    def update_image(self, container_name: str, new_image: str):
        """Update the image used for the given container name"""
        for idx, container_definition in enumerate(self.task_definition["containerDefinitions"]):
            if container_definition["name"] == container_name:
                self.task_definition["containerDefinitions"][idx]["image"] = new_image

    def update_family(self, family: str):
        """Update the family name for this definition"""
        self.task_definition["family"] = family

    def set_environment_variable(self, container_name: str, key: str, value: str):
        """Set an environment variable to the given value"""
        for idx, container_definition in enumerate(self.task_definition["containerDefinitions"]):
            if container_definition["name"] == container_name:
                # Check if the environment variable already exists, update it if it does
                for var_idx, var in enumerate(container_definition["environment"]):
                    if var["name"] == key:
                        self.task_definition["containerDefinitions"][idx]["environment"][var_idx][
                            "value"
                        ] = value
                        return

                # Otherwise create it as a new variable
                self.task_definition["containerDefinitions"][idx]["environment"].append(
                    {"name": key, "value": value}
                )


class ECSAgent:
    """Wrapper exposing some utility methods for interacting with the custom ECS Agent container"""

    def __init__(self, *, app_name: str):
        self.ssm = boto3.client("ssm")
        self.ecs = boto3.client("ecs")
        self.app_name = app_name
        self.cluster_arn = self.get_parameter("cluster-arn")
        self.task_definition = self.get_parameter("task-definition-name")

    def get_parameter(self, key: str) -> str:
        parameter_store = ParameterStore()
        return parameter_store.get_parameter(f"{self.app_name}/ecs-agent/{key}")

    def run_task(
        self,
        *,
        command: list[str],
    ) -> ECSTask:
        """Run a task on this cluster"""
        run_task_parameters = json.loads(self.get_parameter("run-task-parameters"))
        ecs_task = ECSTask(
            cluster=self.cluster_arn,
            taskDefinition=self.task_definition,
            overrides={
                "containerOverrides": [
                    {
                        "name": "agent",
                        "command": command,
                    }
                ]
            },
            **run_task_parameters,
        )

        return ecs_task.run()


class ECSService:
    """Simple wrapper around an ECS Service exposing some utility methods for
    taking actions on the service."""

    def __init__(self, *, cluster_arn: str, service_name: str):
        self.cluster_arn = cluster_arn
        self.service_name = service_name
        self.client = boto3.client("ecs")

    def update_task_definition(self, task_definition: str):
        """Update this service to use the given task definition"""
        self.client.update_service(
            cluster=self.cluster_arn,
            service=self.service_name,
            taskDefinition=task_definition,
            forceNewDeployment=True,
        )

    def get_service(self) -> dict:
        """Get the full service object from AWS"""
        service = self.client.describe_services(
            cluster=self.cluster_arn,
            services=[
                self.service_name,
            ],
        )["services"][0]
        return service

    def get_active_tasks(self) -> list[str]:
        """Get all running tasks for this service and return a list of ARNs"""
        return self.client.list_tasks(
            cluster=self.cluster_arn,
            serviceName=self.service_name,
            desiredStatus="RUNNING",
        )["taskArns"]

    def run_task(
        self,
        *,
        task_definition: str,
        container_name: str,
        command: list[str],
    ) -> ECSTask:
        """Run a task on the same cluster as this service, cloning the configuration
        of the most recent deployment."""
        service = self.get_service()
        latest_deployment = service["deployments"][0]
        capacity_provider_strategy = latest_deployment["capacityProviderStrategy"]
        network_configuration = latest_deployment["networkConfiguration"]

        ecs_task = ECSTask(
            cluster=self.cluster_arn,
            taskDefinition=task_definition,
            capacityProviderStrategy=capacity_provider_strategy,
            networkConfiguration=network_configuration,
            overrides={
                "containerOverrides": [
                    {
                        "name": container_name,
                        "command": command,
                    }
                ]
            },
        )
        return ecs_task.run()
