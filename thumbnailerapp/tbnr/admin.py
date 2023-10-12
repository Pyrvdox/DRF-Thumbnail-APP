from django.contrib import admin
from .models import ImageSize, Image, Plan, CustomUser
# Register your models here.


class ImageSizeAdmin(admin.ModelAdmin):
    list_display = ('size',)


admin.site.register(ImageSize, ImageSizeAdmin)


class ImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'file', 'uploaded_by')


admin.site.register(Image, ImageAdmin)


class PlanAdmin(admin.ModelAdmin):
    list_display = ['name',]

    def display_heights(self, obj):
        return ", ".join([str(height.size) for height in obj.height.all()])

    display_heights.short_description = "Heights"


admin.site.register(Plan, PlanAdmin)


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username',]

    def save_model(self, request, obj, form, change):
        obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


admin.site.register(CustomUser, CustomUserAdmin)