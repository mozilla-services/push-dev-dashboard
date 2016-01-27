from django.views.generic import TemplateView

# Create your views here.
class Home(TemplateView):
    template_name = 'home.html'
