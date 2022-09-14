from django.contrib.auth.models import User
from django.db.models.signals import post_save
from leads.models import UserProfile


def post_user_created_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)  # userprofile will be created iff new user will will create
        print(instance)


# post save will call after commit will be saved
post_save.connect(post_user_created_signal, sender=User)


