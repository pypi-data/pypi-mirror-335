import os
from proton_driver import client
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo
from ..secret import SecretManager

timeplus_host = os.getenv("TIMEPLUS_HOST") or "localhost"
timeplus_user = os.getenv("TIMEPLUS_USER") or "proton"
timeplus_password = os.getenv("TIMEPLUS_PASSWORD") or "timeplus@t+"

config_stream_name = "agent_config"


class TimeplusAgentConfig:
    def __init__(self) -> None:
        self.secret_manager = SecretManager()
        self.client = client.Client(
            host=timeplus_host,
            user=timeplus_user,
            password=timeplus_password,
            port=8463,
        )
        self._create_config_stream()

    def _create_config_stream(self) -> None:
        try:
            self.client.execute(
                f"""CREATE MUTABLE STREAM IF NOT EXISTS {config_stream_name} (
                agent string,
                base_url string,
                api_key string,
                model string
            )
            PRIMARY KEY (agent)
            """
            )
        except Exception as e:
            print(e)

    def _update_config(self, agent: str, base_url: str, api_key: str, model: str):
        if agent is None or len(agent) == 0:
            print("agent is empty, skip config")
            return

        try:
            self.client.execute(
                f"INSERT INTO {config_stream_name} (agent, base_url, api_key, model) VALUES",
                [
                    [
                        agent,
                        base_url,
                        self.secret_manager.encrypt(api_key).decode(),
                        model,
                    ]
                ],
            )
        except Exception as e:
            print(e)

    def _get_config(self, agent: str) -> dict:
        result = {}
        result["base_url"] = os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        result["api_key"] = os.getenv("OPENAI_API_KEY")
        result["model"] = "gpt-4o"
        try:
            rows = self.client.execute_iter(
                f"SELECT base_url, api_key, model FROM table({config_stream_name}) WHERE agent = '{agent}'"
            )
            for row in rows:
                result["base_url"] = row[0]
                result["api_key"] = self.secret_manager.decrypt(row[1].encode())
                result["model"] = row[2]

            return result

        except Exception as e:
            print(e)

        return result

    def config(self, agent: str, base_url: str, api_key: str, model: str) -> None:
        self._update_config(agent, base_url, api_key, model)

    def get_client(self, agent: str) -> OpenAIChatCompletionClient:
        agent_config = self._get_config(agent)
        model_info = ModelInfo(
            family=agent_config["model"],
            function_calling=False,
            json_output=False,
            vision=False,
        )
        openai_model_client = OpenAIChatCompletionClient(
            model=agent_config["model"],
            base_url=agent_config["base_url"],
            api_key=agent_config["api_key"],
            model_info=model_info,
            temperature=0.0,
        )
        return openai_model_client
