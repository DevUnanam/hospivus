from django.contrib import admin
from django.urls import path
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),

    # Include app URLs
    path('', include("core.urls")),
    path('', include("health_tech.urls")),
    path('', include("accounts.urls")),
    path('', include("email_campaign.urls")),
    path('', include("appointments.urls")),
    path('', include("bulletins.urls")),
    path('', include("giftshops.urls")),
    path('', include("tasks.urls")),
    path('', include("dm.urls")),
    path('', include("tv.urls")),
    # path('', include("payments.urls")),
    # path('', include("services.urls")),

    # API URLs
    path("api/accounts/", include("accounts.api.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)