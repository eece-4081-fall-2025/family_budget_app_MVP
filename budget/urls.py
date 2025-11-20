from django.urls import path
from . import views
from . import views_reports
from . import views_api   # API views for Expense tests

urlpatterns = [
    # ---------------------------------------------------------
    # Core / Auth / Dashboard
    # ---------------------------------------------------------
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Epic 3 "home" view kept on a separate URL so we don't lose it
    path('home/', views.home, name='home'),

    # ---------------------------------------------------------
    # Income routes
    # ---------------------------------------------------------
    path('income/add/', views.add_income_view, name='add_income'),
    path('income/', views.view_income, name='view_income'),
    path('income/edit/<int:income_id>/', views.edit_income, name='edit_income'),
    path('income/delete/<int:income_id>/', views.delete_income, name='delete_income'),

    # ---------------------------------------------------------
    # Expense form/page routes (MVP UI)
    # ---------------------------------------------------------
    path('expense/', views.add_expense_view, name='add_expense'),

    # ---------------------------------------------------------
    # Summary page
    # ---------------------------------------------------------
    path('summary/', views.summary_view, name='summary'),

    # ---------------------------------------------------------
    # Epic 5 — Reporting Endpoints
    # ---------------------------------------------------------
    path(
        'reports/<int:budget_id>/csv/',
        views_reports.reports_csv,
        name='reports_csv',
    ),
    path(
        'reports/<int:budget_id>/what_if/',
        views_reports.reports_what_if,
        name='reports_what_if',
    ),
    path(
        'reports/<int:budget_id>/recommendations/',
        views_reports.reports_recommendations,
        name='reports_recos',
    ),

    # ---------------------------------------------------------
    # Expense API endpoints used by tests (Epic 3)
    # ---------------------------------------------------------
    path(
        'api/expenses/create/',
        views_api.create_expense,
        name='create_expense',
    ),
    path(
        'api/expenses/',
        views_api.list_expenses,
        name='list_expenses',
    ),

    # Logout
    path('logout/', views.logout_view, name='logout'),
]
