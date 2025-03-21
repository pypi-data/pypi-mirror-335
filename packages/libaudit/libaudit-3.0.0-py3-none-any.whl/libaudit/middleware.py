from typing import Type

from django.utils.deprecation import MiddlewareMixin

from libaudit.core import db
from libaudit.core.requests import AbstractAuditContextResolver
from libaudit.core.settings import get_context_resolver


class AuditLogMiddleware(MiddlewareMixin):
    """Извлекает из запроса и передаёт в контекст аудита дополнительную информацию."""

    @property
    def _audit_context_resolver(self) -> Type[AbstractAuditContextResolver]:
        return get_context_resolver()

    def process_request(self, request):
        """Добавляет в контекст аудита данные о запросе."""
        request._audit_context = self._audit_context_resolver.get_audit_context(request)
        db.set_db_params(**request._audit_context.dict())

    def process_response(self, request, response):
        """Обнуляет данные контекста аудита после обработки запроса."""
        request._audit_context = self._audit_context_resolver.get_audit_context()
        db.set_db_params(**request._audit_context.dict())
        return response
