# Generated by Django 5.1.4 on 2024-12-18 01:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_tagcategory_tag'),
        ('testimonials', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testimonial',
            name='images',
        ),
        migrations.RemoveField(
            model_name='testimonial',
            name='tag',
        ),
        migrations.AddField(
            model_name='testimonial',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='testimonials', to='projects.tag'),
        ),
        migrations.AlterField(
            model_name='testimonial',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='testimonial',
            name='rating',
            field=models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]),
        ),
        migrations.CreateModel(
            name='TestimonialImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='testimonial_images/')),
                ('testimonial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='testimonials.testimonial')),
            ],
        ),
        migrations.CreateModel(
            name='TestimonialVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(upload_to='testimonial_videos/')),
                ('testimonial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='testimonials.testimonial')),
            ],
        ),
    ]
