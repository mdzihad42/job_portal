
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import path, re_path
from job.views import*

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/',registerPage, name='registerPage'),
    path('',loginPage, name='loginPage'),
    path('logout/',logout_func, name='logout_func'),
    
    path('dashboard/',dashboard, name='dashboard'),
    path('profile/',profile,name='profile'),
    path('update-profile/',update_profile, name='update_profile'),
    
    path('job-list/',job_list, name='job_list'),
    path('add-job/',add_job, name='add_job'),
    path('update-job/<int:job_id>/',update_job, name='update_job'),
    path('delete-job/<int:job_id>/',delete_job, name='delete_job'),
    
    path('apply-job/<int:job_id>/',applied_job, name='applied_job'),
    path('my-applications/',my_application,name='my_application'),
    
    path('applicant-list/<int:job_id>/',applicant_list,name='applicant_list'),
    path('shortlisted/<int:applied_id>/',shortlisted, name='shortlisted'),
    path('rejected/<int:applied_id>/',rejected, name='rejected'),
    path('job_search/',job_search,name='job_search'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns+=re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
urlpatterns+=re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),