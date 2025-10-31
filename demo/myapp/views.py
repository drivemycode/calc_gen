from django.shortcuts import render, redirect
from .models import TodoItem
from .script import calc_gen_text, solve_problem
import asyncio

# Create your views here.
def home(request):
    expression = request.session.get('current_expression', 'x+2')
    solution = request.session.get('current_solution', 'I\'m here to help! :)')
    return render(request, "home.html", {'expression': expression, "solution": solution})

def about(request):
    return render(request, "about.html")

def run_script(request):
    if request.method == "POST":
        if 'action' in request.POST:
            value = request.POST.get('action')
            if value == "":
                solution = asyncio.run(solve_problem(request.session['current_expression']))
                request.session['current_solution'] = solution
            else:
                expression = calc_gen_text(value)
                request.session['current_expression'] = expression
            request.session.modified = True
    return redirect('home')
