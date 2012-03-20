# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

from lizard_ui.urls import debugmode_urlpatterns
from lizard_maptree.views import MaptreeHomepageView

admin.autodiscover()

ITEM_MODELS = ['']

urlpatterns = patterns(
    '',
    url(r'^$',
        MaptreeHomepageView.as_view(),
        {'item_models': ITEM_MODELS},
        name='lizard_wms.homepage'),
    #url(r'^admin/', include(admin.site.urls)),
    # url(r'^something/',
    #     direct.import.views.some_method,
    #     name="name_it"),
    )
urlpatterns += debugmode_urlpatterns()
