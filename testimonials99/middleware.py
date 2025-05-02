from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from campaigns.models import Campaign
from displays.models import Display
from django.utils import timezone
from django.conf import settings
from django.shortcuts import render


class CustomCorsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

class CampaignDomainMiddleware(MiddlewareMixin):
    def process_request(self, request):
        full_domain = request.get_host().lower()

        # Skip middleware if accessing main application domain
        if full_domain == settings.MAIN_DOMAIN or full_domain in settings.ALLOWED_HOSTS:
            return None

        # Check if it's a subdomain request
        if '.' in full_domain:
            subdomain = full_domain.split(':')[0]
            
            try:
                # Find campaign with matching custom subdomain
                campaign = Campaign.objects.get(
                    custom_subdomain=subdomain,
                )
                campaign.verification_status=True
                campaign.save()

                # Store campaign in request for use in views
                request.campaign = campaign
                
                # Update last checked timestamp
                campaign.last_checked_at = timezone.now()
                campaign.save(update_fields=['last_checked_at'])
                context = {
                   'CAMPAIGN': campaign.id
                }
                return render(request, 'index.html',context)
                
            except Campaign.DoesNotExist:
                pass
            
            try:
                display = Display.objects.filter(custom_subdomain=subdomain).first()
                context = {
                    'DISPLAY':display.id
                }
                return render(request,'index.html',context)
            except Exception as e:
                pass

        return None
