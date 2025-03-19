from dataclasses import dataclass, field, fields

from ecs_util.aws.parameter_store import ParameterStore


@dataclass
class AppConfig:
    app_name: str = ""
    cluster_arn: str = ""
    web_service_name: str = ""
    web_task_definition_template_name: str = ""
    web_task_definition_name: str = ""
    web_container_name: str = ""
    run_task_container_name: str = ""
    scheduled_tasks: list[str] = field(default_factory=list)


@dataclass
class ConfigSchema:
    app: AppConfig

    @classmethod
    def from_parameter_store(cls, app_name: str):
        expected_keys = [field.name for field in fields(AppConfig)]
        expected_keys.remove("app_name")

        parameter_store = ParameterStore()
        keys = AppConfig.__annotations__.keys()
        prefixed_keys = [f"/{app_name}/{key}" for key in keys]
        parameters = parameter_store.get_parameters(prefixed_keys)
        unprefixed_parameters = {
            key.replace(f"/{app_name}/", ""): value for key, value in parameters.items()
        }

        # Find any keys that are in expected_keys but not in unprefixed_parameters
        missing_keys = set(expected_keys) - set(unprefixed_parameters.keys())
        if missing_keys:
            raise ValueError(f"Missing required parameters: {missing_keys}")

        scheduled_tasks = unprefixed_parameters.pop("scheduled_tasks")
        return ConfigSchema(
            app=AppConfig(
                app_name=app_name,
                **unprefixed_parameters,
                scheduled_tasks=scheduled_tasks.split(","),
            )
        )
