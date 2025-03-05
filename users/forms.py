import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission, Group
from events.forms import StyledFormMixin
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from users.models import CustomUser

User = get_user_model()



class RegisterForm(UserCreationForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser  # Use CustomUser model
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'profile_image', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']: 
            self.fields[fieldname].help_text = None

class CustomRegistrationForm(StyledFormMixin, forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser  # Use CustomUser model
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'profile_image', 'password1', 'confirm_password']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_exists = CustomUser.objects.filter(email=email).exists()  # Check email uniqueness in CustomUser
        
        if email_exists:
            raise forms.ValidationError("Email Already exists")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        errors = []

        if len(password1) < 8:
            errors.append('Password must be at least 8 characters long')
        if not re.search(r'[a-z]', password1):
            errors.append("Password must include at least one lowercase letter")
        if not re.search(r'[0-9]', password1):
            errors.append("Password must include at least one number")
        if not re.search(r'[@#$%^&+=]', password1):
            errors.append("Password must include at least one special character")
        if errors:
            raise forms.ValidationError(errors)
        return password1
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        confirm_password = cleaned_data.get('confirm_password')

        if password1 and confirm_password and password1 != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

class AssignRoleForm(StyledFormMixin, forms.Form):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="Select a Role"
    )

class createGroupForm(StyledFormMixin, forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset= Permission.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        label = 'Assign Permission'
    )
    class Meta:
        model = Group
        fields = ['name', 'permissions']

class CustomPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    pass


class CustomPasswordResetForm(StyledFormMixin, PasswordResetForm):
    pass

class EditProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'bio', 'profile_image']
class CustomPasswordResetConfirmForm(StyledFormMixin, SetPasswordForm):
    pass