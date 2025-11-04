from django.contrib.admin.apps import AdminConfig


#django.contrib.admin 대신 프로젝트 전용 AdminSite를 사용하기 위한 설정
class ConfigAdminConfig(AdminConfig):
    """Project-specific admin configuration using a custom AdminSite."""

    default_site = "config.admin_site.BijouAdminSite"
