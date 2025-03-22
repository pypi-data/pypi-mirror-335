from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from artd_alliance.models import Alliance
import random
import string
from artd_promotion.models import Coupon
from datetime import timedelta
from artd_partner.models import Partner


@receiver(post_migrate)
def execute_after_migrations(sender, **kwargs):
    from artd_modules.utils import create_or_update_module_row

    create_or_update_module_row(
        slug="artd_alliance",
        name="ArtD Alliance",
        description="ArtD Alliance",
        version="1.0.7",
        is_plugin=False,
    )


def generate_aleatory_string(length: int = 20) -> str:
    """
    Generates a random string of a specified length, composed of
    uppercase and lowercase letters and digits.

    Parameters:
    length (int): Length of the generated string. Default is 20.

    Returns:
    str: Randomly generated string.
    """
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def generate_unique_code_alliance() -> str:
    """
    Generates a unique code for the Alliance model. Ensures that
    the generated code does not already exist in the database.

    Returns:
    str: A unique code that does not conflict with existing Alliance codes.
    """
    from artd_alliance.models import Alliance

    while True:
        code = generate_aleatory_string(50)
        if not Alliance.objects.filter(code_alliance=code).exists():
            return code


def generate_unique_code_coupon(partner_slug: str) -> str:
    """
    Generates a unique code for the Coupon model. Ensures that
    the generated code does not already exist in the database.

    Returns:
    str: A unique code that does not conflict with existing Coupon codes.
    """
    from artd_alliance.models import Coupon

    while True:
        code = partner_slug + "_" + generate_aleatory_string(10)
        if not Coupon.objects.filter(code=code).exists():
            return code


@receiver(post_save, sender=Alliance)
def alliance_post_save(sender, instance: Alliance, created: bool, **kwargs) -> None:
    """
    Signal handler for the Alliance model to generate a unique `code_alliance`
    upon creation, using specified prefix and suffix if available. Also, if
    the alliance is active and `generate_coupons` is True, initiates coupon
    creation based on the `coupon_quantity`.

    Parameters:
    sender (Type[Alliance]): The model class that sent the signal.
    instance (Alliance): The instance of the Alliance model being saved.
    created (bool): True if a new record was created, False if updated.
    **kwargs: Additional keyword arguments.
    """
    alliance = instance
    if created:
        # Generate unique alliance code with prefix/suffix if provided
        coupon_code = generate_unique_code_alliance()
        if alliance.coupon_prefix:
            coupon_code = f"{alliance.coupon_prefix}_{coupon_code}"
        if alliance.coupon_suffix:
            coupon_code = f"{coupon_code}_{alliance.coupon_suffix}"

        alliance.code_alliance = coupon_code
        alliance.save()

    else:
        if alliance.alliance_status == "active":
            if alliance.coupons.count() > 0:
                """
                coupons don't exist, create them
                """
                coupons = alliance.coupons.all()
                for coupon in coupons:
                    the_coupon: Coupon = coupon
                    if the_coupon.uses < the_coupon.uses_per_coupon:
                        the_coupon.status = True
                        the_coupon.save()
            else:
                if alliance.start_at:
                    start_at = alliance.start_at
                else:
                    start_at = alliance.created_at

                if alliance.end_at:
                    end_at = alliance.end_at
                else:
                    end_at = alliance.created_at + timedelta(days=365)
                coupon_quantity = alliance.coupon_quantity
                coupons = []
                partner: Partner = alliance.partner
                coupon_is_percentage = False
                if alliance.benefit_type == "percentage":
                    coupon_is_percentage = True

                for _ in range(coupon_quantity):
                    specific_coupon_code = generate_unique_code_coupon(
                        partner.partner_slug,
                    )
                    coupon = Coupon.objects.create(
                        partner=partner,
                        code=specific_coupon_code,
                        name=alliance.benefit,
                        start_date=start_at,
                        end_date=end_at,
                        is_percentage=coupon_is_percentage,
                        value=alliance.value,
                        uses_per_coupon=alliance.uses_per_coupon,
                    )
                    coupons.append(coupon)

                alliance.coupons.add(*coupons)

        elif alliance.alliance_status == "inactive":
            coupons = alliance.coupons.all()
            for coupon in coupons:
                the_coupon: Coupon = coupon
                the_coupon.status = False
                the_coupon.save()
