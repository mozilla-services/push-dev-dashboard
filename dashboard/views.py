from django.views.generic import TemplateView

class Home(TemplateView):
    template_name = 'dashboard/home.html'

class Profile(TemplateView):
    template_name = 'dashboard/profile.html'
