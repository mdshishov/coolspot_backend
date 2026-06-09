from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


admin.site.site_header = 'CoolSpot Admin'
admin.site.site_title = 'CoolSpot Admin'
admin.site.index_title = 'Панель управления рестораном'


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 20

    @admin.display(description='')
    def admin_actions(self, obj):
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name

        edit_url = reverse(
            f'admin:{app_label}_{model_name}_change',
            args=[obj.id]
        )

        return format_html(
            '''
            <a class="changelink" style="text-decoration: none" href="{}"></a>
            ''',
            edit_url,
            delete_url,
        )
