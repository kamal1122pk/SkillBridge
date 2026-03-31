from django.contrib import admin
from .models import Profile, PortfolioMedia, Job, Order, Review, OTP, Conversation, Message, Application

# Register your models here.
admin.site.register(Profile)
admin.site.register(PortfolioMedia)
admin.site.register(Job)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(OTP)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Application)
