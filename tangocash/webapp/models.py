from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models


# Currencies referenced by ISO 4217
class Currency(models.Model):
	name = models.CharField(max_length=50)
	id = models.CharField(primary_key=True, max_length=10)

	def __str__(self):
		return self.name
		
class Advertisement(models.Model):
	trader = models.ForeignKey(
		get_user_model(),
		on_delete=models.CASCADE
	)
	post_date = models.DateTimeField('date posted')
	ad_text = models.CharField(max_length=200)
	# ISO 4217
	currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
	location_point = models.PointField(geography=True)
	location_name = models.CharField(max_length=50)
	# google places id
	location_place_id = models.CharField(max_length=50)
	# is this ad selling or buying
	selling = models.BooleanField()
	price = models.IntegerField(default=0)
	markup = models.IntegerField(default=0)
	min_volume = models.IntegerField(default=0)
	max_volume = models.IntegerField(default=0)

	def __str__(self):
		return self.ad_text


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	phone_number = PhoneNumberField()
	score = models.IntegerField(default=0)
	localbitcoins_verified = models.BooleanField(default=False)
	localbitcoins_request = models.BooleanField(default=False)
	localbitcoins_username = models.CharField(max_length=30, blank=True)
	paxful_verified = models.BooleanField(default=False)
	paxful_request = models.BooleanField(default=False)
	paxful_username = models.CharField(max_length=30, blank=True)

	def __str__(self):
		return self.user.username

class Review(models.Model):
	# The person being reviewed
	trader = models.ForeignKey(
		get_user_model(),
		on_delete=models.CASCADE,
		related_name='reviews'
	)
	# The person doing the reviewing
	reviewer = models.ForeignKey(
		get_user_model(),
		on_delete=models.CASCADE,
		related_name='reviews_of_traders'
	)
	review_title = models.CharField(max_length=50)
	comment = models.CharField(max_length=200)
	score = models.IntegerField()
	
	def __str__(self):
		return self.review_title

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()