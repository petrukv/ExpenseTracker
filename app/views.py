import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render

from .forms import ExpenseForm, UserRegistrationForm
from .models import Expense

# Create your views here.

def index(request):
    if request.method == "POST":
        expense = ExpenseForm(request.POST)
        if expense.is_valid():
            new_expense = expense.save(commit=False)
            new_expense.owner = request.user
            new_expense.save()

    expenses = Expense.objects.filter(owner=request.user)
    total_expenses = expenses.aggregate(Sum('amount'))

    last_year = datetime.date.today() - datetime.timedelta(days=365)
    data = Expense.objects.filter(owner=request.user, date__gt=last_year)
    yearly_sum = expenses.aggregate(Sum('amount'))

    last_month = datetime.date.today() - datetime.timedelta(days=30)
    data = Expense.objects.filter(owner=request.user, date__gt=last_month)
    monthly_sum = expenses.aggregate(Sum('amount'))

    last_week = datetime.date.today() - datetime.timedelta(days=7)
    data = Expense.objects.filter(owner=request.user, date__gt=last_week)
    weekly_sum = expenses.aggregate(Sum('amount'))

    daily_sums = Expense.objects.filter(owner=request.user).values('date').order_by('date').annotate(sum=Sum('amount'))

    categorical_sums = Expense.objects.filter(owner=request.user).values('category').order_by('category').annotate(sum=Sum('amount'))

    expense_form = ExpenseForm()
    return render(request, "app/index.html", {'expense_form': expense_form, 'expenses': expenses, 'total_expenses': total_expenses, 'yearly_sum': yearly_sum, 'monthly_sum': monthly_sum, 'weekly_sum': weekly_sum, 'daily_sums': daily_sums, 'categorical_sums': categorical_sums})


def edit(request, id):
    expense = Expense.objects.get(id=id)
    expense_form = ExpenseForm(instance=expense)
    if request.method == "POST":
        expense = Expense.objects.get(id=id)
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('index')
        
    return render(request, "app/edit.html", {'expense_form' : expense_form})

def delete(request, id):
    if request.method == "POST" and 'delete' in request.POST:
        expense = Expense.objects.get(id=id)
        expense.delete()
    return redirect("index")

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data['password'])
        new_user.save()
        return redirect('index')
    form = UserRegistrationForm()
    return render(request, "app/register.html", {'form':form})