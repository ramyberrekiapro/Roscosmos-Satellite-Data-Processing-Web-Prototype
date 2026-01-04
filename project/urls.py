from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from files import views as files_views
from files import views

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    # path('', RedirectView.as_view(url='/en/'), name='index'),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', files_views.landing, name='landing'),
    path('viewer/', include('files.urls', namespace='files')),
    path('howto/', views.howto_view, name='howto'),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)