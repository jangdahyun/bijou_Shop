import logging
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

logger = logging.getLogger("accounts.audit")

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    logger.info("로그인 성공: user=%s ip=%s", user.pk, request.META.get("REMOTE_ADDR"))

@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    logger.warning("로그인 실패: email=%s ip=%s", credentials.get("username"), request.META.get("REMOTE_ADDR"))