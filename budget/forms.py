from django import forms
from .models import Transaction, Debt, Bill, User

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'amount']


class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['total_debt']


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['name', 'amount', 'due_date', 'assigned_to', 'link']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'visibility']
