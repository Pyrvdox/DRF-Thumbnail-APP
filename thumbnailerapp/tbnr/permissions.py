from rest_framework import permissions

class HasLinkPlanPermission(permissions.BasePermission):
    message = "Your plan does not allow you to create links to images"

    def has_permission(self, request, view):
        user = request.user
        if user.plan and user.plan.link:
            return True
        return False
