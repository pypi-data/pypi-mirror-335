import boto3


class EventBridgeSchedule:
    def __init__(self, schedule_name: str):
        self.schedule_name = schedule_name
        self.client = boto3.client("scheduler")

    def update_task_definition(self, new_task_definition_arn: str):
        schedule = self.client.get_schedule(Name=self.schedule_name)
        target = schedule["Target"]
        task_definition_arn = target["EcsParameters"]["TaskDefinitionArn"]
        new_arn = task_definition_arn.split("/")
        new_arn[1] = new_task_definition_arn
        new_arn = "/".join(new_arn)
        target["EcsParameters"]["TaskDefinitionArn"] = new_arn
        self.client.update_schedule(
            Name=self.schedule_name,
            Target=target,
            FlexibleTimeWindow=schedule["FlexibleTimeWindow"],
            ScheduleExpression=schedule["ScheduleExpression"],
            Description=schedule["Description"],
        )
