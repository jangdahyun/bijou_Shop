from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    #앱이 로드될 때 실행되는 초기화 훅
    def ready(self):
        import accounts.signals 
