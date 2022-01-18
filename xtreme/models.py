from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
import requests
from pathlib import Path
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
# Create your models here.

class City(models.Model):
    cityName = models.CharField(max_length=20)

    def __str__(self):
        return self.cityName
    class Meta: #show the plural of city as cities instead of citys
        verbose_name_plural = 'cities'

class User(models.Model):
    name = models.CharField(max_length= 50)
    email= models.EmailField()
    city = models.ForeignKey(City, on_delete= models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

@receiver(post_save, sender= User)
def send_weather_email(sender, instance, **kwargs):
    subject = f'Hi {instance.name}, interested in our services.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [instance.email, ]
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=317b273c180693daa5b15540c80d198a'
    city = f'{instance.city}'
    city_weather = requests.get(url.format(city)).json()
    temperature = city_weather['main']['temp']
    description = city_weather['weather'][0]['description']
    icon =  city_weather['weather'][0]['icon']
    text_message = f'Hi {instance.name}, Weather report for {city}: {temperature}, {description} {icon}'
    
    html_message = f"""
    <!doctype html>
        <html lang=en>
            <head>
                <meta charset=utf-8>
                <title>Weather Report</title>
            </head>
            <body>
                <h1>{city}'s Weather Report</h1>
                <h2>Temperature : {temperature}, {description}</h2>
                <p>
                <img src = "http://openweathermap.org/img/w/{icon}.png" alt="Image">
                </p>
            </body>
        </html>
    """
    email = EmailMultiAlternatives(subject=subject, body=text_message, from_email=email_from, to=recipient_list)
    email.attach_alternative(html_message, "text/html")
    email.content_subtype = 'html'  
    email.mixed_subtype = 'related'  
    email.send()
