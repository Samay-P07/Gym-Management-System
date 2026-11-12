from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    categoryname = models.CharField(max_length=200, null=True)
    status = models.CharField(max_length=300, null=True, blank=True)
    creationdate = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.categoryname or "Category"

class Packagetype(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    packagename = models.CharField(max_length=200, null=True)
    creationdate = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Package Types"

    def __str__(self):
        return self.packagename or "Package Type"

class Signup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    mobile = models.CharField(max_length=15, null=True)
    state = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    creationdate = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Member Profile"
        verbose_name_plural = "Member Profiles"

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        if self.user:
            name = f"{self.user.first_name} {self.user.last_name}".strip()
            return name if name else self.user.username
        return "Member"

class Package(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    packagename = models.ForeignKey(Packagetype, on_delete=models.CASCADE, null=True)
    titlename = models.CharField(max_length=200, null=True)
    packageduration = models.CharField(max_length=50, null=True)
    price = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True, blank=True)
    creationdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titlename or "Package"

    @property
    def clean_price(self):
        try:
            cleaned = str(self.price).replace('$', '').replace('₹', '').replace(',', '').strip()
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0

    @property
    def formatted_price(self):
        try:
            val = self.clean_price
            return f"{int(val):,}" if val.is_integer() else f"{val:,.2f}"
        except Exception:
            return str(self.price)

STATUS = (
    (1, "Pending / Unpaid"),
    (2, "Partial Payment"),
    (3, "Full Payment / Active"),
)

class Booking(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True)
    register = models.ForeignKey(Signup, on_delete=models.CASCADE, null=True, blank=True)
    bookingnumber = models.CharField(max_length=100, null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=1)
    creationdate = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creationdate']

    def __str__(self):
        return f"Booking #{self.bookingnumber or self.id}"

    @property
    def status_label(self):
        for code, label in STATUS:
            if self.status == code:
                return label
        return "Unknown"

    @property
    def invoice_number(self):
        num = self.bookingnumber if self.bookingnumber else str(self.id)
        return f"FC-INV-{num}"

class Paymenthistory(models.Model):
    user = models.ForeignKey(Signup, on_delete=models.CASCADE, null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=1)
    creationdate = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Payment Histories"
        ordering = ['-creationdate']

    def __str__(self):
        return f"Payment #{self.id} - ₹{self.price}"

class Contact(models.Model):
    name = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
    subject = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField(null=True)
    creationdate = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creationdate']

    def __str__(self):
        return f"{self.name} - {self.subject or 'Message'}"

class Trainer(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, default="Head Strength Coach")
    speciality = models.CharField(max_length=200, default="Hypertrophy & Biomechanics")
    experience = models.CharField(max_length=50, default="7+ Years")
    bio = models.TextField(blank=True, null=True)
    certifications = models.CharField(max_length=255, default="CSCS, ACE-CPT, Precision Nutrition L1")
    image_url = models.CharField(max_length=300, blank=True, null=True)
    instagram = models.CharField(max_length=100, default="@fitcore_coach")
    is_active = models.BooleanField(default=True)
    creationdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ClassSchedule(models.Model):
    classname = models.CharField(max_length=150)
    category = models.CharField(max_length=100)  # Strength, HIIT, Yoga, CrossFit, Boxing
    trainer = models.CharField(max_length=150)
    day_of_week = models.CharField(max_length=20)  # Monday, Tuesday, ...
    start_time = models.CharField(max_length=20)
    end_time = models.CharField(max_length=20)
    room = models.CharField(max_length=100, default="Main Arena")
    intensity = models.CharField(max_length=50, default="High Intensity")
    capacity = models.IntegerField(default=25)
    creationdate = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.classname} ({self.day_of_week} {self.start_time})"
