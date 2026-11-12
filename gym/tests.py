from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from gym.models import (
    Category, Packagetype, Package, Signup, Booking, Paymenthistory, Trainer, ClassSchedule, Contact
)

class GymManagementSystemTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Admin
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='testpassword123',
            first_name='Admin',
            last_name='User'
        )

        # Create Member User
        self.member_user = User.objects.create_user(
            username='member_test@test.com',
            email='member_test@test.com',
            password='testpassword123',
            first_name='John',
            last_name='Doe'
        )
        self.member_signup = Signup.objects.create(
            user=self.member_user,
            mobile='9876543210',
            city='Ahmedabad',
            state='Gujarat',
            address='123 Fitness St'
        )

        # Create Category & Package
        self.category = Category.objects.create(
            categoryname='Strength & Conditioning',
            status='Active'
        )
        self.packagetype = Packagetype.objects.create(
            category=self.category,
            packagename='Monthly Strength'
        )
        self.package = Package.objects.create(
            category=self.category,
            packagename=self.packagetype,
            titlename='Hypertrophy Beast',
            packageduration='1 Month',
            price='2499',
            description='Access to Olympic weights and guided plans.'
        )

        # Create Trainer & Schedule
        self.trainer = Trainer.objects.create(
            name='Marcus Vance',
            role='Head Strength Coach',
            speciality='Powerlifting',
            experience='8 Years',
            certifications='CSCS'
        )
        self.schedule = ClassSchedule.objects.create(
            classname='Dawn CrossFit',
            category='CrossFit',
            trainer='Marcus Vance',
            day_of_week='Monday',
            start_time='06:00 AM',
            end_time='07:00 AM',
            room='Arena 1'
        )

    def test_public_pages_status_codes(self):
        """Verify all public showcase pages render with HTTP 200."""
        routes = [
            'index',
            'about_us',
            'facilities',
            'trainers_view',
            'schedule_view',
            'calculator_view',
            'pricing_view',
            'contact',
            'user_login',
            'admin_login',
            'registration',
        ]
        for route in routes:
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, 200, f"Route {route} failed with status {response.status_code}")

    def test_package_model_properties(self):
        """Test clean_price and formatted_price calculations."""
        self.assertEqual(self.package.clean_price, 2499.0)
        self.assertEqual(self.package.formatted_price, "2,499")

    def test_member_registration(self):
        """Test new member registration flow."""
        response = self.client.post(reverse('registration'), {
            'firstname': 'Jane',
            'secondname': 'Smith',
            'email': 'jane.smith@test.com',
            'password': 'securepassword123',
            'mobile': '9123456780',
            'address': '456 Gym Ave',
            'city': 'Ahmedabad',
            'state': 'Gujarat'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='jane.smith@test.com').exists())
        self.assertTrue(Signup.objects.filter(mobile='9123456780').exists())

    def test_user_authentication(self):
        """Test member login and redirection."""
        response = self.client.post(reverse('user_login'), {
            'email': 'member_test@test.com',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('member_dashboard'))

    def test_admin_authentication(self):
        """Test dedicated admin login."""
        response = self.client.post(reverse('admin_login'), {
            'uname': 'admin_test',
            'pwd': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_home'))

    def test_booking_and_payment_flow(self):
        """Test full cycle: package booking, checkout, and payment success."""
        self.client.login(username='member_test@test.com', password='testpassword123')

        # Apply booking
        apply_response = self.client.get(reverse('apply_booking', args=[self.package.id]))
        self.assertEqual(apply_response.status_code, 302)

        booking = Booking.objects.filter(register=self.member_signup).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.status, 1)  # Pending

        # Payment Success
        pay_response = self.client.post(reverse('payment_success'), {
            'booking_id': booking.id,
            'razorpay_payment_id': 'pay_test_123456'
        })
        self.assertEqual(pay_response.status_code, 302)

        booking.refresh_from_db()
        self.assertEqual(booking.status, 3)  # Active / Full Payment
        self.assertTrue(Paymenthistory.objects.filter(booking=booking, status=3).exists())

        # Test Invoice Access
        inv_response = self.client.get(reverse('membership_invoice', args=[booking.id]))
        self.assertEqual(inv_response.status_code, 200)
        self.assertContains(inv_response, booking.invoice_number)

    def test_unauthorized_admin_access_redirect(self):
        """Unauthenticated user accessing admin_home must redirect to admin_login."""
        response = self.client.get(reverse('admin_home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin_login'), response.url)

    def test_contact_form_submission(self):
        """Verify contact form stores message in database."""
        response = self.client.post(reverse('contact'), {
            'name': 'Alex Mercer',
            'email': 'alex@mercer.com',
            'subject': 'Personal Training Query',
            'message': 'Looking for 1-on-1 powerlifting coaching.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Contact.objects.filter(email='alex@mercer.com').exists())
