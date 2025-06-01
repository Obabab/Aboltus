from rest_framework import permissions

class IsOwnerOrStaff(permissions.BasePermission):
    """
    Позволяет доступ только владельцу объекта (по полю django_user) или staff-пользователю.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or (
            hasattr(obj, 'django_user') and obj.django_user == request.user
        )
