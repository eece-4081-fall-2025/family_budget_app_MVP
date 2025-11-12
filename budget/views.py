from django.shortcuts import render, redirect
from .models import Income, Expense

# Simulated login (stores name in session)
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        if username:
            request.session['username'] = username
            return redirect('dashboard')
    return render(request, "login.html")

def dashboard_view(request):
    username = request.session.get('username', None)
    if not username:
        return redirect('login')

    total_income = sum(i.amount for i in Income.objects.all())
    total_expense = sum(e.amount for e in Expense.objects.all())
    balance = total_income - total_expense

    context = {
        "username": username,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
    }
    return render(request, "dashboard.html", context)

def add_income_view(request):
    username = request.session.get('username', None)
    if not username:
        return redirect('login')

    if request.method == "POST":
        source = request.POST.get("source")
        amount = request.POST.get("amount")
        if source and amount:
            Income.objects.create(source=source, amount=float(amount))
            return redirect('dashboard')

    return render(request, "add_income.html", {"username": username})

def add_expense_view(request):
    username = request.session.get('username', None)
    if not username:
        return redirect('login')

    error_message = None
    category_value = ""
    amount_value = ""

    if request.method == "POST":
        category = request.POST.get("category")
        amount = request.POST.get("amount")

        # Keep values to refill the form
        category_value = category
        amount_value = amount

        if category and amount:
            try:
                amount_float = float(amount)
                total_income = sum(i.amount for i in Income.objects.all())
                total_expense = sum(e.amount for e in Expense.objects.all())

                if total_expense + amount_float > total_income:
                    error_message = "Error: Expense exceeds your available budget!"
                else:
                    Expense.objects.create(category=category, amount=amount_float)
                    return redirect('dashboard')
            except ValueError:
                error_message = "Invalid amount entered."

    context = {
        "username": username,
        "error_message": error_message,
        "category_value": category_value,
        "amount_value": amount_value,
    }
    return render(request, "add_expense.html", context)



def summary_view(request):
    username = request.session.get('username', None)
    if not username:
        return redirect('login')

    incomes = Income.objects.all()
    expenses = Expense.objects.all()
    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    balance = total_income - total_expense

    context = {
        "username": username,
        "incomes": incomes,
        "expenses": expenses,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
    }
    return render(request, "summary.html", context)
