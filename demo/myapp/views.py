from django.shortcuts import render, redirect
from .models import TodoItem
from .script import calc_gen_text

# Create your views here.
def home(request):
    expression = request.session.get('current_expression', 'x+2')
    return render(request, "home.html", {'expression': expression})

def about(request):
    return render(request, "about.html")

def todos(request):
    items = TodoItem.objects.all()
    return render(request, "todos.html", {"todos": items})

def run_script(request):
    if request.method == "POST":
        if 'action' in request.POST:
            expression = calc_gen_text(request.POST.get('action'))
            request.session['current_expression'] = expression
            request.session.modified = True
    return redirect('home')
