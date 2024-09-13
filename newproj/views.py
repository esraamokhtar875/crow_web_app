import os
import re
import shutil

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from taggit.models import Tag

from .forms import ProjectForm, DonationForm, CommentForm, ReportProjectForm, ReportCommentForm
from .models import Project, ProjectPicture, Donation, Comment, Rating
from accounts.models import CustomUser


@login_required(login_url='login_')
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            user_instance = CustomUser.objects.get(pk=request.user.pk)
            project_pictures = request.FILES.getlist('pictures')
            tags = form.cleaned_data.get('tags', [])

            if len(project_pictures) == 0:
                messages.error(request, f'You should choose at least 1 picture.')
                return render(request, 'newproj/creat_proj.html', {'form': form})

            if len(tags) > 5:
                form.add_error('tags', "Maximum 5 tags allowed.")
            for tag in tags:
                if not re.match(r'^[a-zA-Z0-9_]+$', tag):
                    form.add_error('tags', "Tags can only contain letters, numbers, and underscore.")
                    break
            if form.errors:
                return render(request, 'newproj/creat_proj.html', {'form': form})

            project = form.save(commit=False)
            project.creator = user_instance
            project.save()
            form.save_m2m()

            for pic in project_pictures:
                ProjectPicture.objects.create(project=project, image=pic)

            return redirect('project_details', slug=project.slug)
    else:
        form = ProjectForm()
    return render(request, 'newproj/creat_proj.html', {'form': form})


@login_required(login_url='login_')
def rate_project(request, slug):
    if request.method == 'POST':
        project = get_object_or_404(Project, slug=slug)
        print(project, "rate")
        rating_value = float(request.POST.get('rating'))
        print(rating_value, "rate")
        current_user = CustomUser.objects.get(pk=request.user.pk)
        # if current_user.is_authenticated:
        # Check if the user has already rated the project
        existing_rating = Rating.objects.filter(user=current_user, project=project).first()
        if existing_rating:
            # Update existing rating
            existing_rating.value = rating_value
            existing_rating.save()
            messages.success(request, 'Your rating has been updated.')
        else:
            # Create a new rating object
            Rating.objects.create(user=current_user, project=project, value=rating_value)
            messages.success(request, 'Thank you for rating this project.')
        return JsonResponse({
            'success': True,
            'project_title': project.title,
            'project_slug': project.slug,
            'rating_value': rating_value,
        })
        # else:
        #     return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    else:
        # Return a JSON response indicating failure
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


def project_details(request, slug):
    project = get_object_or_404(Project, slug=slug)
    comments = project.comments.all()
    comments = Comment.objects.filter(project=project)
    # for comment in comments:
    #     comment.replies = Reply.objects.filter(comment=comment)
    # Calculate days left until end time

    end_datetime = project.end_time
    now_datetime = timezone.now()
    days_left = (end_datetime.date() - now_datetime.date()).days

    average_rating = project.ratings.aggregate(Avg('value'))['value__avg']
    print(average_rating, "avg")
    if average_rating is not None:
        project.rate = round(average_rating, 2)
        print(project.rate, "pro")
    else:
        project.rate = None

    project.save()

    user_rating = None
    if request.user.is_authenticated:
        current_user = request.user
        user_rating_obj = Rating.objects.filter(user=current_user, project=project).first()
        if user_rating_obj:
            user_rating = user_rating_obj.value

    related_projects = Project.objects.filter(tags__in=project.tags.all()).exclude(id=project.id).distinct()[:4]
    for related_project in related_projects:
        end_datetime = related_project.end_time
        now_datetime = timezone.now()
        days_left = (end_datetime.date() - now_datetime.date()).days
        related_project.days_left = days_left

    first_donation = Donation.objects.filter(project=project).order_by('created_at').first()
    last_donation = Donation.objects.filter(project=project).order_by('-created_at').first()
    top_donation = Donation.objects.filter(project=project).aggregate(Max('amount'))['amount__max']
    top_donation_user = CustomUser.objects.filter(
        donation__amount=Donation.objects.aggregate(max_amount=Max('amount'))['max_amount']).first()

    # if project.total_target != 0:
    #     current_fund_percentage = round((project.current_fund / project.total_target) * 100, 2)
    # else:
    #     current_fund_percentage = 0  # Handle division by zero case

    num_donors = Donation.objects.filter(project=project).values('user').distinct().count()

    allow_cancel = False
    if request.user.id == project.creator.id and project.percentag < 25:
        allow_cancel = True

    context = {
        'project': project,
        'comments': comments,
        'days_left': days_left,
        'user_rating': user_rating,
        'average_rating': average_rating,
        'related_projects': related_projects,
        'first_donation': first_donation,
        'last_donation': last_donation,
        'top_donation': top_donation,
        'top_donation_user': top_donation_user,
        'num_donors': num_donors,
        # 'current_fund_percentage': current_fund_percentage,
        'allow_cancel': allow_cancel,
    }
    return render(request, 'newproj/project_details.html', context)


