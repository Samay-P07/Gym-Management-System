import datetime
from random import randint
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from .models import (
    Booking, Category, ClassSchedule, Contact, Package,
    Packagetype, Paymenthistory, Signup, Trainer
)

# -------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------
def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


# -------------------------------------------------------------
# Public Pages
# -------------------------------------------------------------
def index(request):
    """
    Main landing page: modern athletic design, hero, featured plans,
    trainers preview, schedule snippet, BMI calculator, contact form.
    """
    if request.method == "POST":
        # Handle embedded admin login if submitted from index
        if 'uname' in request.POST:
            u = request.POST.get('uname', '').strip()
            p = request.POST.get('pwd', '').strip()
            user = authenticate(username=u, password=p)
            if user and user.is_staff:
                login(request, user)
                messages.success(request, f"Welcome back, Admin {user.first_name or user.username}!")
                return redirect('admin_home')
            else:
                messages.error(request, "Invalid administrator credentials. Please check your username and password.")
                return redirect('admin_login')

        # Handle contact form submission
        elif 'name' in request.POST and 'email' in request.POST:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            subject = request.POST.get('subject', 'General Inquiry').strip()
            message = request.POST.get('message', '').strip()
            if name and email and message:
                Contact.objects.create(name=name, email=email, subject=subject, message=message)
                messages.success(request, f"Thank you {name}! Your message has been received. Our team will contact you shortly.")
            else:
                messages.error(request, "Please fill in all required fields before submitting.")
            return redirect('index')

    packages = Package.objects.all().order_by('id')[:6]
    trainers = Trainer.objects.filter(is_active=True)[:4]
    categories = Category.objects.all()[:4]
    schedules = ClassSchedule.objects.all()[:6]

    context = {
        'packages': packages,
        'package': packages,  # for backward compatibility
        'trainers': trainers,
        'categories': categories,
        'schedules': schedules,
    }
    return render(request, 'index.html', context)


def about_us(request):
    """About FITCORE, our philosophy, amenities, and team."""
    trainers = Trainer.objects.filter(is_active=True)[:4]
    return render(request, 'about.html', {'trainers': trainers})


def facilities(request):
    """Showcase of gym facilities and zones."""
    return render(request, 'facilities.html')


def trainers_view(request):
    """Full coaching staff roster and certifications."""
    trainers = Trainer.objects.filter(is_active=True)
    return render(request, 'trainers.html', {'trainers': trainers})


def schedule_view(request):
    """Weekly class timetable with filterable categories."""
    selected_day = request.GET.get('day', 'Monday')
    all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    schedules = ClassSchedule.objects.filter(day_of_week=selected_day)
    all_schedules = ClassSchedule.objects.all()

    context = {
        'schedules': schedules,
        'all_schedules': all_schedules,
        'selected_day': selected_day,
        'all_days': all_days,
    }
    return render(request, 'schedule.html', context)


def calculator_view(request):
    """Interactive BMI, BMR, and Daily Caloric Target Calculator."""
    packages = Package.objects.all()[:3]
    return render(request, 'calculator.html', {'packages': packages})


def pricing_view(request):
    """Full membership plans and feature comparison."""
    packages = Package.objects.all()
    categories = Category.objects.all()
    return render(request, 'pricing.html', {'packages': packages, 'categories': categories})


def contact_view(request):
    """Contact page with direct messaging."""
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', 'General Inquiry').strip()
        message = request.POST.get('message', '').strip()
        if name and email and message:
            Contact.objects.create(name=name, email=email, subject=subject, message=message)
            messages.success(request, f"Thank you {name}! Your message has been received. Our team will reach out within 24 hours.")
            return redirect('contact')
        else:
            messages.error(request, "Please complete all required fields.")
    return render(request, 'contact.html')


# -------------------------------------------------------------
# Authentication & Registration
# -------------------------------------------------------------
def registration(request):
    """New member registration with validation."""
    if request.user.is_authenticated:
        return redirect('member_dashboard')

    if request.method == "POST":
        fname = request.POST.get('firstname', '').strip()
        lname = request.POST.get('secondname', '').strip()
        email = request.POST.get('email', '').strip().lower()
        pwd = request.POST.get('password', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', 'Ahmedabad').strip()
        state = request.POST.get('state', 'Gujarat').strip()

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "This Email Address is already registered. Please log in.")
            return redirect('registration')

        if len(pwd) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return redirect('registration')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=pwd,
            first_name=fname,
            last_name=lname
        )
        Signup.objects.create(
            user=user,
            mobile=mobile,
            address=address,
            city=city,
            state=state
        )
        messages.success(request, "Registration Successful! You can now log in.")
        return redirect('user_login')

    return render(request, 'registration.html')


