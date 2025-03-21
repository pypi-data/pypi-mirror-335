from rest_framework.fields import CharField
from rest_framework.fields import IntegerField
from rest_framework.fields import JSONField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer

from libaudit.core.types import OperationType
from libaudit.handlers.database_table.proxies import AuditLogViewProxy


class OperationSerializer(Serializer):
    """Сериалайзер данных об операции."""

    id = IntegerField(read_only=True, source='value')
    name = CharField(read_only=True, source='label')

    def to_representation(self, instance):  # noqa: D102
        return super().to_representation(instance)


class AuditLogSerializer(ModelSerializer):
    """Сериалайзер данных записи журнала изменений."""

    object_id = CharField(read_only=True, label='Код объекта')
    object_display = CharField(read_only=True, label='Строковое представление объекта')
    user_name = CharField(read_only=True, label='Организация пользователя')
    user_unit_name = CharField(read_only=True, label='Наименование организации пользователя')
    model_verbose_name = CharField(read_only=True, label='Модель объекта')
    diff = JSONField(read_only=True, label='Изменения')
    operation = OperationSerializer(read_only=True, label='Операция')

    def to_representation(self, instance):  # noqa: D102
        instance.operation = next(i for i in OperationType if i.value == instance.operation)
        return super().to_representation(instance)

    class Meta:  # noqa: D106
        model = AuditLogViewProxy
        fields = (
            'id',
            'object_id',
            'object_display',
            'model_verbose_name',
            'user_name',
            'user_unit_name',
            'diff',
            'user_id',
            'user_type_id',
            'user_unit_id',
            'user_unit_type_id',
            'timestamp',
            'table_name',
            'old_data',
            'changes',
            'operation',
            'request_id',
            'transaction_id',
            'ip_address',
        )
