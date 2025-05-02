from django.contrib import admin
from .models import Testimonial, TestimonialImage, TestimonialVideo, Customer, TestimonialHighlight

admin.site.register(Testimonial)
admin.site.register(TestimonialImage)
admin.site.register(TestimonialVideo)
admin.site.register(Customer)
admin.site.register(TestimonialHighlight)
