from django.contrib.auth.models import Group
from rest_framework import permissions


class IsUploaderOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return Group.objects.get(name='owners') in request.user.groups.all()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.uploaded_by


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST' and 'place' in request.data:
            return request.user.id and \
                   request.user.places.filter(
                       id=request.data['place']
                   ).exists()
        return True

    def has_object_permission(self, request, view, obj):
        unsafe_methods_permission = request.user == obj.place.uploaded_by
        if request.method in ['PATCH', 'PUT']:
            if 'place' in request.data:
                return request.user.id and \
                       request.user.places.filter(
                           id=request.data['place']
                       ).exists()
            return unsafe_methods_permission
        if request.method == 'DELETE':
            return unsafe_methods_permission
        return True


class IsReviewerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST' and 'place' in request.data:
            can_not_review = request.user.id is None
            has_already_reviewed = request.user.reviews.filter(
                place=request.data['place']
            ).exists() if not can_not_review else can_not_review
            return request.user.is_authenticated and not has_already_reviewed
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.author
