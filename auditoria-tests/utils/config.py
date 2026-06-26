import os
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        self.base_url = self._require("BASE_URL")
        self.login_user = self._require("LOGIN_USER")
        self.login_password = self._require("LOGIN_PASSWORD")

    @staticmethod
    def _require(var_name: str) -> str:
        value = os.getenv(var_name)
        if not value:
            raise EnvironmentError(
                f"Variável de ambiente obrigatória não definida: {var_name}\n"
                f"Crie o arquivo .env com base em .env.example"
            )
        return value
