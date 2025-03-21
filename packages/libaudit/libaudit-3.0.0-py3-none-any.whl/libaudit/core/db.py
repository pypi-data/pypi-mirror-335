from typing import Any
from typing import Union

from django.db import connection


def set_db_param(key, value):
    """Устанавливает параметры в настройках БД."""
    cursor = connection.cursor()
    value = f'{value}' if value else ''
    cursor.execute('SELECT set_config(%s, %s, False);', (key, value))


def set_db_params(**params):
    """Устанавливает параметры сеанса."""
    for name, value in params.items():
        set_db_param(name, value)


def get_db_param(key) -> Union[Any, None]:
    """Получить параметр сеанса по имени."""
    cursor = connection.cursor()
    cursor.execute('SELECT current_setting(%s, true);', (key,))
    if result := cursor.fetchone():
        return result[0]
