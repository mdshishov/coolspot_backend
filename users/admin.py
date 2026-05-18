from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from core.admin import BaseAdmin
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin, UserAdmin


class UserGroupInline(admin.TabularInline):
    model = CustomUser.groups.through
    extra = 0
    verbose_name = 'Пользователь'
    verbose_name_plural = 'Пользователи'

    autocomplete_fields = ('customuser',)

    class Media:
        css = {
            'all': ('admin/css/hide_edit_group_users_lines.css',)
        }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'customuser':
            formfield.label = 'Пользователь'
        return formfield

class CustomGroupAdmin(GroupAdmin):
    list_display = (
        'name',
        'users_count',
        'users_list',
    )

    inlines = [UserGroupInline]

    @admin.display(description='Кол-во пользователей')
    def users_count(self, obj):
        return obj.user_set.count()

    @admin.display(description='Пользователи')
    def users_list(self, obj):
        users = obj.user_set.all()

        links = []

        for user in users:
            url = f'/admin/users/customuser/{user.id}/change/'
            links.append(
                f'<a href="{url}">{user}</a>'
            )
        return mark_safe(', '.join(links))


admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm

    list_display = (
        'username',
        'id',
        'is_active',
        'full_name',
        'phone',
        'email',
        'role_badge',
        'is_staff',
        'is_superuser',
        'date_joined',
    )

    list_filter = (
        'role',
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
    )

    search_fields = (
        'username',
        'full_name',
        'phone',
        'email',
    )

    ordering = ('-date_joined',)

    readonly_fields = (
        'last_login',
        'date_joined',
    )
    filter_horizontal = ('groups', 'user_permissions')

    add_fieldsets = (
        ('Основная информация', {
            'fields': (
                'username',
                'password1',
                'password2',
                'role',
                'is_active',
            )
        }),

        ('Контактные данные', {
            'fields': (
                'full_name',
                'phone',
                'email',
            )
        }),
    )

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'username',
                'password',
                'role',
                'is_active',
            )
        }),

        ('Контактные данные', {
            'fields': (
                'full_name',
                'phone',
                'email',
            )
        }),
        ('Группы и права', {
            'description': '''
                <div style="
                    color:#dc2626;
                ">
                    <b>Важно!</b> Группы и права пользователя назначаются автоматически при создании в зависимости от выбранной <b>роли</b>.
                    Рекумендуется изменять данные параметры только при необходимости точной настройки для конкретного пользователя.
                </div>
            ''',
            'fields': (
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),

        ('Даты', {
            'fields': (
                'last_login',
                'date_joined',
            )
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        if not obj:
            fieldsets = tuple(
                fs for fs in fieldsets
                if fs[0] not in ['Группы и права', 'Даты']
            )

        return fieldsets

    @admin.display(description='Роль')
    def role_badge(self, obj):
        colors = {
            'client': '#3b82f6',
            'staff': '#f59e0b',
            'admin': '#ef4444',
        }

        return format_html(
            '''
            <span style="
                background:{};
                color:white;
                padding:4px 10px;
                border-radius:4px;
            ">
                {}
            </span>
            ''',
            colors.get(obj.role, '#3b82f6'),
            obj.get_role_display(),
        )
