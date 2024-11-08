from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username',  'is_active')
    list_filter = ('email', 'username',  'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_active',  'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_active', '' ,'is_superuser','user_permissions'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)

# Register the CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(VideoAnalysis)
class VideoAnalysisAdmin(admin.ModelAdmin):
    readonly_fields = ('dominant_emotion', 'analyzed_on', 'calm_percentage', 'emotion_counts', 'token', 'status')
    list_display = ('dominant_emotion', 'analyzed_on', 'status')

    def has_add_permission(self, request):
        return False  # Disable ability to add new instances

    def has_delete_permission(self, request, obj=None):
        return False  # Disable ability to delete instances
