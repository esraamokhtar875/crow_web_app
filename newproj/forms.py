from django.utils import timezone
from django import forms
from taggit import forms as taggit_forms

from .models import Project, Donation, Comment, ProjectReport, CommentReport


class ProjectForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Title", "class": "form-control"})
    )

    details = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Details", "class": "form-control", "rows": 5}),
    )

    total_target = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "Total Target", "class": "form-control", "min": "0"}),
    )

    start_time = forms.DateField(
        widget=forms.DateInput(attrs={"placeholder": "Start Date", "type": "date", "class": "form-control", "readonly": True}),
        required=False,
        initial=timezone.now(),
    )

    end_time = forms.DateField(
        widget=forms.DateInput(attrs={"placeholder": "End Date", "type": "date", "class": "form-control"})
    )

    tags = taggit_forms.TagField(
        widget=forms.TextInput(attrs={"placeholder": "Tags", "class": "form-control"}),
        required=False
    )
    # remove catgery   >>>>> , 'category'
    class Meta:
        model = Project
        fields = ('title', 'details', 'end_time', 'total_target', 'tags')

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters long.")
        elif Project.objects.filter(title=title).exists() and self.instance.title != title:
            raise forms.ValidationError("A project with this title already exists.")
        return title

    def clean_total_target(self):
        total_target = self.cleaned_data.get('total_target')
        if total_target is not None and total_target <= 0:
            raise forms.ValidationError("Total Target must be a positive number.")
        return total_target

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and end_time <= start_time:
            self.add_error("end_time", "End time should be greater than Start time.")


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount']
        labels = {
            'amount': 'Donation Amount (EGP)'
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter donation amount'})
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Donation amount should be greater than zero.")
        return amount


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'Add a comment'
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your comment here'})
        }


class ReportProjectForm(forms.ModelForm):
    class Meta:
        model = ProjectReport
        fields = ['reason']
        labels = {
            'reason': 'Reason for Report'
        }
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Please provide details about why you are reporting this project.'})
        }


class ReportCommentForm(forms.ModelForm):
    class Meta:
        model = CommentReport
        fields = ['reason']
        labels = {
            'reason': 'Reason for Report'
        }
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Please provide details about why you are reporting this comment.'})
        }


class ReplyCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'Reply to comment'
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your reply here'})
        }