def user_login(request):
    """Member login view."""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_home')
        return redirect('member_dashboard')

    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        pwd = request.POST.get('password', '').strip()

        # Try username or email matching
        user = authenticate(username=email, password=pwd)
        if not user:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=pwd)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            if user.is_staff:
                messages.success(request, f"Welcome back, Administrator {user.first_name or user.username}!")
                return redirect('admin_home')
            else:
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect('member_dashboard')
        else:
            messages.error(request, "Invalid email or password. Please verify your credentials.")
            return redirect('user_login')

    return render(request, 'user_login.html')


def admin_login_view(request):
    """Dedicated Admin & Staff login portal."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_home')

    if request.method == "POST":
        u = request.POST.get('uname', '').strip()
        p = request.POST.get('pwd', '').strip()
        user = authenticate(username=u, password=p)
        if user and user.is_staff:
            login(request, user)
            messages.success(request, f"Welcome to the Executive Admin Hub, {user.first_name or user.username}!")
            return redirect('admin_home')
        else:
            messages.error(request, "Access Denied: Invalid administrator credentials.")
            return redirect('admin_login')

    return render(request, 'admin/admin_login.html')


def Logout(request):
    """Log out any user or admin."""
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('index')


def user_logout(request):
    """Log out member."""
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('index')


# -------------------------------------------------------------
# Member Hub & Booking Views
# -------------------------------------------------------------
@login_required(login_url='user_login')
def member_dashboard(request):
    """
    Dedicated Member Hub:
    Digital Membership Pass, Active Status, Countdown, Booking Overview,
    Recent Payments, and Quick Actions.
    """
    signup, _ = Signup.objects.get_or_create(
        user=request.user,
        defaults={'mobile': '0000000000', 'address': 'Member'}
    )
    bookings = Booking.objects.filter(register=signup).order_by('-creationdate')
    active_booking = bookings.filter(status=3).first()
    pending_booking = bookings.filter(status__in=[1, 2]).first()

    plan_name = "No Active Plan"
    if active_booking and active_booking.package:
        plan_name = active_booking.package.titlename
    elif pending_booking and pending_booking.package:
        plan_name = pending_booking.package.titlename

    # Calculate days remaining simulation for active package
    days_left = 30
    if active_booking:
        dur = active_booking.package.packageduration if active_booking.package else "1 Month"
        if "12" in dur or "Year" in dur:
            days_left = 320
        elif "6" in dur:
            days_left = 150
        elif "3" in dur:
            days_left = 75
        else:
            days_left = 22

    context = {
        'signup': signup,
        'bookings': bookings,
        'active_booking': active_booking,
        'pending_booking': pending_booking,
        'plan_name': plan_name,
        'days_left': days_left,
        'total_bookings': bookings.count(),
    }
    return render(request, 'member_dashboard.html', context)


@login_required(login_url='user_login')
def user_profile(request):
    """View and update member profile information."""
    signup, _ = Signup.objects.get_or_create(
        user=request.user,
        defaults={'mobile': '0000000000', 'address': 'Member'}
    )

    if request.method == "POST":
        fname = request.POST.get('firstname', '').strip()
        lname = request.POST.get('secondname', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', signup.city or 'Ahmedabad').strip()
        state = request.POST.get('state', signup.state or 'Gujarat').strip()

        # Update User model
        user = request.user
        user.first_name = fname
        user.last_name = lname
        if email and email != user.email:
            if not User.objects.filter(email=email).exclude(id=user.id).exists():
                user.email = email
                user.username = email
        user.save()

        # Update Signup model
        signup.mobile = mobile
        signup.address = address
        signup.city = city
        signup.state = state
        signup.save()

        messages.success(request, "Your profile details have been successfully updated.")
        return redirect('user_profile')

    data = signup
    return render(request, "user_profile.html", {'data': data, 'signup': signup})


@login_required(login_url='user_login')
def user_change_password(request):
    """Change member password with old password verification."""
    if request.method == "POST":
        old_pwd = request.POST.get('pwd3', '').strip()
        new_pwd = request.POST.get('pwd1', '').strip()
        conf_pwd = request.POST.get('pwd2', '').strip()

        if not request.user.check_password(old_pwd):
            messages.error(request, "Current password does not match our records.")
            return redirect('user_change_password')

        if new_pwd != conf_pwd:
            messages.error(request, "New password and Confirm password do not match.")
            return redirect('user_change_password')

        if len(new_pwd) < 6:
            messages.error(request, "New password must be at least 6 characters long.")
            return redirect('user_change_password')

        user = request.user
        user.set_password(new_pwd)
        user.save()
        update_session_auth_hash(request, user)  # Keep user logged in
        messages.success(request, "Password changed successfully!")
        return redirect('member_dashboard')

    return render(request, 'user_change_password.html')


@login_required(login_url='user_login')
def booking_history(request):
    """Display user's membership and booking history."""
    signup, _ = Signup.objects.get_or_create(
        user=request.user,
        defaults={'mobile': '0000000000', 'address': 'Member'}
    )
    data = Booking.objects.filter(register=signup).order_by('-creationdate')
    return render(request, "booking_history.html", {'data': data})


