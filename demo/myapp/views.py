from django.shortcuts import render

from . import script
from .models import TodoItem

# Create your views here.
def home(request):
    script.calc_gen()
    return render(request, "home.html")

def todos(request):
    items = TodoItem.objects.all()
    return render(request, "todos.html", {"todos": items})