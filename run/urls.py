from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
  url(r'^/?$', 'run.views.index', name="report-current"),
  url(r'^(?P<year>\d{4})/(?P<week>\d{2})/excel$', 'run.views.excel', name="report_excel"),
)
