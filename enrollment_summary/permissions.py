from rest_framework.permissions import BasePermission


class IsSelfOrStaff(BasePermission):
    """
    Only allow:
      - the authenticated user to request their own data (user_id absent or equals request.user.id), or
      - staff/superusers to query any user_id.
    """

    message = "You may only query your own enrollments unless you are staff."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        user_id_param = request.query_params.get("user_id")
        if user_id_param is None:
            # No user_id provided -> defaults to current user in the view
            return True

        try:
            requested_user_id = int(user_id_param)
        except (TypeError, ValueError):
            # Invalid user_id -> block at permission level (clear error)
            self.message = "Invalid user_id; it must be an integer."
            return False

        if requested_user_id == user.id:
            return True

        return bool(user.is_staff or user.is_superuser)
