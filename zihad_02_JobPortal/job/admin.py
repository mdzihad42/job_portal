from django.contrib import admin
from job.models import *

admin.site.register(PortalUserModel)
admin.site.register(EmployerModel)
admin.site.register(JobSeekerModel)
admin.site.register(JobPostModel)
admin.site.register(ApplyJobModel)