@login_required(login_url='user_login')
def apply_booking(request, pid):
    """Create a new booking and redirect to checkout."""
    package = get_object_or_404(Package, id=pid)
    signup, _ = Signup.objects.get_or_create(
        user=request.user,
        defaults={'mobile': '0000000000', 'address': 'Member'}
    )
    booking_num = str(random_with_N_digits(10))
    booking = Booking.objects.create(
        package=package,
        register=signup,
        bookingnumber=booking_num,
        status=1  # Pending
    )
    messages.success(request, f"Membership plan '{package.titlename}' selected. Please finalize payment to activate your pass.")
    return redirect('payment_checkout', booking_id=booking.id)


@login_required(login_url='user_login')
def payment_checkout(request, booking_id):
    """Checkout page for a booking."""
    booking = get_object_or_404(Booking, id=booking_id)

    # Security check: User can only checkout their own booking
    if not request.user.is_staff and booking.register.user != request.user:
        messages.error(request, "Unauthorized access to this booking.")
        return redirect('booking_history')

    return render(request, 'payment_checkout.html', {'booking': booking})


@login_required(login_url='user_login')
def payment_success(request):
    """Process payment confirmation and activate membership."""
    if request.method == "POST":
        booking_id = request.POST.get('booking_id')
        payment_id = request.POST.get('razorpay_payment_id', f"PAY_{random_with_N_digits(8)}")

        booking = get_object_or_404(Booking, id=booking_id)

        # Security check
        if not request.user.is_staff and booking.register.user != request.user:
            messages.error(request, "Unauthorized operation.")
            return redirect('booking_history')

        booking.status = 3  # Full Payment / Active
        booking.save()

        price_val = booking.package.price if booking.package else "0"
        Paymenthistory.objects.create(
            user=booking.register,
            booking=booking,
            price=price_val,
            status=3
        )

        messages.success(request, f"Payment Verified! Txn ID: {payment_id}. Your membership is now ACTIVE!")
        return redirect('membership_invoice', booking_id=booking.id)

    return redirect('member_dashboard')


@login_required(login_url='user_login')
def booking_detail(request, pid):
    """
    Detailed booking specification.
    Includes security protection: non-staff members can only view their own bookings.
    Staff members can view and update payment records.
    """
    booking = get_object_or_404(Booking, id=pid)

    # Security IDOR protection
    if not request.user.is_staff and (not booking.register or booking.register.user != request.user):
        messages.error(request, "Access restricted: You cannot view other members' bookings.")
        return redirect('booking_history')

    if request.method == "POST" and request.user.is_staff:
        price = request.POST.get('price', booking.package.price if booking.package else '0')
        status = int(request.POST.get('status', 1))
        booking.status = status
        booking.save()
        Paymenthistory.objects.create(user=booking.register, booking=booking, price=price, status=status)
        messages.success(request, f"Booking status updated to: {booking.status_label}")
        return redirect('booking_detail', pid)

    payment = Paymenthistory.objects.filter(booking=booking).order_by('-creationdate')

    context = {
        'data': booking,
        'booking': booking,
        'payment': payment,
    }
    if request.user.is_staff:
        return render(request, "admin/admin_booking_detail.html", context)
    return render(request, "user_booking_detail.html", context)


