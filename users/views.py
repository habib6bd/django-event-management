from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth import login, logout
from users.forms import CustomRegistrationForm, AssignRoleForm, createGroupForm
from django.contrib import messages
from users.forms import LoginForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm, EditProfileForm 
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse, reverse_lazy
from users.forms import AssignRoleForm, CustomPasswordChangeForm
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView

from django.contrib.auth import get_user_model
User = get_user_model()

class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect('profile')

class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm

#Test for users
def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def sign_up(request):
    form = CustomRegistrationForm()
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False  # Keep inactive until email confirmation
            user.save()
            
            # Ensure the user is ONLY in the Participant group
            user.groups.clear()  # Remove any default groups
            participant_group, created = Group.objects.get_or_create(name="Participant")
            user.groups.add(participant_group)

            print(f"User created: {user.username}, Email: {user.email}")
            messages.success(request, 'A confirmation email has been sent. Please check your email.')
            return redirect('sign-in')

    return render(request, 'registration/register.html', {"form": form})

def sign_in(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    return render(request, 'registration/login.html', {'form': form})

@login_required
def sign_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('sign-in')
    
def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('sign-in')
        else:
            return HttpResponse('Invalid Id or token')
    except User.DoesNotExist:
        return HttpResponse('User not found')

@user_passes_test(is_admin, login_url='no-permission')   
def admin_dashboard(request):
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
        ).all()
    print(users)
    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = 'No Group Assigned'

    return render(request, 'admin/dashboard.html', {"users": users})

# @user_passes_test(is_admin, login_url='no-permission')   
# def assign_role(request, user_id):
#     user = User.objects.get(id=user_id)
#     form = AssignRoleForm

#     if request.method == 'POST':
#         form = AssignRoleForm(request.POST)
#         if form.is_valid():
#             role = form.cleaned_data.get('role')
#             user.groups.clear() #Remove old roles
#             user.groups.add(role)
#             messages.success(request, f"User {user.username} has been assigned to the {role.name} role")
#             return redirect('admin-dashboard')
#     return render(request, 'admin/assign_role.html', {"form": form})

#Class Based View
class AssignRoleView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'admin/assign_role.html'
    form_class = AssignRoleForm

    def test_func(self):
        """Only allow admins to access this view"""
        return is_admin(self.request.user)

    def form_valid(self, form):
        """Process the role assignment"""
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)

        role = form.cleaned_data.get('role')
        user.groups.clear()  # Remove old roles
        user.groups.add(role)

        messages.success(self.request, f"User {user.username} has been assigned to the {role.name} role")
        return redirect('admin-dashboard')

    def handle_no_permission(self):
        """Redirect unauthorized users"""
        messages.error(self.request, "You don't have permission to assign roles.")
        return redirect('no-permission')

@user_passes_test(is_admin, login_url='no-permission')   
def create_group(request):
    form = createGroupForm()
    if request.method == 'POST':
        form = createGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} has been created successfully")
            return redirect('create-group')
    return render(request, 'admin/create_group.html', {'form': form})

# @user_passes_test(is_admin, login_url='no-permission')   
# def group_list(request):
#     groups = Group.objects.prefetch_related('permissions').all()
#     return render(request, 'admin/group_list.html', {'groups': groups})

#Class based View
@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class GroupListView(ListView):
    model = Group
    template_name = 'admin/group_list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        return Group.objects.prefetch_related('permissions').all()

class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()

        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        return context



class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')
    html_email_template_name = 'registration/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print(context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email sent. Please check your email')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset successfully')
        return super().form_valid(form)
