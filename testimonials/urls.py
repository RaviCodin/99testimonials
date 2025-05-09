from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    TestimonialViewSet,
    SampleCSVView,
    UploadCSVView,
    TestimonialImageViewSet,
    TestimonialVideoViewSet,
    ImportTestimonialView,
    TagViewSet,
    get_customer,
    get_customer_testimonials,
    update_testimonial_highlights,
)

router = DefaultRouter()
router.register(
    r"(?P<project_id>\d+)/testimonials", TestimonialViewSet, basename="testimonial"
)
router.register(
    r"testimonial-images", TestimonialImageViewSet, basename="testimonialimage"
)
router.register(
    r"testimonial-videos", TestimonialVideoViewSet, basename="testimonialvideo"
)
router.register(r"(?P<project_id>\d+)/tags", TagViewSet, basename="tag")

urlpatterns = router.urls

urlpatterns += [
    path("sample-csv/", SampleCSVView.as_view(), name="sample-csv"),
    path("upload-csv/<int:project_id>/", UploadCSVView.as_view(), name="upload-csv"),
    path(
        "import-testimonial/<int:project_id>/",
        ImportTestimonialView.as_view(),
        name="import-testimonial",
    ),
    path("get-customer/<uuid:customer_id>/", get_customer, name="get-customer"),
    path(
        "get-customer-testimonials/<uuid:customer_id>/",
        get_customer_testimonials,
        name="get-customer-testimonials",
    ),
    path(
        "update-testimonial-highlights/<int:testimonial_id>/",
        update_testimonial_highlights,
        name="update-testimonial-highlights",
    ),
]
