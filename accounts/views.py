from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django_countries import countries

from .models import CustomUser
from .forms import RegistrationForm, LoginForm, ChangePasswordForm, ResetPasswordForm, EditProfileForm
from .tokens import account_activation_token
# from apps.projects.models import Project, Donation


def send_email_activation(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("registration/verify_email_message.html", {
        'request': request,
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = 'html'
    if email.send():
        messages.success(request, f'Dear {user}, please go to your email {to_email}inbox and click on \
                received activation link to confirm and complete the registration. Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login_')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('/')


def create_user(request):
    if request.user.is_authenticated:
        return redirect('/')
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            if request.FILES:
                user.profile_picture = form.cleaned_data["profile_picture"]
            user.save()
            email = form.cleaned_data.get('username')
            send_email_activation(request, user, email)
            return redirect('/')
    return render(request, 'registration/register.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            User = get_user_model()

            # Admin login condition
            if username == 'admin@admin.com' and password == 'ADMIN@12345':
                try:
                    user = User.objects.get(username=username)
                    # Set backend explicitly
                    user.backend = 'django.contrib.auth.backends.ModelBackend'  # Default Django backend
                    login(request, user)
                    return redirect('admin_dashboard')
                except User.DoesNotExist:
                    form.add_error(None, 'Admin account not found.')

            # Regular user login
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None

            # Check if the user exists and the password is correct
            if user is not None and user.check_password(password):
                if user.is_active:
                    # Explicitly set the backend attribute before logging in
                    user.backend = 'django.contrib.auth.backends.ModelBackend'  # Adjust this if you are using other backends
                    login(request, user)
                    # return redirect('home.html')
                    return redirect(f'/accounts/profile/{user.id}/')

                    # return redirect('/')
                else:
                    # User is not active
                    activation_deadline = user.date_joined + timezone.timedelta(days=1)
                    if activation_deadline < timezone.now():
                        send_email_activation(request, user, username)
                        form.add_error(None,
                                       'Account activation link expired. Resent activation link, please check your email.')
                    else:
                        form.add_error(None,
                                       'Your account is not yet activated. Please check your email for activation instructions.')
            else:
                form.add_error(None, 'Your email or password is incorrect.')
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})
# def login_user(request):
#     if request.user.is_authenticated:
#         return redirect('/')
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             User = get_user_model()
#
#             if username == 'admin@admin.com' and password == 'ADMIN@12345':
#                 user = User.objects.get(username=username)
#                 login(request, user)
#                 return redirect('admin_dashboard')
#
#             try:
#                 user = User.objects.get(username=username)
#             except User.DoesNotExist:
#                 user = None
#             # Check if the user exists and the password is correct
#             if user is not None and user.check_password(password):
#                 if user.is_active:
#                     login(request, user)
#                     return redirect('/')
#
#                 else:
#                     # User is not active
#                     activation_deadline = user.date_joined + timezone.timedelta(days=1)
#                     if activation_deadline < timezone.now():
#                         send_email_activation(request, user, username)
#                         form.add_error(None, 'Account activation link expired. Resent activation link, please check your email.')
#                     else:
#                         form.add_error(None, 'Your account is not yet activated. Please check your email for activation instructions.')
#             else:
#                 form.add_error(None, 'Your email or password is incorrect.')
#     else:
#         form = LoginForm()
#     return render(request, 'registration/login.html', {'form': form})


@login_required(login_url='login_')
def logout_user(request):
    logout(request)
    return redirect('/')


@login_required(login_url='login_')
def user_profile(request, id):
    return redirect('profile_page.html')
    # user = get_object_or_404(CustomUser, pk=id)
    # # donations = Donation.objects.filter(user_id=id).select_related('project')
    # # projects = Project.objects.filter(creator_id=id,status='active')
    #
    # if user.country:
    #     country_name = dict(countries).get(user.country, user.country)
    # else:
    #     country_name = None
    # user.country = country_name
    #
    # # for project in projects:
    # #     percentage = project.current_fund * 100 / project.total_target
    #     project.percentage = percentage
    #
    # if request.user.id == id:
    #     url = "profile/profile_page.html"
    # else:
    #     url = "profile/profile_page2.html"
    #
    # return render(request, url,
    #               context={"User": user, "Donations": donations, "Projects": projects})


@login_required(login_url='login_')
def edit_profile(request):
    user = request.user.customuser
    if request.method == 'POST':
        if 'delete_account' in request.POST:
            return redirect('delete_account')
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            if form.data.get('country'):
                user.country = form.data.get('country')
            if request.FILES:
                user.profile_picture = form.cleaned_data["profile_picture"]
            user.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile', user.id)
    else:
        form = EditProfileForm(instance=user)
    return render(request, 'profile/edit_profile.html', {'form': form})


@login_required(login_url='login_')
def change_password(request):
    user = request.user.customuser
    if request.method == 'POST':
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")
            return redirect('login_')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = ChangePasswordForm(user)
    return render(request, 'password/password_reset_confirm.html', {'form': form})


def password_reset_request(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['username']
            associated_user = get_user_model().objects.filter(Q(username=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("password/password_reset_message.html", {
                    'request': request,
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.username])
                email.content_subtype = 'html'
                try:
                    email.send()
                    messages.success(request, "Password reset email has been sent.")
                    return redirect('login_')
                except Exception as e:
                    messages.error(request, f"Failed to send reset password email. Error: {str(e)}")
            else:
                messages.error(request, "User with this email does not exist.")
        else:
            messages.error(request, "Invalid email address. Please enter a valid email.")
    else:
        form = ResetPasswordForm()
    return render(request, "password/password_reset.html", {"form": form})


def password_reset_confirm(request, uidb64, token):
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = ChangePasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in</b> now.")
                return redirect('login_')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
        else:
            form = ChangePasswordForm(user)
        return render(request, 'password/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("/")


@login_required(login_url='login_')
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        confirmation = request.POST.get('confirmation')
        if confirmation == 'Delete':
            user.delete()
            messages.success(request, 'Your account has been deleted successfully.')
            return redirect('/')
        else:
            messages.error(request, 'Incorrect password. Please try again.')
    return render(request, 'profile/edit_profile.html')




from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  # Assuming you have a template named 'home.html'


















# from django.shortcuts import render
# from django.shortcuts import render, redirect
# from django.contrib.auth import login
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str
# from django.template.loader import render_to_string
# from django.contrib.sites.shortcuts import get_current_site
# from .forms import RegistrationForm
# from .models import CustomUser
# from django.core.mail import send_mail
# from .tokens import account_activation_token
# from django.contrib.auth import login
# from django.utils.http import urlsafe_base64_decode
# from django.contrib.auth.models import User
# from django.http import HttpResponse
# from django.contrib.auth import authenticate, login, logout
#
#
#
#
# def register(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False  # Deactivate account until email is confirmed
#             user.save()
#
#             current_site = get_current_site(request)
#             mail_subject = 'Activate your crowdfunding account.'
#             message = render_to_string('accounts/activation_email.html', {
#                 'user': user,
#                 'domain': current_site.domain,
#                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#                 'token': account_activation_token.make_token(user),
#             })
#             send_mail(mail_subject, message, 'admin@crowdfunding.com', [user.email])
#
#             return render(request, 'accounts/confirm_email.html')
#     else:
#         form = RegistrationForm()
#     return render(request, 'accounts/register.html', {'form': form})
#
#
#
# def activate(request, uidb64, token):
#     try:
#         uid = force_text(urlsafe_base64_decode(uidb64))
#         user = CustomUser.objects.get(pk=uid)
#     except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
#         user = None
#     if user is not None and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.save()
#         login(request, user)
#         return redirect('home')
#     else:
#         return HttpResponse('Activation link is invalid!')
#
#
#
# def user_login(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']
#         user = authenticate(request, email=email, password=password)
#         if user is not None and user.is_active:
#             login(request, user)
#             return redirect('home')
#         else:
#             return HttpResponse('Invalid login credentials or account not activated.')
#     return render(request, 'accounts/login.html')
#
#
# def user_logout(request):
#     logout(request)
#     return redirect('home')
#
#
