from django.contrib.auth.admin import UserAdmin

UserAdmin.list_display = ('username', 'is_staff',)
