from __future__ import annotations

import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Callable

from app.models import DeliveryLog, NotificationTarget, Report
from app.notifications.base import NotificationProvider


class SMTPConfigError(RuntimeError):
    pass


class EmailNotificationProvider(NotificationProvider):
    provider_id = "smtp_email"

    def __init__(
        self,
        *,
        smtp_factory: Callable[..., smtplib.SMTP] | Callable[..., smtplib.SMTP_SSL] | None = None,
    ) -> None:
        self.host = os.getenv("SMTP_HOST", "smtp.qq.com")
        self.port = int(os.getenv("SMTP_PORT", "465"))
        self.use_ssl = _bool(os.getenv("SMTP_USE_SSL", "true"))
        self.username = os.getenv("SMTP_USERNAME", "")
        self.password = os.getenv("SMTP_PASSWORD", "")
        self.sender = os.getenv("SMTP_FROM", self.username)
        self.sender_name = os.getenv("SMTP_FROM_NAME", "SgodAI Market Radar")
        self.timeout = int(os.getenv("SMTP_TIMEOUT_SECONDS", "20"))
        self.smtp_factory = smtp_factory

    def send_report(self, target: NotificationTarget, report: Report) -> DeliveryLog:
        subject = f"{report.title} · {report.report_type}"
        body = self._report_body(report)
        return self.send_message(target, subject=subject, body=body, report_id=report.id)

    def send_test(self, target: NotificationTarget) -> DeliveryLog:
        now = datetime.now(timezone.utc).isoformat()
        body = (
            "SgodAI Market Radar 测试邮件发送成功。\n\n"
            f"目标：{target.name} <{target.address_or_endpoint}>\n"
            f"时间：{now}\n\n"
            "本邮件仅用于验证 SMTP 配置与投递链路，不构成投资建议。"
        )
        return self.send_message(target, subject="SgodAI Market Radar 测试邮件", body=body)

    def retry_failed(self, delivery_log_id: str) -> DeliveryLog:
        return DeliveryLog(
            id=f"retry_{delivery_log_id}",
            target_id="unknown",
            channel="email",
            status="failed",
            retry_count=1,
            error_message="retry requires persisted target payload; not implemented in MVP",
            sent_at=datetime.now(timezone.utc),
        )

    def send_message(
        self,
        target: NotificationTarget,
        *,
        subject: str,
        body: str,
        report_id: str | None = None,
        alert_id: str | None = None,
    ) -> DeliveryLog:
        try:
            self._validate_config()
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender}>"
            message["To"] = target.address_or_endpoint
            message.set_content(body)
            self._send(message)
            return self._log(target, "success", report_id=report_id, alert_id=alert_id)
        except Exception as exc:  # noqa: BLE001
            return self._log(
                target,
                "failed",
                report_id=report_id,
                alert_id=alert_id,
                error_message=str(exc),
            )

    def _send(self, message: EmailMessage) -> None:
        if self.smtp_factory is not None:
            server = self.smtp_factory(self.host, self.port, timeout=self.timeout)
        elif self.use_ssl:
            server = smtplib.SMTP_SSL(
                self.host,
                self.port,
                timeout=self.timeout,
                context=ssl.create_default_context(),
            )
        else:
            server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
        with server as smtp:
            if not self.use_ssl:
                smtp.starttls(context=ssl.create_default_context())
            smtp.login(self.username, self.password)
            smtp.send_message(message)

    def _validate_config(self) -> None:
        missing = [
            key
            for key, value in {
                "SMTP_HOST": self.host,
                "SMTP_USERNAME": self.username,
                "SMTP_PASSWORD": self.password,
                "SMTP_FROM": self.sender,
            }.items()
            if not value
        ]
        if missing:
            raise SMTPConfigError(f"SMTP 配置缺失：{', '.join(missing)}")

    @staticmethod
    def _report_body(report: Report) -> str:
        return (
            f"{report.title}\n\n"
            f"报告类型：{report.report_type}\n"
            f"区间：{report.period_start.isoformat()} ~ {report.period_end.isoformat()}\n"
            f"事件数量：{len(report.event_ids)}\n"
            f"信号数量：{len(report.signal_ids)}\n\n"
            f"{report.disclaimer}"
        )

    @staticmethod
    def _log(
        target: NotificationTarget,
        status: str,
        *,
        report_id: str | None = None,
        alert_id: str | None = None,
        error_message: str | None = None,
    ) -> DeliveryLog:
        timestamp = datetime.now(timezone.utc)
        return DeliveryLog(
            id=f"dlv_{int(timestamp.timestamp() * 1000)}",
            target_id=target.id,
            channel="email",
            status=status,
            report_id=report_id,
            alert_id=alert_id,
            retry_count=0,
            error_message=error_message,
            sent_at=timestamp,
        )


def _bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}
