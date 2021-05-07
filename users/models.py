from django.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string
# from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
# from PIL import Image
from django.utils.html import strip_tags
# from .utils import id_generator
from django.contrib.auth.models import AbstractUser

# Create your models here.

# User = settings.AUTH_USER_MODEL


class User(AbstractUser):
    seller = models.BooleanField(default=False)
    customer = models.BooleanField(default=True)


class Profile(models.Model):
    """User Profile model.
    This model has a one-to-one relationship with the user model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='imgrepo/profile_pics')
    phone = models.CharField(max_length=11)

    # experience
    experience = models.CharField(max_length=120, null=True, blank=True)
    business_name = models.CharField(max_length=120, null=True, blank=True)

    # bank account details
    acc_number = models.CharField(max_length=50, blank=True, null=True)
    bank_name = models.CharField(max_length=150, blank=True, null=True)

    # Social Handles
    facebook = models.CharField(max_length=150, blank=True, null=True)
    twitter = models.CharField(max_length=150, blank=True, null=True)
    instagram = models.CharField(max_length=50, blank=True, null=True)

    # check if welcome email has been sent
    has_sent_welcome_email = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    # def save(self, *args, **kwargs):
    #     super(Profile, self).save(*args, **kwargs)

        # img = Image.open(self.image.path)

        # if img.height > 300 or img.width > 300:
        #     output_size = (300,300)
        #     img.thumbnail(output_size)
        #     img.save(self.image.path)

    """SENDING EMAIL TO NEW USERS"""
    def send_welcome_mail(self):
        print('Welcome message function!')
        context = {
        'name': self.user.username,
        'email': self.user.email,
        }
        subject = 'Welcome!'
        message = render_to_string('emails/welcome_email.html', context)
        plain_body = strip_tags(message)

        send_mail(
            subject,
            plain_body,
            'learnwithtusby@gmail.com',
            [self.user.email],
            html_message=message
            )



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
	instance.profile.save()

@receiver(post_save, sender=Profile)
def email_handler(sender, instance, **kwargs):
    # print(instance)
    # print('the post_save is working')
    profile = instance
    if profile.has_sent_welcome_email is False:
        profile.send_welcome_mail()
        profile.has_sent_welcome_email = True
        profile.save()
