from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Income, Expense
import json
import os
from datetime import date, datetime


# ============================================================
# Epic 3 – Expense API (JSON, uses Django auth)
# ============================================================

@csrf_exempt
@login_required
def create_expense(request):
    """
    API endpoint: create an expense for the logged-in user.
    Used by ExpenseAPITests (reverse('create_expense')).
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=405)

    # Accept both JSON and form-encoded payloads
    if request.content_type == "application/json":
        data = json.loads(request.body or b"{}")
    else:
        data = request.POST

    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Amount must be a number"}, status=400)

    category = (data.get("category") or "").strip()
    note = data.get("note", "")

    if amount <= 0 or not category:
        return JsonResponse({"error": "Invalid input"}, status=400)

    Expense.objects.create(
        user=request.user,
        amount=amount,
        category=category,
        note=note,
        date=date.today(),
    )
    return JsonResponse({"message": "Expense created"}, status=201)


@login_required
def list_expenses(request):
    """
    API endpoint: list expenses for a given month for the logged-in user.
    Used by ExpenseListTests (reverse('list_expenses')).
    Expects ?month=YYYY-MM.
    """
    month_str = request.GET.get("month")
    if not month_str:
        return JsonResponse({"error": "Month parameter is required"}, status=400)

    try:
        year, month = map(int, month_str.split("-"))
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()
    except Exception:
        return JsonResponse(
            {"error": "Invalid month format (use YYYY-MM)"},
            status=400,
        )

    expenses = (
        Expense.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lt=end_date,
        )
        .values("id", "amount", "category", "note", "date")
    )

    return JsonResponse(list(expenses), safe=False, status=200)


# ============================================================
# Core views – login, dashboard, income/expense JSON storage
# (MVP / Epic 2 functionality)
# ============================================================

# Helper functions to handle per-user data
def get_user_file(username):
    return f"{username}_data.json"


def load_user_data(username):
    filename = get_user_file(username)
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return {
            "income": [],
            "expenses": [],
            "total_income": 0,
            "total_expense": 0,
            "balance": 0,
        }


def save_user_data(username, data):
    filename = get_user_file(username)
    with open(filename, "w") as f:
        json.dump(data, f)


# -------------------------------------------
# LOGIN (supports both auth + simple session)
# -------------------------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password", "")

        # If password is provided, use Django auth
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # also keep username in session for JSON-based flows
                request.session["username"] = username
                return redirect("dashboard")
            else:
                context = {"error": "Invalid username or password."}
                return render(request, "login.html", context)

        # Fallback: original MVP behavior (no password, just set session)
        if username and not password:
            request.session["username"] = username
            return redirect("dashboard")

    # GET request or missing username → just render the page
    return render(request, "login.html")


# -------------------------------------------
# DASHBOARD (Shows totals)
# -------------------------------------------
def dashboard_view(request):
    username = request.session.get("username", None)
    if not username:
        return redirect("login")

    user_data = load_user_data(username)

    context = {
        "username": username,
        "total_income": user_data["total_income"],
        "total_expense": user_data["total_expense"],
        "balance": user_data["balance"],
    }
    return render(request, "dashboard.html", context)


# -------------------------------------------
# ADD INCOME (EPIC 2)
# -------------------------------------------
def add_income_view(request):
    username = request.session.get("username", None)
    if not username:
        return redirect("login")

    if request.method == "POST":
        source = request.POST.get("source")
        amount = request.POST.get("amount")
        contributor = request.POST.get("contributor")
        planned = request.POST.get("planned") == "on"
        date_val = request.POST.get("date")

        if source and amount:
            user_data = load_user_data(username)

            new_entry = {
                "id": len(user_data["income"]) + 1,
                "source": source,
                "amount": float(amount),
                "contributor": contributor,
                "planned": planned,
                "date": date_val,
            }

            user_data["income"].append(new_entry)
            user_data["total_income"] += float(amount)
            user_data["balance"] = (
                user_data["total_income"] - user_data["total_expense"]
            )

            save_user_data(username, user_data)

            return redirect("dashboard")

    return render(request, "add_income.html", {"username": username})


# -------------------------------------------
# ADD EXPENSE
# -------------------------------------------
def add_expense_view(request):
    username = request.session.get("username", None)
    if not username:
        return redirect("login")

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
                user_data = load_user_data(username)

                # Budget validation using JSON data
                if (
                    user_data["total_expense"] + amount_float
                    > user_data["total_income"]
                ):
                    error_message = (
                        "Error: Expense exceeds your available budget!"
                    )
                else:
                    # Add expense to user's JSON data
                    expense_item = {"category": category, "amount": amount_float}
                    user_data["expenses"].append(expense_item)
                    user_data["total_expense"] += amount_float
                    user_data["balance"] = (
                        user_data["total_income"] - user_data["total_expense"]
                    )
                    save_user_data(username, user_data)
                    return redirect("dashboard")
            except ValueError:
                error_message = "Invalid amount entered."

    context = {
        "username": username,
        "error_message": error_message,
        "category_value": category_value,
        "amount_value": amount_value,
    }
    return render(request, "add_expense.html", context)


# -------------------------------------------
# SUMMARY PAGE
# -------------------------------------------
def summary_view(request):
    username = request.session.get("username", None)
    if not username:
        return redirect("login")

    user_data = load_user_data(username)

    context = {
        "username": username,
        "incomes": user_data["income"],
        "expenses": user_data["expenses"],
        "total_income": user_data["total_income"],
        "total_expense": user_data["total_expense"],
        "balance": user_data["balance"],
    }
    return render(request, "summary.html", context)


# =================================================================
#                   EPIC 2 — INCOME MANAGEMENT
# =================================================================


# -------------------------------------------
# VIEW INCOME LIST
# -------------------------------------------
def view_income(request):
    username = request.session.get("username")
    if not username:
        return redirect("login")

    user_data = load_user_data(username)
    return render(
        request,
        "view_income.html",
        {
            "username": username,
            "incomes": user_data["income"],
        },
    )


# -------------------------------------------
# EDIT INCOME
# -------------------------------------------
def edit_income(request, income_id):
    username = request.session.get("username")
    if not username:
        return redirect("login")

    user_data = load_user_data(username)

    # Find entry
    income_item = next(
        (i for i in user_data["income"] if i["id"] == income_id),
        None,
    )
    if not income_item:
        return redirect("view_income")

    if request.method == "POST":
        income_item["source"] = request.POST.get("source")
        income_item["amount"] = float(request.POST.get("amount"))
        income_item["contributor"] = request.POST.get("contributor")
        income_item["planned"] = request.POST.get("planned") == "on"
        income_item["date"] = request.POST.get("date")

        # Recalculate totals
        user_data["total_income"] = sum(i["amount"] for i in user_data["income"])
        user_data["balance"] = user_data["total_income"] - user_data["total_expense"]

        save_user_data(username, user_data)
        return redirect("view_income")

    return render(
        request,
        "edit_income.html",
        {
            "username": username,
            "income": income_item,
        },
    )


# -------------------------------------------
# DELETE INCOME
# -------------------------------------------
def delete_income(request, income_id):
    username = request.session.get("username")
    if not username:
        return redirect("login")

    user_data = load_user_data(username)

    user_data["income"] = [i for i in user_data["income"] if i["id"] != income_id]

    # Recalculate totals
    user_data["total_income"] = sum(i["amount"] for i in user_data["income"])
    user_data["balance"] = user_data["total_income"] - user_data["total_expense"]

    save_user_data(username, user_data)

    return redirect("view_income")


# -------------------------------------------
# LOGOUT
# -------------------------------------------
def logout_view(request):
    """
    Logs out a Django-authenticated user and clears session data.
    """
    logout(request)
    request.session.flush()
    return redirect("login")
