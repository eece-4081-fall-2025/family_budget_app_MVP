from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# ============================================================
# Existing Models (Income / Expense)
# ============================================================


class Income(models.Model):
    source = models.CharField(max_length=100)
    amount = models.FloatField()
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.source} - ${self.amount:.2f}"


class Expense(models.Model):
    """
    Expense model used by:
      - Existing app features
      - Epic 3 recurring-expense management
      - Tests in budget.tests.* (once updated)
    """
    # from Epic 3: tie each expense to a user
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expenses",
        null=True,      # keep nullable so old rows still work
        blank=True,
    )

    # from Epic 3: DecimalField; from MVP: amount field already existed
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    category = models.CharField(max_length=100)

    # from MVP: CharField; from Epic 3: TextField
    # choose TextField (more flexible); CharField usage still works with it
    note = models.TextField(blank=True)

    # from Epic 3: auto_now_add; from MVP: default=timezone.now
    # choose default so tests/forms can still set date manually
    date = models.DateField(default=timezone.now)

    # from both: recurring flag
    recurring = models.BooleanField(default=False)

    # from Epic 3: recurrence_rule string
    recurrence_rule = models.CharField(max_length=100, blank=True)

    # from MVP: keep original field for backward compatibility
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        username = self.user.username if self.user_id else "Unknown user"
        return f"{username} - {self.category} (${self.amount})"


# ============================================================
# Epic 5 Models (Budget / Category / Transaction)
# ============================================================


class Budget(models.Model):
    """
    A named budget owned by a user.
    Used by Epic 5 tests for summaries & reports.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    name = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Category(models.Model):
    """
    A spending category tied to a specific budget.
    Example: Food, Rent, Misc.
    """
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.budget.name})"


class Transaction(models.Model):
    """
    Positive amount = income
    Negative amount = expense

    Extended with Epic 3 fields:
      - type (Money In / Money Out)
      - family_member (who the transaction is associated with)
    """

    # MVP fields
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)

    # amount was already DecimalField in MVP
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Epic 3 additions (kept but optional so they don’t break anything yet)
    TYPE_CHOICES = [
        ("IN", "Money In"),
        ("OUT", "Money Out"),
    ]
    type = models.CharField(
        max_length=3,
        choices=TYPE_CHOICES,
        blank=True,
    )
    family_member = models.CharField(max_length=100, blank=True)

    def __str__(self):
        # keep the simple MVP string for now so old tests still pass
        return f"{self.date} {self.description} {self.amount}"
