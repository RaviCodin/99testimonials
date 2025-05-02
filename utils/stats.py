from django.db.models import Q
from django.db.models import Count
from testimonials.models import Testimonial
from projects.models import Project
from campaigns.models import Campaign


def get_user_stats(user):
    testimonials = Testimonial.objects.filter(project__owner=user).count()
    video_testimonials = Testimonial.objects.filter(
        project__owner=user, videos__isnull=False).count()
    campaigns = Campaign.objects.filter(project__owner=user).count()
    projects = Project.objects.filter(
        Q(owner=user) | Q(collaborators=user)).distinct().count()
    staff = Project.objects.filter(
        Q(owner=user) | Q(collaborators=user)
    ).values('collaborators').distinct().count()
    return {
        'testimonials': testimonials,
        'video_testimonials': video_testimonials,
        'campaigns': campaigns,
        'projects': projects,
        'staff': staff,
    }
