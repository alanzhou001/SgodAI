from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import DeliveryLog, NotificationTarget, Report


class NotificationProvider(ABC):
    provider_id: str

    @abstractmethod
    def send_report(self, target: NotificationTarget, report: Report) -> DeliveryLog:
        raise NotImplementedError

    @abstractmethod
    def send_test(self, target: NotificationTarget) -> DeliveryLog:
        raise NotImplementedError

    @abstractmethod
    def retry_failed(self, delivery_log_id: str) -> DeliveryLog:
        raise NotImplementedError

