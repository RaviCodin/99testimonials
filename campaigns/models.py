from django.db import models
from projects.models import Project
import uuid
import dns.resolver

def verify_cname_record(host, expected_target):
    try:
        answers = dns.resolver.resolve(host, 'CNAME')
        for rdata in answers:
            if expected_target in rdata.to_text():
                return True
        return False
    except:
        return False


class Campaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField(blank=True, default='')
    logo = models.ImageField(
        upload_to='campaign_logos/', null=True, blank=True)
    primaryColor = models.CharField(max_length=7, default='#000000')
    backgroundColor = models.CharField(max_length=7, default='#ffffff')
    textColor = models.CharField(max_length=7, default='#000000')
    fontFamily = models.CharField(max_length=255, default='Arial')
    welcomeTitle = models.CharField(max_length=255, blank=True, default='')
    welcomeNote = models.TextField(blank=True, default='')
    textCheckbox = models.BooleanField(default=False)
    videoCheckbox = models.BooleanField(default=False)
    textButtonName = models.CharField(max_length=255, blank=True, default='')
    videoButtonName = models.CharField(max_length=255, blank=True, default='')
    responseTitle = models.CharField(max_length=255, blank=True, default='')
    responseInstructions = models.TextField(blank=True, default='')
    textResponseActionName = models.CharField(
        max_length=255, blank=True, default='Submit')
    videoResponseTitle = models.CharField(
        max_length=255, blank=True, default='')
    videoResponseInstructions = models.TextField(blank=True, default='')
    collectStarRating = models.BooleanField(default=False)
    collectImageFiles = models.BooleanField(default=False)
    videoCollectStarRating = models.BooleanField(default=False)
    videoCollectImageFiles = models.BooleanField(default=False)

    customerDetailsTitle = models.TextField(blank=True, default='')
    gatherEmailEnabled = models.BooleanField(default=False)
    gatherEmailRequired = models.BooleanField(default=False)

    captureCompanyName = models.BooleanField(default=False)
    captureCompanyNameRequired = models.BooleanField(default=False)

    captureJobTitleEnabled = models.BooleanField(default=False)
    captureJobTitleRequired = models.BooleanField(default=False)

    collectUserPhotoEnabled = models.BooleanField(default=False)
    collectUserPhotoRequired = models.BooleanField(default=False)
    acquireWebsiteUrlEnabled = models.BooleanField(default=False)
    acquireWebsiteUrlRequired = models.BooleanField(default=False)

    gatherCompanyLogoEnabled = models.BooleanField(default=False)
    gatherCompanyLogoRequired = models.BooleanField(default=False)

    thankYouTitle = models.CharField(max_length=255, blank=True, default='')
    thankYouNote = models.TextField(blank=True, default='')
    callToActionEnabled = models.BooleanField(default=False)
    callToActionLabel = models.CharField(
        max_length=255, blank=True, default='')
    callToActionUrl = models.URLField(blank=True, default='')

    shareLink = models.BooleanField(default=True)
    shareFacebook = models.BooleanField(default=True)
    shareTiktok = models.BooleanField(default=True)
    shareInstagram = models.BooleanField(default=True)
    shareLinkedin = models.BooleanField(default=True)
    shareTwitter = models.BooleanField(default=True)
    shareWhatsapp = models.BooleanField(default=True)

    removeBranding = models.BooleanField(default=True)

    custom_subdomain = models.CharField(max_length=255, blank=True, default='')
    verification_status = models.BooleanField(default=False)
    last_checked_at = models.DateTimeField(null=True, blank=True, default=None)

    project = models.ForeignKey(
        Project, related_name='campaigns', on_delete=models.CASCADE)

    def check_dns_status(self, expected_target):
        if self.custom_subdomain:
            return verify_cname_record(self.custom_subdomain, expected_target)
        return False

        return self.name
