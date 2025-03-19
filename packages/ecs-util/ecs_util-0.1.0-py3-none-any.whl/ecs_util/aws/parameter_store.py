import boto3


class ParameterStore:
    def __init__(self):
        self.client = boto3.client("ssm")

    def get_parameter(self, key: str) -> str:
        response = self.client.get_parameter(Name=key, WithDecryption=True)
        return response["Parameter"]["Value"]

    def get_parameters(self, keys: list[str]) -> dict[str, str]:
        response = self.client.get_parameters(Names=keys)
        return {param["Name"]: param["Value"] for param in response["Parameters"]}

    def set_parameter(self, name: str, value: str):
        self.client.put_parameter(Name=name, Value=value, Type="String")
