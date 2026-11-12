from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from gym.views import (
    index, about_us, facilities, trainers_view, schedule_view,
    calculator_view, pricing_view, contact_view,
    registration, user_login, admin_login_view, Logout, user_logout,
    member_dashboard, user_profile, user_change_password,
    booking_history, apply_booking, payment_checkout, payment_success,
    booking_detail, membership_invoice,
    admin_home, manageCategory, editCategory, deleteCategory,
    managePackageType, editPackageType, deletePackageType,
    managePackage, addPackage, editPackage, deletePackage,
    new_booking, deleteBooking, reg_user, delete_user,
    bookingReport, regReport, changePassword, view_messages, delete_message
)

urlpatterns = [
    # Built-in Django Admin
    path('admin/', admin.site.urls),

    # Public Showcase Pages
    path('', index, name='index'),
    path('about/', about_us, name='about_us'),
    path('facilities/', facilities, name='facilities'),
    path('trainers/', trainers_view, name='trainers_view'),
    path('schedule/', schedule_view, name='schedule_view'),
    path('calculator/', calculator_view, name='calculator_view'),
    path('pricing/', pricing_view, name='pricing_view'),
    path('contact/', contact_view, name='contact'),

    # Authentication & Accounts
    path('registration/', registration, name='registration'),
    path('registration', registration),  # legacy compatibility
    path('user_login/', user_login, name='user_login'),
    path('admin_login/', admin_login_view, name='admin_login'),
    path('logout/', Logout, name='logout'),
    path('user_logout/', user_logout, name='user_logout'),

    # Member Portal
    path('dashboard/', member_dashboard, name='member_dashboard'),
    path('user_profile/', user_profile, name='user_profile'),
    path('user_change_password/', user_change_password, name='user_change_password'),
    path('booking_history/', booking_history, name='booking_history'),
    path('apply-booking/<int:pid>/', apply_booking, name='apply_booking'),
    path('payment_checkout/<int:booking_id>/', payment_checkout, name='payment_checkout'),
    path('payment_success/', payment_success, name='payment_success'),
    path('booking_detail/<int:pid>/', booking_detail, name='booking_detail'),
    path('invoice/<int:booking_id>/', membership_invoice, name='membership_invoice'),

    # Staff / Admin Management Hub
    path('admin_home/', admin_home, name='admin_home'),
    path('manageCategory/', manageCategory, name='manageCategory'),
    path('editCategory/<int:pid>/', editCategory, name='editCategory'),
    path('deleteCategory/<int:pid>/', deleteCategory, name='deleteCategory'),
    path('managePackageType/', managePackageType, name='managePackageType'),
    path('editPackageType/<int:pid>/', editPackageType, name='editPackageType'),
    path('deletePackageType/<int:pid>/', deletePackageType, name='deletePackageType'),
    path('managePackage/', managePackage, name='managePackage'),
    path('addPackage/', addPackage, name='addPackage'),
    path('addPackage', addPackage),  # legacy compatibility
    path('editPackage/<int:pid>/', editPackage, name='editPackage'),
    path('deletePackage/<int:pid>/', deletePackage, name='deletePackage'),
    path('new_booking/', new_booking, name='new_booking'),
    path('deleteBooking/<int:pid>/', deleteBooking, name='deleteBooking'),
    path('reg_user/', reg_user, name='reg_user'),
    path('delete_user/<int:pid>/', delete_user, name='delete_user'),
    path('bookingReport/', bookingReport, name='bookingReport'),
    path('regReport/', regReport, name='regReport'),
    path('changePassword/', changePassword, name='changePassword'),
    path('changePassword', changePassword),  # legacy compatibility
    path('view_messages/', view_messages, name='view_messages'),
    path('delete_message/<int:pid>/', delete_message, name='delete_message'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
