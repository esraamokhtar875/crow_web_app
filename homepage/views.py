from django.shortcuts import render,get_object_or_404
from django.db.models import Avg, Count
from taggit.models import Tag
from .forms import SearchForm
from django.utils import timezone
from django.http import JsonResponse
from newproj.models import Project, Category
# from apps.models import Category
from accounts.models import CustomUser

# Create your views here.

def home_page(request):
    top_projects = Project.objects.filter(status='active', end_time__gt=timezone.now()).order_by('-rate')[:5]
    categories = Category.objects.all()
    categories_projects=Project.objects.all()
    for project in categories_projects:
        percentage = project.current_fund * 100 / project.total_target
        project.percentage = "{:.3f}".format(percentage)

    latest_projects = Project.objects.filter(status='active').order_by('-start_time')[:5]
    for project in latest_projects:
        percentage = project.current_fund * 100 / project.total_target
        project.percentage = "{:.3f}".format(percentage)

    featured_projects = Project.objects.filter(featured=True,status='active').order_by('-featured_at')[:5]
    for project in featured_projects:
        percentage = project.current_fund * 100 / project.total_target
        project.percentage = "{:.3f}".format(percentage)

    return render(request, 'index.html',context = {'top_projects':top_projects,
                                                            'latest_projects': latest_projects,
                                                            'featured_projects':featured_projects,
                                                            'categories':categories,
                                                            'categories_projects':categories_projects,
                                                            })

def get_projects_by_category_id(request):
    category_id = request.GET.get('category_id')
    if category_id:
        projects = Project.objects.filter(category_id=category_id,status='active')
    else:
        projects = Project.objects.all()

    for project in projects:
        percentage = project.current_fund * 100 / project.total_target
        project.percentage = "{:.3f}".format(percentage)

    data = [{'id': project.id, 'title': project.title, 'details': project.details, 
             'picture_url': project.picture_url, 'current_fund': project.current_fund, 
             'total_target': project.total_target,'slug':project.slug, 'percentage': project.percentage} 
            for project in projects]

    return JsonResponse({'projects': data})
    
def search(request):
    form = SearchForm(request.GET)
    results = []

    if form.is_valid():
        search_option = form.cleaned_data['search_option']
        query = form.cleaned_data['query'].strip()  # Remove leading/trailing spaces

        if search_option == 'project':
            results = Project.objects.filter(title__icontains=query)
            print(results)
        elif search_option == 'tag':
            # Filter projects by tags
            results = Project.objects.filter(tags__name__icontains=query)
            print(results)
        else:
            results = []
    else:
        results = []

    return render(request, 'search_results.html', {'searchForm': form, 'searchResults': results})
 
    
