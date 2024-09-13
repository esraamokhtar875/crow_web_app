import os

from django.utils import timezone
from django.utils.text import slugify
from django.db import models
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.core.validators import MaxValueValidator, MinValueValidator
from taggit.managers import TaggableManager
from accounts.models import CustomUser
# from apps.categories.models import Category

#======================= categories model ====================
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# ===================== Project Model =====================
class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, editable=False, blank=True)
    details = models.TextField()
    total_target = models.IntegerField()
    current_fund = models.IntegerField(default=0)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True)
    # category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=None, related_name='projects')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    tags = TaggableManager()
    updated_at = models.DateTimeField(auto_now=True)
    rate = models.FloatField(default=0, null=True, validators=[MinValueValidator(0.5), MaxValueValidator(5.0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    featured = models.BooleanField(default=False)
    featured_at = models.DateTimeField(default=None, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)

        # Check if current_fund has reached total_target and update status to 'completed'
        if self.current_fund >= self.total_target and self.status != 'completed':
            self.status = 'completed'

        # Check if featured field has changed and update featured_at
        if self.featured and not self.featured_at:
            self.featured_at = timezone.now()
        elif not self.featured:
            self.featured_at = None

        super(Project, self).save(*args, **kwargs)

    @classmethod
    def get_project_by_slug(cls, slug):
        return get_object_or_404(cls, slug=slug)

    @property
    def show_url(self):
        return reverse('project_details', args=[self.slug])

    @property
    def update_url(self):
        return reverse('update_project', args=[self.slug])

    @property
    def cancel_url(self):
        return reverse('cancel_project', args=[self.slug])

    @property
    def pictures_urls(self):
        return [pic.image.url for pic in self.pictures.all()]

    @property
    def picture_url(self):
        first_picture = self.pictures.first()
        if first_picture:
            return first_picture.image.url

    @property
    def get_tags(self):
        return self.tags.all()

    @property
    def percentag(self):
        if self.total_target == 0:
            return 0
        value = (self.current_fund * 100) / self.total_target
        return round(value, 2)


# ===================== ProjectPicture Model =====================
def project_picture_upload_path(instance, filename):
    if instance.project.pictures.exists():
        project_directory_name = os.path.dirname(instance.project.pictures.first().image.path)
    else:
        project_directory_name = instance.project.title.replace(' ', '_')
    return os.path.join('project_uploads', project_directory_name, filename)


class ProjectPicture(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="pictures")
    image = models.ImageField(db_column='image', upload_to=project_picture_upload_path)

    @property
    def image_url(self):
        return f"/media/{self.image}"


# ===================== Donation Model =====================
class Donation(models.Model):
    amount = models.IntegerField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='donations')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_DEFAULT, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.amount


# ===================== Comment Model =====================
class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,default=None, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# ===================== Reply Model =====================
class Reply(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE ,default=None, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class CommentReport(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=None, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# ===================== Report Project Model =====================
class ProjectReport(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=None, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# ===================== Rating Model =====================
class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=None, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ratings')
    value = models.FloatField(validators=[MinValueValidator(0.5), MaxValueValidator(5.0)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')

