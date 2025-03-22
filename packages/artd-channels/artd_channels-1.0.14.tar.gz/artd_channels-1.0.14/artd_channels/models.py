from django.db import models
from artd_customer.models import Customer
from slugify import slugify


# Create your models here.
class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} (id: {self.id})"


class Channel(Base):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Channel, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Provider(Base):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Provider, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Credential(Base):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    credentials = models.JSONField()

    def __str__(self):
        return f"{self.provider} - {self.channel.name}"


class Messagge(Base):
    messages = models.CharField(max_length=1000)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    result = models.JSONField()
    retries = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.customer.name} - {self.channel.name}"


class CustomerChannel(Base):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("order", "customer")
        unique_together = ("channel", "customer")

    def __str__(self):
        return f"{self.customer.name} - {self.channel.name}"
