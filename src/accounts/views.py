import logging
import secrets
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.views.generic import FormView

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)

from .forms import (
    LoginForm,
    SignUpForm,
    VerificationForm,
    _hash_code,
    clear_signup_session,
    get_signup_session,
    save_signup_session,
)

# Django 기본 인증 뷰를 상속하여 커스터마이징
@method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True), name="dispatch")
class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    # 중복 로그인 방지
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("home")


class SignUpView(FormView):
    template_name = "accounts/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("home")

    @staticmethod
    def _form_initial_from_session(data):
        if not data:
            return None
        initial = data.copy()
        initial.pop("password1", None)
        initial.pop("password2", None)
        initial["terms_agreed"] = True
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("verification_form", VerificationForm())
        context.setdefault("show_verification", False)
        context.setdefault("verification_passed", False)
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action == "send_code":
            logger.debug("회원가입 POST - 인증번호 발송 요청 수신")
            return self.handle_send_code(request)
        elif action == "verify_code":
            logger.debug("회원가입 POST - 인증번호 검증 요청 수신")
            return self.handle_verify_code(request)
        elif action == "complete_signup":
            logger.debug("회원가입 POST - 가입 완료 요청 수신")
            return self.handle_complete_signup(request)
        return super().post(request, *args, **kwargs)
        
    def handle_send_code(self, request):
        form = SignUpForm(request.POST) 
        if not form.is_valid():
            logger.info("회원가입 폼 검증 실패: %s", form.errors)
            return self.render_to_response(self.get_context_data(form=form))
        code = f"{secrets.randbelow(1_000_000):06d}"
        logger.debug("인증번호 생성 완료 - email=%s", form.cleaned_data.get("email"))
        payload = {
            "data": form.to_session_payload(), 
            "code_hash": _hash_code(code),
            "expires": (timezone.now() + timedelta(minutes=5)).isoformat(), #만료 시간
            "tries": 0, #시도 횟수
            "verified": False,
        }
        save_signup_session(request, payload)
        logger.info("세션에 인증 정보 저장 - email=%s", form.cleaned_data.get("email"))
        send_mail("Bijou 인증번호", f"인증번호: {code}", settings.DEFAULT_FROM_EMAIL, [form.cleaned_data["email"]])
        logger.info("인증 이메일 발송 완료 - email=%s", form.cleaned_data.get("email"))
        messages.info(request, "이메일로 인증번호를 보냈습니다.")
        ctx = self.get_context_data(
            form=form,
            show_verification=True,
            verification_form=VerificationForm(),
            verification_passed=False,
        )
        return self.render_to_response(ctx)
    
    def handle_verify_code(self, request):
        session_data = get_signup_session(request)
        if not session_data:
            logger.warning("세션 데이터 없이 인증 시도 발생")
            messages.error(request, "먼저 인증번호를 요청해 주세요.")
            return redirect("accounts:signup")

        signup_form = SignUpForm(initial=self._form_initial_from_session(session_data["data"]))
        verification_form = VerificationForm(request.POST)

        if not verification_form.is_valid():
            logger.info("인증번호 폼 검증 실패: %s", verification_form.errors)
            ctx = self.get_context_data(
                form=signup_form,
                show_verification=True,
                verification_form=verification_form,
            )
            return self.render_to_response(ctx)

        expires_at = datetime.fromisoformat(session_data["expires"])
        if timezone.now() > expires_at:
            logger.info("인증번호 만료 - email=%s", session_data["data"].get("email"))
            clear_signup_session(request)
            verification_form.add_error(None, "인증번호가 만료되었습니다.")
            ctx = self.get_context_data(
                form=signup_form,
                show_verification=True,
                verification_form=verification_form,
            )
            return self.render_to_response(ctx)

        if session_data.get("tries", 0) >= 5:
            logger.warning("인증번호 시도 횟수 초과 - email=%s", session_data["data"].get("email"))
            clear_signup_session(request)
            verification_form.add_error(None, "인증번호 시도 횟수를 초과했습니다.")
            ctx = self.get_context_data(
                form=signup_form,
                show_verification=True,
                verification_form=verification_form,
            )
            return self.render_to_response(ctx)

        if not constant_time_compare(
            session_data["code_hash"],
            _hash_code(verification_form.cleaned_data["code"]),
        ):
            session_data["tries"] = session_data.get("tries", 0) + 1
            save_signup_session(request, session_data)
            logger.info(
                "인증번호 불일치 - email=%s (시도 %d회)",
                session_data["data"].get("email"),
                session_data["tries"],
            )
            verification_form.add_error("code", "인증번호가 올바르지 않습니다.")
            ctx = self.get_context_data(
                form=signup_form,
                show_verification=True,
                verification_form=verification_form,
                verification_passed=False,
            )
            return self.render_to_response(ctx)

        session_data["verified"] = True
        save_signup_session(request, session_data)
        messages.success(request, "이메일 인증이 완료되었습니다. 회원가입 버튼을 눌러 마무리해 주세요.")
        logger.info("이메일 인증 성공 - email=%s", session_data["data"].get("email"))
        ctx = self.get_context_data(
            form=signup_form,
            show_verification=True,
            verification_form=VerificationForm(),
            verification_passed=True,
        )
        return self.render_to_response(ctx)

    def handle_complete_signup(self, request):
        session_data = get_signup_session(request)
        if not session_data or not session_data.get("verified"):
            logger.warning("인증 완료 전 가입 시도")
            messages.error(request, "이메일 인증을 먼저 완료해 주세요.")
            form_initial = self._form_initial_from_session(session_data["data"]) if session_data else None
            form = SignUpForm(initial=form_initial)
            ctx = self.get_context_data(
                form=form,
                show_verification=bool(session_data),
                verification_form=VerificationForm(),
                verification_passed=bool(session_data and session_data.get("verified")),
            )
            return self.render_to_response(ctx)

        user = SignUpForm.create_user_from_payload(session_data["data"])
        auth_user = authenticate(
            request,
            username=user.username,
            password=session_data["data"]["password1"],
        )
        if auth_user is None:
            logger.error("자동 로그인 실패 - username=%s", user.username)
            messages.error(request, "자동 로그인을 진행할 수 없습니다. 직접 로그인해 주세요.")
            return redirect("accounts:login")
        login(request, auth_user)
        clear_signup_session(request)
        logger.info("회원가입 완료 및 자동 로그인 - username=%s", user.username)
        messages.success(request, "회원가입이 완료되었습니다.")
        return redirect(self.get_success_url())
