from rest_framework.permissions import BasePermission


class IsAdminGroup(BasePermission):
    """Доступ только для группы Admin."""
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.groups.filter(name="Admin").exists()


class IsManagerGroup(BasePermission):
    """Доступ только для группы Manager."""
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.groups.filter(name="Manager").exists()


class IsEmployeeGroup(BasePermission):
    """Доступ только для группы Employee."""
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.groups.filter(name="Employee").exists()


class IsAdminOrManager(BasePermission):
    """Доступ для Admin или Manager."""
    def has_permission(self, request, view) -> bool:
        if not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name__in=["Admin", "Manager"]).exists()
