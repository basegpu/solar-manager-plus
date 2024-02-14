from pydantic_settings import BaseSettings
from requests import get, Response
from typing import Any


class ApiConfig(BaseSettings):
    apiUrl: str = 'https://cloud.solar-manager.ch/v1'
    apiUser: str = ''
    apiPassword: str = ''

    @property
    def apiAuth(self) -> tuple[str, str]:
        return (self.apiUser, self.apiPassword)

    class Config:
        env_file = '.env'
        env_prefix = 'SOLARMANAGER_'


cfg = ApiConfig()


def get_call(route: str, params: dict[str, Any] = {}) -> Response:
    return get(f'{cfg.apiUrl}/{route}', params=params, auth=cfg.apiAuth)