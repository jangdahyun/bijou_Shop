import logging
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib import messages


logger = logging.getLogger("accounts.audit")

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    logger.info("로그인 성공: user=%s ip=%s", user.pk, request.META.get("REMOTE_ADDR"))

    current_session_key = request.session.session_key
    user_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in user_sessions:
        data = session.get_decoded()
        if data.get("_auth_user_id") == str(user.pk) and session.session_key != current_session_key:
            session.delete()
            messages.error(request, "다른 기기에서의 로그인이 감지되어 해당 세션이 종료되었습니다.")

@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    logger.warning("로그인 실패: email=%s ip=%s", credentials.get("username"), request.META.get("REMOTE_ADDR"))