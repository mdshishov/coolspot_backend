from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.conf import settings

from .models import CustomUser
from cart.models import Cart
from .permissions import ROLE_TO_GROUP


@receiver(post_save, sender=CustomUser)
def create_user_cart(sender, instance, created, **kwargs):
    if created and instance.is_client_role:
        Cart.objects.create(user=instance)

    if created and instance.is_staff_role:
        group_name = settings.ACCESS_GROUPS[ROLE_TO_GROUP[CustomUser.Role.STAFF]]
        group = Group.objects.get(name=group_name)

        instance.groups.add(group)


@receiver(post_migrate)
def create_groups(sender, **kwargs):
    for key, name in settings.ACCESS_GROUPS.items():
        staff_group, created = Group.objects.get_or_create(name=name)

        if key == ROLE_TO_GROUP[CustomUser.Role.STAFF]:
            permissions = Permission.objects.filter(
                codename__in=[
                    "view_dish",
                    "add_dish",
                    "change_dish",

                    "view_dishimage",
                    "add_dishimage",
                    "change_dishimage",
                    "delete_dishimage",

                    "view_tag",
                    "add_tag",
                    "change_tag",

                    "view_category",
                    "add_category",
                    "change_category",

                    "view_subcategory",
                    "add_subcategory",
                    "change_subcategory",

                    "view_orderdish",
                    "change_orderdish",
                    "add_orderdish",
                    "delete_orderdish",

                    "view_order",
                    "change_order",
                    "delete_order",

                    "view_customuser",
                ]
            )

            staff_group.permissions.add(*permissions)
