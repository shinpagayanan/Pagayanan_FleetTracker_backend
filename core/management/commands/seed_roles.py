# from django.core.management.base import (
#     BaseCommand
# )

# from core.models import User


# class Command(BaseCommand):

#     help = (
#         "Create default system users"
#     )

#     def handle(
#         self,
#         *args,
#         **kwargs
#     ):

#         users = [

#             {
#                 "username": "manager",
#                 "password": "manager123",
#                 "role": User.MANAGER,
#                 "first_name": "Shane",
#                 "last_name": "Pagayanan",
#                 "email": "john.doe@example.com",
#             },

#             {
#                 "username": "auditor",
#                 "password": "auditor123",
#                 "role": User.AUDITOR,
#                 "first_name": "Jane",
#                 "last_name": "Smith",
#                 "email": "jane.smith@example.com",
#             },

#             {
#                 "username": "staff1",
#                 "password": "staff123",
#                 "role": User.STAFF,
#                 "first_name": "Michael",
#                 "last_name": "Johnson",
#                 "email": "michael.johnson@example.com",
#             },

#             {
#                 "username": "staff2",
#                 "password": "staff123",
#                 "role": User.STAFF,
#                 "first_name": "Emily",
#                 "last_name": "Davis",
#                 "email": "emily.davis@example.com",
#             },
#         ]

#         for data in users:

#             username = data[
#                 "username"
#             ]

#             if User.objects.filter(
#                 username=username
#             ).exists():

#                 self.stdout.write(
#                     self.style.WARNING(
#                         f"{username} already exists"
#                     )
#                 )

#                 continue

#             user = User.objects.create_user(

#                 username=data["username"],

#                 password=data["password"],

#                 role=data["role"],

#                 first_name=data["first_name"],

#                 last_name=data["last_name"],

#                 email=data["email"],
#             )

#             self.stdout.write(
#                 self.style.SUCCESS(
#                     f"Created {user.username}"
#                 )
#             )

#         self.stdout.write(
#             self.style.SUCCESS(
#                 "Role seeding completed."
#             )
#         )