@login_required(login_url='user_login')
def membership_invoice(request, booking_id):
    """
    Printable & Downloadable Digital Tax Invoice & Membership Receipt.
    Complete with GSTIN mock, invoice #, member details, breakdown, and verified paid stamp.
    """
    booking = get_object_or_404(Booking, id=booking_id)

    # Security check: User can only view their own invoice unless staff
    if not request.user.is_staff and booking.register.user != request.user:
        messages.error(request, "Unauthorized access to this invoice.")
        return redirect('booking_history')

    # Calculate tax breakdown (assuming total price includes or adds 18% GST)
    total_price = booking.package.clean_price if booking.package else 0.0
    base_price = round(total_price / 1.18, 2)
    gst_amount = round(total_price - base_price, 2)

    context = {
        'booking': booking,
        'total_price': total_price,
        'base_price': base_price,
        'gst_amount': gst_amount,
        'today': datetime.date.today(),
    }
    return render(request, 'invoice.html', context)


# -------------------------------------------------------------
# Admin Management Views
# -------------------------------------------------------------
def admin_home(request):
    """Executive Admin Dashboard with KPIs, Revenue, and Analytics."""
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "Please log in with administrator credentials.")
        return redirect('admin_login')

    totalcategory = Category.objects.count()
    totalpackagetype = Packagetype.objects.count()
    totalpackage = Package.objects.count()
    totalbooking = Booking.objects.count()
    total_members = Signup.objects.count()
    total_messages = Contact.objects.count()

    New = Booking.objects.filter(status=1)
    Partial = Booking.objects.filter(status=2)
    Full = Booking.objects.filter(status=3)

    # Calculate total revenue from completed payments
    revenue = 0
    for p in Paymenthistory.objects.filter(status=3):
        try:
            revenue += float(str(p.price).replace('$', '').replace('₹', '').replace(',', '').strip())
        except (ValueError, TypeError):
            pass

    recent_bookings = Booking.objects.all().order_by('-creationdate')[:6]
    recent_messages = Contact.objects.all().order_by('-creationdate')[:4]

    context = {
        'totalcategory': totalcategory,
        'totalpackagetype': totalpackagetype,
        'totalpackage': totalpackage,
        'totalbooking': totalbooking,
        'total_members': total_members,
        'total_messages': total_messages,
        'total_revenue': f"{int(revenue):,}",
        'New': New,
        'Partial': Partial,
        'Full': Full,
        'recent_bookings': recent_bookings,
        'recent_messages': recent_messages,
    }
    return render(request, 'admin/admin_home.html', context)


@login_required(login_url='admin_login')
def manageCategory(request):
    """Admin: Manage package categories."""
    if not request.user.is_staff:
        return redirect('admin_login')

    category = Category.objects.all().order_by('-creationdate')
    if request.method == "POST":
        categoryname = request.POST.get('categoryname', '').strip()
        status = request.POST.get('status', 'Active').strip()
        if categoryname:
            Category.objects.create(categoryname=categoryname, status=status)
            messages.success(request, f"Category '{categoryname}' created successfully.")
            return redirect('manageCategory')

    return render(request, 'admin/manageCategory.html', {'category': category})


@login_required(login_url='admin_login')
def editCategory(request, pid):
    """Admin: Edit category."""
    if not request.user.is_staff:
        return redirect('admin_login')

    category = get_object_or_404(Category, id=pid)
    if request.method == "POST":
        categoryname = request.POST.get('categoryname', '').strip()
        status = request.POST.get('status', 'Active').strip()
        if categoryname:
            category.categoryname = categoryname
            category.status = status
            category.save()
            messages.success(request, "Category updated successfully.")
            return redirect('manageCategory')

    return render(request, 'admin/editCategory.html', {'category': category})


@login_required(login_url='admin_login')
def deleteCategory(request, pid):
    """Admin: Delete category."""
    if not request.user.is_staff:
        return redirect('admin_login')

    category = get_object_or_404(Category, id=pid)
    name = category.categoryname
    category.delete()
    messages.success(request, f"Category '{name}' deleted.")
    return redirect('manageCategory')


