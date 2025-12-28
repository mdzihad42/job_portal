from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from job.models import *
from django.contrib import messages

def registerPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        display_name =  request.POST.get('display_name')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')
        password = request.POST.get('password')
        conf_password = request.POST.get('conf_password')
        
        username_exist = PortalUserModel.objects.filter(username=username).exists()
        
        if username_exist:
            messages.error(request, "Username already exists")
            return redirect('registerPage')
        
        if password == conf_password:
            user = PortalUserModel.objects.create_user(
                username=username,
                display_name =display_name,
                email=email,
                user_type=user_type,
                password=password
            )
            
            if user_type == 'Recruiters':
                EmployerModel.objects.create(employer=user)
            else:
                JobSeekerModel.objects.create(seeker=user)

            return redirect('loginPage')
        else:
            messages.error(request, 'Both password does not match')
            return redirect('registerPage')
    
    return render(request, 'auth/register.html')


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.warning(request, 'Invalid Credentials')
            return redirect('loginPage')
        
    return render(request, 'auth/login.html')

@login_required
def dashboard(request):
    current_user = request.user
    user_type = current_user.user_type

    if user_type == 'JobSeeker':
        seeker = JobSeekerModel.objects.get(seeker=current_user)
        user_skills = seeker.skills or ""
        matched_jobs = []
        all_jobs = JobPostModel.objects.all()
        for job in all_jobs:
            job_skills = job.skills_required or ""
            if any(skill.strip().lower() in job_skills.lower() for skill in user_skills.split(',')):
                matched_jobs.append(job)
        context = {
            'matched_jobs': matched_jobs,
            'user_type': user_type,
        }
    elif user_type == 'Recruiters':
        employer = EmployerModel.objects.get(employer=current_user)
        posted_jobs = JobPostModel.objects.filter(posted_by=employer)
        matched_seekers = []
        for job in posted_jobs:
            job_skills = job.skills_required or ""
            seekers = JobSeekerModel.objects.all()
            for seeker in seekers:
                seeker_skills = seeker.skills or ""
                if any(skill.strip().lower() in seeker_skills.lower() for skill in job_skills.split(',')):
                    matched_seekers.append({
                        'seeker': seeker,
                        'matching_job': job,
                    })
        context = {
            'matched_seekers': matched_seekers,
            'user_type': user_type,
        }
    else:
        return redirect('dashboard')
    
    return render(request, 'dashboard.html',context)


def logout_func(request):
    logout(request)
    return redirect('loginPage')

@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required
def update_profile(request):
    current_user = request.user
    user_type = current_user.user_type

    if request.method == 'POST':
      
        picture = request.FILES.get('profile_picture')

        if user_type == 'Recruiters':
            employer_data = EmployerModel.objects.get(employer=current_user)

            company_name = request.POST.get('company_name')
            address = request.POST.get('address')

            employer_data.company_name = company_name
            employer_data.address = address

            if picture:
                employer_data.profile_picture = picture

            employer_data.save()

        else:
            seeker_data = JobSeekerModel.objects.get(seeker=current_user)

            full_name = request.POST.get('full_name')
            contact_numer = request.POST.get('contact_numer')
            last_education = request.POST.get('last_education')
            skills = request.POST.get('skills')

            seeker_data.full_name = full_name
            seeker_data.contact_numer = contact_numer
            seeker_data.last_education = last_education
            seeker_data.skills = skills

            if picture:
                seeker_data.profile_picture = picture

            seeker_data.save()

        return redirect('profile')

    return render(request, 'update-profile.html')



@login_required
def job_list(request):
    current_user = request.user
    user_type = current_user.user_type
    
    if user_type == 'JobSeeker':
        job_data = JobPostModel.objects.all()
    else:
        job_data = JobPostModel.objects.filter(posted_by__employer=current_user)
        
    context = {
        'job_data': job_data
    }
    
    return render(request, 'jobs/job-list.html', context)

@login_required
def add_job(request):
    current_user = request.user
    if request.method == 'POST':
        job_title = request.POST.get('job_title')
        description = request.POST.get('description')
        number_of_openings = request.POST.get('number_of_openings')
        skills_required = request.POST.get('skills_required')
        salary = request.POST.get('salary')
        deadline = request.POST.get('deadline')
        
        user = EmployerModel.objects.get(employer=current_user)
        
        JobPostModel.objects.create(
            posted_by=user,
            job_title=job_title,
            description=description,
            number_of_openings=number_of_openings,
            skills_required=skills_required,
            salary=salary,
            deadline=deadline,
        )
        return redirect('job_list')
    
    return render(request, 'jobs/add-job.html')

@login_required
def update_job(request, job_id):
    job_data = JobPostModel.objects.get(id=job_id)
    
    if request.method == 'POST':
        job_data.job_title = request.POST.get('job_title')
        job_data.description = request.POST.get('description')
        job_data.number_of_openings=request.POST.get('number_of_openings')
        job_data.skills_required = request.POST.get('skills_required')
        job_data.salary = request.POST.get('salary')
        job_data.deadline = request.POST.get('deadline')
        job_data.save()
        
        return redirect('job_list')
    
    context = {
        'job_data': job_data
    }
    return render(request, 'jobs/update-job.html', context)

@login_required
def delete_job(request, job_id):
    JobPostModel.objects.get(id=job_id).delete()
    return redirect('job_list')

@login_required
def applied_job(request, job_id):
    job_data = JobPostModel.objects.get(id=job_id)
    current_user = request.user
    
    application_exists = ApplyJobModel.objects.filter(job=job_data).exists()
    if application_exists:
        messages.warning(request, 'Already Applied this job')
        return redirect('job_list')
    
    if request.method == 'POST':
        resume = request.FILES.get('resume')
        user = JobSeekerModel.objects.get(seeker=current_user)
        
        ApplyJobModel.objects.create(
            applied_by=user,
            job=job_data,
            resume=resume,
            status='Pending',
        )
        return redirect('my_application')

    context = {
        'job_data': job_data,
    }
    
    return render(request, 'applied_jobs/apply-job.html', context)

@login_required
def my_application(request):
    current_user = request.user
    job_data = ApplyJobModel.objects.filter(applied_by__seeker=current_user)
    
    context = {
        'job_data': job_data
    }
    
    return render(request, 'applied_jobs/my-application.html', context)

@login_required
def applicant_list(request, job_id):
    applicant_data = ApplyJobModel.objects.filter(job=job_id)
    
    context = {
        'applicant_data': applicant_data
    }
    
    return render(request, 'jobs/applicant-list.html', context)

@login_required
def shortlisted(request, applied_id):
    applied_job = ApplyJobModel.objects.get(id=applied_id)
    applied_job.status = 'Shortlisted'
    applied_job.save()
    return redirect('job_list')
    
@login_required
def rejected(request, applied_id):
    applied_job = ApplyJobModel.objects.get(id=applied_id)
    applied_job.status = 'Rejected'
    applied_job.save()
    return redirect('job_list')

@login_required
def job_search(request):
    current_user = request.user
    if current_user.user_type != 'JobSeeker':
        return redirect('dashboard')

    job_data = JobPostModel.objects.all()

    query = request.GET.get('q')
    skills = request.GET.get('skills')

    if query:
        job_data = job_data.filter(job_title__icontains=query)
    if skills:
        job_data = job_data.filter(skills_required__icontains=skills)

    context = {
        'job_data': job_data,
        'query': query or '',
        'skills': skills or '',
    }

    return render(request, 'jobs/job_search.html', context)



