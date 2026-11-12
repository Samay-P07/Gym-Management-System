from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gym.models import (
    Category, Packagetype, Package, Signup, Booking, Paymenthistory, Trainer, ClassSchedule, Contact
)

class Command(BaseCommand):
    help = "Populates the database with realistic demo data, admin, members, trainers, packages, and schedules."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Seeding FITCORE Gym Management System database..."))

        # 1. Admin Superuser
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@fitcore.com",
                "first_name": "Patel",
                "last_name": "Samay",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / admin123"))
        else:
            admin_user.set_password("admin123")
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Updated admin password to: admin123"))

        # Admin signup record
        Signup.objects.get_or_create(
            user=admin_user,
            defaults={
                "mobile": "+91 98765 43210",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "address": "FITCORE HQ, Ring Road, Ahmedabad",
            }
        )

        # 2. Demo Member
        member_user, created = User.objects.get_or_create(
            username="john.doe@gmail.com",
            defaults={
                "email": "john.doe@gmail.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_staff": False,
            }
        )
        if created:
            member_user.set_password("member123")
            member_user.save()
            self.stdout.write(self.style.SUCCESS("Created member: john.doe@gmail.com / member123"))
        else:
            member_user.set_password("member123")
            member_user.save()

        member_signup, _ = Signup.objects.get_or_create(
            user=member_user,
            defaults={
                "mobile": "+91 91234 56789",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "address": "42 Sunset Boulevard, Bodakdev",
            }
        )

        # 3. Categories
        cat_data = [
            ("Strength & Hypertrophy", "Active"),
            ("Cardio, Endurance & HIIT", "Active"),
            ("Functional Mobility & Yoga", "Active"),
            ("VIP Elite Athlete Tier", "Active"),
        ]
        categories = {}
        for name, status in cat_data:
            cat, _ = Category.objects.get_or_create(categoryname=name, defaults={"status": status})
            categories[name] = cat

        # 4. Package Types
        type_data = [
            ("Strength & Hypertrophy", "1 Month Pure Iron"),
            ("Strength & Hypertrophy", "3 Months Hypertrophy Split"),
            ("Strength & Hypertrophy", "12 Months Elite Bodybuilding"),
            ("Cardio, Endurance & HIIT", "1 Month Cardio Burn"),
            ("Cardio, Endurance & HIIT", "6 Months Stamina Pro"),
            ("Functional Mobility & Yoga", "3 Months Zen Flow & Core"),
            ("VIP Elite Athlete Tier", "Annual All-Access VIP Pass"),
        ]
        pack_types = {}
        for cat_name, p_name in type_data:
            cat = categories.get(cat_name)
            pt, _ = Packagetype.objects.get_or_create(category=cat, packagename=p_name)
            pack_types[p_name] = pt

        # 5. Packages
        packages_info = [
            {
                "category": categories["Strength & Hypertrophy"],
                "packagename": pack_types["1 Month Pure Iron"],
                "titlename": "Starter Iron Pass",
                "packageduration": "1 Month",
                "price": "1499",
                "description": "Full access to Olympic free weights, barbell racks, and resistance machines. Includes free initial biometric analysis and standard gym locker.",
            },
            {
                "category": categories["Strength & Hypertrophy"],
                "packagename": pack_types["3 Months Hypertrophy Split"],
                "titlename": "Hypertrophy Beast",
                "packageduration": "3 Months",
                "price": "3999",
                "description": "Designed for maximum muscle synthesis. Includes customized 4-day PPL workout routine, bi-weekly coach check-ins, and free electrolyte recovery shakes.",
            },
            {
                "category": categories["Cardio, Endurance & HIIT"],
                "packagename": pack_types["6 Months Stamina Pro"],
                "titlename": "Endurance Master",
                "packageduration": "6 Months",
                "price": "6499",
                "description": "Unlimited treadmill theatre, assault bikes, rowing ergometers, and HIIT bootcamps. Complimentary VO2 max benchmark test included.",
            },
            {
                "category": categories["Functional Mobility & Yoga"],
                "packagename": pack_types["3 Months Zen Flow & Core"],
                "titlename": "Mobility & Core Flow",
                "packageduration": "3 Months",
                "price": "3499",
                "description": "Daily guided Ashtanga & Vinyasa yoga sessions, pelvic alignment workshops, myofascial release gear access, and steam room passes.",
            },
            {
                "category": categories["VIP Elite Athlete Tier"],
                "packagename": pack_types["Annual All-Access VIP Pass"],
                "titlename": "VIP Champion All-Access",
                "packageduration": "12 Months",
                "price": "12999",
                "description": "The ultimate fitness experience. 24/7 all-club access, 12 complimentary 1-on-1 personal trainer sessions, towel service, guest passes, and custom diet macro charts.",
            },
        ]

        created_packages = []
        for p in packages_info:
            pkg, _ = Package.objects.get_or_create(
                titlename=p["titlename"],
                defaults={
                    "category": p["category"],
                    "packagename": p["packagename"],
                    "packageduration": p["packageduration"],
                    "price": p["price"],
                    "description": p["description"],
                }
            )
            created_packages.append(pkg)

        # 6. Trainers
        trainers_data = [
            {
                "name": "Marcus Sterling",
                "role": "Head Strength & Olympic Coach",
                "speciality": "Barbell Mechanics, Powerlifting & Hypertrophy",
                "experience": "9+ Years Experience",
                "certifications": "CSCS (NSCA), USAW Level 2, Precision Nutrition L1",
                "bio": "Former national powerlifting competitor dedicated to helping athletes build bulletproof joints and record-breaking raw strength without injury.",
                "image_url": "first-trainer.jpg",
                "instagram": "@marcus_strength",
            },
            {
                "name": "Elena Rostova",
                "role": "Lead HIIT & Athletic Conditioning",
                "speciality": "VO2 Max, Functional Hyrox, Fat Loss Splits",
                "experience": "7+ Years Experience",
                "certifications": "ACE Master Trainer, CrossFit L-2, CPR/AED",
                "bio": "Specializes in high-density interval training and metabolic burn routines designed to maximize post-exercise oxygen consumption (EPOC).",
                "image_url": "second-trainer.jpg",
                "instagram": "@elena_conditioning",
            },
            {
                "name": "Aarav Sharma",
                "role": "Mobility & Holistic Performance Specialist",
                "speciality": "Ashtanga Yoga, Spinal Decompression & Core",
                "experience": "8+ Years Experience",
                "certifications": "RYT-500 Yoga Alliance, FMS Level 1 & 2",
                "bio": "Passionate about combining classical breathwork with modern functional movement to restore mobility in sedentary professionals and athletes.",
                "image_url": "third-trainer.jpg",
                "instagram": "@aarav_movement",
            },
            {
                "name": "Devin Miller",
                "role": "Senior Body Recomposition Coach",
                "speciality": "Hypertrophy Science, Calorie Periodization",
                "experience": "6+ Years Experience",
                "certifications": "ISSA Elite Trainer, NASM-CES",
                "bio": "Has guided over 350+ corporate clients through successful body transformations using sustainable habits and progressive overload.",
                "image_url": "training-image-01.jpg",
                "instagram": "@devin_fitbody",
            },
        ]

        for t in trainers_data:
            Trainer.objects.get_or_create(
                name=t["name"],
                defaults=t
            )

        # 7. Class Schedules
        schedules_data = [
            ("Dawn CrossFit WOD", "CrossFit", "Marcus Sterling", "Monday", "06:00 AM", "07:00 AM", "CrossFit Arena", "High Intensity"),
            ("Ashtanga Flow Yoga", "Yoga", "Aarav Sharma", "Monday", "07:30 AM", "08:30 AM", "Zen Studio", "Low / Restorative"),
            ("Heavy Iron Bench & Pull", "Strength", "Marcus Sterling", "Tuesday", "06:30 AM", "07:45 AM", "Free Weights Zone", "High Intensity"),
            ("HIIT Tabata Blitz", "HIIT", "Elena Rostova", "Tuesday", "06:00 PM", "07:00 PM", "Cardio Deck", "Extreme Cardio"),
            ("Hyrox Kettlebell Challenge", "HIIT", "Elena Rostova", "Wednesday", "07:00 AM", "08:00 AM", "Functional Turf", "High Intensity"),
            ("Mobility & Foam Roller Lab", "Yoga", "Aarav Sharma", "Thursday", "06:30 PM", "07:30 PM", "Recovery Spa Lounge", "Gentle / Mobility"),
            ("Olympic Clean & Jerk Workshop", "Strength", "Marcus Sterling", "Friday", "06:00 PM", "07:30 PM", "Olympic Platforms", "High Technical"),
            ("Weekend Warrior Boot Camp", "HIIT", "Elena Rostova", "Saturday", "08:00 AM", "09:30 AM", "Outdoor Rooftop Deck", "All Levels"),
        ]

        for s in schedules_data:
            ClassSchedule.objects.get_or_create(
                classname=s[0],
                day_of_week=s[3],
                start_time=s[4],
                defaults={
                    "category": s[1],
                    "trainer": s[2],
                    "end_time": s[5],
                    "room": s[6],
                    "intensity": s[7],
                }
            )

        # 8. Sample Booking & Payment for John Doe
        if created_packages:
            fav_pkg = created_packages[1]  # Hypertrophy Beast
            demo_booking, b_created = Booking.objects.get_or_create(
                register=member_signup,
                package=fav_pkg,
                defaults={
                    "bookingnumber": "8849201948",
                    "status": 3,  # Full Payment / Active
                }
            )
            if b_created:
                Paymenthistory.objects.get_or_create(
                    user=member_signup,
                    booking=demo_booking,
                    defaults={
                        "price": fav_pkg.price,
                        "status": 3,
                    }
                )

        # 9. Sample Contact Messages
        Contact.objects.get_or_create(
            email="rohit.mehta@yahoo.com",
            defaults={
                "name": "Rohit Mehta",
                "subject": "Corporate Gym Membership Inquiry",
                "message": "Hi Team, we have a 45-person tech firm in Bodakdev and would like to inquire about group annual fitness packages for our employees.",
            }
        )

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully! All demo records ready."))