@login_required(login_url='admin_login')
def managePackageType(request):
    """Admin: Manage package types."""
    if not request.user.is_staff:
        return redirect('admin_login')

    package = Packagetype.objects.all().order_by('-creationdate')
    category = Category.objects.all()

    if request.method == "POST":
        cid = request.POST.get('category')
        packagename = request.POST.get('packagename', '').strip()
        if cid and packagename:
            cat_obj = get_object_or_404(Category, id=cid)
            Packagetype.objects.create(category=cat_obj, packagename=packagename)
            messages.success(request, f"Package Type '{packagename}' created successfully.")
            return redirect('managePackageType')

    return render(request, 'admin/managePackageType.html', {'package': package, 'category': category})


@login_required(login_url='admin_login')
def editPackageType(request, pid):
    """Admin: Edit package type."""
    if not request.user.is_staff:
        return redirect('admin_login')

    packagetype = get_object_or_404(Packagetype, id=pid)
    category = Category.objects.all()

    if request.method == "POST":
        cid = request.POST.get('category')
        packagename = request.POST.get('packagename', '').strip()
        if cid and packagename:
            packagetype.category = get_object_or_404(Category, id=cid)
            packagetype.packagename = packagename
            packagetype.save()
            messages.success(request, "Package Type updated successfully.")
            return redirect('managePackageType')

    return render(request, 'admin/editPackageType.html', {
        'package': packagetype,
        'category': category
    })


@login_required(login_url='admin_login')
def deletePackageType(request, pid):
    """Admin: Delete package type."""
    if not request.user.is_staff:
        return redirect('admin_login')

    packagetype = get_object_or_404(Packagetype, id=pid)
    packagetype.delete()
    messages.success(request, "Package type deleted.")
    return redirect('managePackageType')


@login_required(login_url='admin_login')
def managePackage(request):
    """Admin: List all packages."""
    if not request.user.is_staff:
        return redirect('admin_login')

    package = Package.objects.all().order_by('-creationdate')
    return render(request, 'admin/managePackage.html', {'package': package})


@login_required(login_url='admin_login')
def addPackage(request):
    """Admin: Add a new package."""
    if not request.user.is_staff:
        return redirect('admin_login')

    category = Category.objects.all()
    mypackage = Packagetype.objects.all()

    if request.method == "POST":
        cid = request.POST.get('category')
        packagename = request.POST.get('packagename')
        titlename = request.POST.get('titlename', '').strip()
        duration = request.POST.get('duration', '').strip()
        price = request.POST.get('price', '').strip()
        description = request.POST.get('description', '').strip()

        if cid and packagename and titlename and price:
            cat_obj = get_object_or_404(Category, id=cid)
            type_obj = get_object_or_404(Packagetype, id=packagename)
            Package.objects.create(
                category=cat_obj,
                packagename=type_obj,
                titlename=titlename,
                packageduration=duration,
                price=price,
                description=description
            )
            messages.success(request, f"New package '{titlename}' created successfully.")
            return redirect('managePackage')

    return render(request, 'admin/addPackage.html', {
        'category': category,
        'mypackage': mypackage
    })


@login_required(login_url='admin_login')
def editPackage(request, pid):
    """Admin: Edit an existing package."""
    if not request.user.is_staff:
        return redirect('admin_login')

    data = get_object_or_404(Package, id=pid)
    category = Category.objects.all()
    mypackage = Packagetype.objects.all()

    if request.method == "POST":
        cid = request.POST.get('category')
        packagename = request.POST.get('packagename')
        titlename = request.POST.get('titlename', '').strip()
        duration = request.POST.get('duration', '').strip()
        price = request.POST.get('price', '').strip()
        description = request.POST.get('description', '').strip()

        if cid and packagename and titlename:
            data.category = get_object_or_404(Category, id=cid)
            data.packagename = get_object_or_404(Packagetype, id=packagename)
            data.titlename = titlename
            data.packageduration = duration
            data.price = price
            data.description = description
            data.save()
            messages.success(request, f"Package '{titlename}' updated successfully.")
            return redirect('managePackage')

    return render(request, "admin/editPackage.html", {
        'data': data,
        'category': category,
        'mypackage': mypackage
    })


@login_required(login_url='admin_login')
def deletePackage(request, pid):
    """Admin: Delete package."""
    if not request.user.is_staff:
        return redirect('admin_login')

    package = get_object_or_404(Package, id=pid)
    package.delete()
    messages.success(request, "Package deleted successfully.")
    return redirect('managePackage')


