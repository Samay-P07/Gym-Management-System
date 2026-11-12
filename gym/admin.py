from django.contrib import admin
from .models import (
    Category, Packagetype, Signup, Package,
    Booking, Paymenthistory, Contact, Trainer, ClassSchedule
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'categoryname', 'status', 'creationdate')
    search_fields = ('categoryname',)
    list_filter = ('creationdate',)

@admin.register(Packagetype)
class PackagetypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'packagename', 'category', 'creationdate')
    search_fields = ('packagename', 'category__categoryname')
    list_filter = ('category',)

@admin.register(Signup)
class SignupAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'get_email', 'mobile', 'city', 'state', 'creationdate')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'mobile', 'city')
    list_filter = ('creationdate',)

    def get_email(self, obj):
        return obj.user.email if obj.user else "-"
    get_email.short_description = 'Email'

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'titlename', 'category', 'packagename', 'packageduration', 'price', 'creationdate')
    search_fields = ('titlename', 'category__categoryname', 'packagename__packagename')
    list_filter = ('category', 'packageduration')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'bookingnumber', 'get_member', 'package', 'status', 'creationdate')
    search_fields = ('bookingnumber', 'register__user__first_name', 'register__user__last_name', 'register__user__email')
    list_filter = ('status', 'creationdate')
    readonly_fields = ('creationdate',)

    def get_member(self, obj):
        return obj.register.full_name if obj.register else "-"
    get_member.short_description = 'Member'

@admin.register(Paymenthistory)
class PaymenthistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'get_member', 'price', 'status', 'creationdate')
    search_fields = ('booking__bookingnumber', 'user__user__email')
    list_filter = ('status', 'creationdate')

    def get_member(self, obj):
        return obj.user.full_name if obj.user else "-"
    get_member.short_description = 'Member'

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'subject', 'creationdate')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('creationdate',)

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'role', 'speciality', 'experience', 'is_active')
    search_fields = ('name', 'role', 'speciality')
    list_filter = ('is_active',)

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'classname', 'category', 'trainer', 'day_of_week', 'start_time', 'end_time', 'room')
    search_fields = ('classname', 'trainer', 'category')
    list_filter = ('day_of_week', 'category')
