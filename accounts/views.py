from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm, CustomAuthenticationForm

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/signup.html'

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.role == 'SELLER':
            return reverse_lazy('dashboard:seller_dashboard')
        elif user.role == 'ADMIN' or user.is_superuser:
            return reverse_lazy('adminpanel:admin_dashboard')
        return reverse_lazy('core:home')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('core:home')
