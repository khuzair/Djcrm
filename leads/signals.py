from django.contrib.auth.models import User
from django.db.models.signals import post_save
from leads.models import UserProfile


def post_user_created_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        print(instance)
        
        
post_save.connect(post_user_created_signal, sender=User)


