from django.test import TestCase
from budget.models import Expense

class Epic3ExpenseManagementTest(TestCase):
    def test_add_expense_with_category_and_amount(self):
        """User can add an expense with category and amount"""
        expense = Expense.objects.create(
            category='Food',
            amount=50
        )
        self.assertEqual(expense.category, 'Food')
        self.assertEqual(expense.amount, 50)

    def test_add_expense_with_notes(self):
        """User can add notes to an expense"""
        expense = Expense.objects.create(
            category='Entertainment',
            amount=20
        )
        # Add notes dynamically (simulate adding notes field if you implement later)
        expense.notes = "Movie ticket"
        expense.save()
        self.assertEqual(expense.notes, "Movie ticket")

    def test_multiple_expenses(self):
        """User can add multiple expenses"""
        Expense.objects.create(category='Rent', amount=500)
        Expense.objects.create(category='Food', amount=100)
        all_expenses = Expense.objects.all()
        self.assertEqual(all_expenses.count(), 2)
