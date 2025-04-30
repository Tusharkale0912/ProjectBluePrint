from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Cart, CartItem

# Register UserProfile in admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = True

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    def has_delete_permission(self, request, obj=None):
        # Only superuser can delete users
        return request.user.is_superuser

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product_name', 'price', 'quantity')
    search_fields = ('product_name', 'cart__user__username')

# Register your models here.