def projects_list(request):
    projects = Project.objects.all().filter(status='active')
    return render(request, 'newproj/index.html', {'projects': projects})


def tagged(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    projects = Project.objects.filter(tags=tag, status='active')
    return render(request, 'newproj/tagged.html', {'tag': tag, 'projects': projects})


@login_required(login_url='login_')
def cancel_project(request, slug):
    project = Project.get_project_by_slug(slug)
    project_directory = os.path.join(settings.MEDIA_ROOT, 'project_uploads', project.title.replace(' ', '_'))

    current_fund = project.current_fund
    recipient_project = Project.objects.filter(category=project.category).exclude(pk=project.pk).first()

    # add the current fund of that project to another project in the same category
    if recipient_project:
        recipient_project.current_fund += current_fund
        recipient_project.save()

    else:
        # If no project in the same category, transfer the funds to any available project
        recipient_project = Project.objects.exclude(pk=project.pk).first()
        recipient_project.current_fund += current_fund
        recipient_project.save()

    # Delete the project directory
    if os.path.exists(project_directory):
        shutil.rmtree(project_directory)

    project.delete()
    return redirect('/')


@login_required(login_url='login_')
def add_donation(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        donation_form = DonationForm(request.POST)
        if donation_form.is_valid():
            donation = donation_form.save(commit=False)
            donation.project = project
            user_instance = CustomUser.objects.get(pk=request.user.pk)
            donation.user = user_instance
            project.current_fund += donation.amount
            if project.current_fund > project.total_target:
                messages.error(request, 'please enter a donation amount lower than the total target')
                return render(request, 'newproj/project_details.html', {'project': project})
            donation.save()
            project.save()
            messages.success(request, 'Thank you for your donation!')
            return redirect('project_details', slug=slug)
    else:
        donation_form = DonationForm()
    return render(request, 'newproj/project_details.html', {'donation_form': donation_form, 'project': project})


@login_required(login_url='login_')
def add_comment(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.project = project
            user_instance = CustomUser.objects.get(pk=request.user.pk)
            comment.user = user_instance
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('project_details', slug=slug)
    else:
        comment_form = CommentForm()
    return render(request, 'newproj/add_comment.html', {'comment_form': comment_form, 'project': project})

@login_required(login_url='login_')
def report_project(request, slug):
    project = Project.get_project_by_slug(slug)
    if request.method == 'POST':
        report_project_form = ReportProjectForm(request.POST)
        if report_project_form.is_valid():
            report = report_project_form.save(commit=False)
            report.project = project
            user_instance = CustomUser.objects.get(pk=request.user.pk)
            report.user = user_instance
            report.save()
            messages.success(request, 'Thank you for reporting this project!')
            return redirect('project_details', slug=slug)
    else:
        report_project_form = ReportProjectForm()
    return render(request, 'newproj/project_details.html',
                  {'report_project_form': report_project_form, 'project': project})


@login_required(login_url='login_')
def report_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        report_comment_form = ReportCommentForm(request.POST)
        if report_comment_form.is_valid():
            report = report_comment_form.save(commit=False)
            report.comment = comment
            user_instance = CustomUser.objects.get(pk=request.user.pk)
            report.user = user_instance
            report.save()
            messages.success(request, 'Thank you for reporting this comment!')
            return redirect('project_details', slug=comment.project.slug)
    else:
        report_comment_form = ReportCommentForm()
    return render(request, 'newproj/project_details.html',
                  {'report_comment_form': report_comment_form, 'comment': comment})

