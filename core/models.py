from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.utils.text import slugify
# from django_countries.fields import CountryField
# from PIL import Image

# Create your models here.

# This manager helps to display the required categories on the homepage
# Just 4 categories will be displayed on the homepage.
class CategoryManager(models.Manager):
    def first_cat(self):
        if super(CategoryManager, self).all().order_by('-id').exists():
            return super(CategoryManager, self).all().order_by('-id')[0]
    def second_cat(self):
        if super(CategoryManager, self).count() >= 2:
            return super(CategoryManager, self).all().order_by('-id')[1]
        else:
            return None
    def third_cat(self):
        if super(CategoryManager, self).count() >= 3:
            return super(CategoryManager, self).all().order_by('-id')[2]
        else:
            return None
    def fourth_cat(self):
        if super(CategoryManager, self).count() >= 4:
            return super(CategoryManager, self).all().order_by('-id')[3]
        else:
            return None

class Category(models.Model):
    name = models.CharField(max_length=120)

    # objects = CategoryManager()

    def __str__(self):
        return self.name


class Item(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    image = models.ImageField(
        upload_to='imgrepo/products/')
    downloadable_file = models.FileField(upload_to='imgrepo/downloadable-files/', help_text='Please upload as a zip file.')
    price = models.FloatField()
    discount_price = models.FloatField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    description = models.CharField(max_length=150)
    dimension = models.CharField(max_length=50, default='1920x1080', help_text='1920x1080, 2400x1600')
    format = models.CharField(max_length=50, default='JPG', help_text='JPG, PNG etc.')

    # use this value to determine if the item is still in stock.
    quantity = models.IntegerField(default=10000000000)
    downloads = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(
        default='',
        editable=False,
        max_length=120,
    )

    class Meta:
        unique_together = ('name', 'slug')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        value = self.name
        self.slug = slugify(value, allow_unicode=True)
        super(Item, self).save(*args, **kwargs)

        # img = Image.open(self.image.path)

        # if img.height != 236 or img.width != 420:
        #     output_size = (420,236)
        #     img.thumbnail(output_size)
        #     img.save(self.image.path)

    def get_absolute_url(self):
        return reverse('core:item-detail', kwargs={
            'slug': self.slug
            })

    def get_add_to_cart_url(self):
        return reverse('core:add-to-cart', kwargs={
            'slug':self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse('core:remove-from-cart', kwargs={
            'slug':self.slug
        })
    # This function gets the price based on the quantity
    def get_total_item_price(self):
        return self.downloads * self.price

    # gets the total_price using discount_price
    def get_total_discount_item_price(self):
        return self.downloads * self.discount_price

    # returns the price depending on either discounted or not.
    def get_earning(self):
        if self.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()



class OrderItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    # This function gets the price based on the quantity
    def get_total_item_price(self):
        return self.quantity * self.item.price

    # gets the total_price using discount_price
    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    # returns the price depending on either discounted or not.
    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=120, default='ABC', unique=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    # returns the total price of all order_items in a cart
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

class Payment(models.Model):
    paystack_transaction_id = models.CharField(max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username