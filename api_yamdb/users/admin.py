from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm  #пока не понял нужно ли...............


User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role',
    )
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role',
    )
    list_editable = ('role',)


admin.site.register(User, UserAdmin)

# все говно что в админ зоне опишем здесь но у меня уже нихуя не получается 14:43 15.05