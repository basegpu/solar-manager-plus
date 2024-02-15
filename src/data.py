import datetime as dt
from pydantic_settings import BaseSettings
from requests import get, Response
from typing import Any

from solar_manager.statistics import Statistics


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
    response = get(f'{cfg.apiUrl}/{route}', params=params, auth=cfg.apiAuth)
    response.raise_for_status()
    return response


def get_stats(sm_id: str, start: dt.datetime, end: dt.datetime) -> Statistics:
        data = get_call(
            f'statistics/gateways/{sm_id}',
            params={
                'accuracy': 'high',
                'from': start.isoformat(),
                'to': end.isoformat()})
        return Statistics(**data.json())