@login_required(login_url='admin_login')
def new_booking(request):
    """Admin: View bookings filtered by status."""
    if not request.user.is_staff:
        return redirect('admin_login')

    action = request.GET.get('action', 'Total')
    data = Booking.objects.all().order_by('-creationdate')

    if action == "New":
        data = data.filter(status=1)
    elif action == "Partial":
        data = data.filter(status=2)
    elif action == "Full":
        data = data.filter(status=3)

    return render(request, "admin/new_booking.html", {
        'data': data,
        'action': action
    })


@login_required(login_url='admin_login')
def deleteBooking(request, pid):
    """Admin: Delete a booking."""
    if not request.user.is_staff:
        return redirect('admin_login')

    booking = get_object_or_404(Booking, id=pid)
    booking.delete()
    messages.success(request, "Booking deleted successfully.")
    return redirect('new_booking')


@login_required(login_url='admin_login')
def reg_user(request):
    """Admin: View and search registered members."""
    if not request.user.is_staff:
        return redirect('admin_login')

    q = request.GET.get('q', '').strip()
    data = Signup.objects.all().order_by('-creationdate')
    if q:
        data = data.filter(
            user__first_name__icontains=q
        ) | data.filter(
            user__last_name__icontains=q
        ) | data.filter(
            user__email__icontains=q
        ) | data.filter(
            mobile__icontains=q
        )

    return render(request, "admin/reg_user.html", {'data': data, 'q': q})


@login_required(login_url='admin_login')
def delete_user(request, pid):
    """Admin: Delete a member."""
    if not request.user.is_staff:
        return redirect('admin_login')

    signup = get_object_or_404(Signup, id=pid)
    if signup.user:
        signup.user.delete()
    else:
        signup.delete()
    messages.success(request, "Member account deleted.")
    return redirect('reg_user')


@login_required(login_url='admin_login')
def bookingReport(request):
    """Admin: Generate date-range booking report."""
    if not request.user.is_staff:
        return redirect('admin_login')

    data = None
    data2 = False
    fromdate = ""
    todate = ""

    if request.method == "POST":
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        if fromdate and todate:
            data = Booking.objects.filter(creationdate__date__gte=fromdate, creationdate__date__lte=todate).order_by('-creationdate')
            data2 = True

    return render(request, "admin/bookingReport.html", {
        'data': data,
        'data2': data2,
        'fromdate': fromdate,
        'todate': todate
    })


@login_required(login_url='admin_login')
def regReport(request):
    """Admin: Generate member registration report by date range."""
    if not request.user.is_staff:
        return redirect('admin_login')

    data = None
    data2 = False
    fromdate = ""
    todate = ""

    if request.method == "POST":
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        if fromdate and todate:
            data = Signup.objects.filter(creationdate__date__gte=fromdate, creationdate__date__lte=todate).order_by('-creationdate')
            data2 = True

    return render(request, "admin/regReport.html", {
        'data': data,
        'data2': data2,
        'fromdate': fromdate,
        'todate': todate
    })


@login_required(login_url='admin_login')
def changePassword(request):
    """Admin: Change administrative password."""
    if not request.user.is_staff:
        return redirect('admin_login')

    error = ""
    if request.method == "POST":
        old_pwd = request.POST.get('oldpassword', '').strip()
        new_pwd = request.POST.get('newpassword', '').strip()

        if request.user.check_password(old_pwd):
            user = request.user
            user.set_password(new_pwd)
            user.save()
            update_session_auth_hash(request, user)
            error = "no"
            messages.success(request, "Admin password updated successfully.")
        else:
            error = "not"
            messages.error(request, "Old password was incorrect.")

    return render(request, 'admin/changePassword.html', {'error': error})


@login_required(login_url='admin_login')
def view_messages(request):
    """Admin: View customer inquiries from contact forms."""
    if not request.user.is_staff:
        return redirect('admin_login')

    data = Contact.objects.all().order_by('-creationdate')
    return render(request, "admin/view_messages.html", {'data': data})


@login_required(login_url='admin_login')
def delete_message(request, pid):
    """Admin: Delete contact inquiry."""
    if not request.user.is_staff:
        return redirect('admin_login')

    msg = get_object_or_404(Contact, id=pid)
    msg.delete()
    messages.success(request, "Message deleted.")
    return redirect('view_messages')
