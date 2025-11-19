# Family Budget App — MVP (Expense Epic)

Minimal Django API for managing expenses as part of a Family Budgeting Tool. The MVP includes two core features and was developed using **Test-Driven Development (TDD)**.

---

## ✅ MVP Features

| Feature | Endpoint |
|---------|----------|
| Create Expense | `POST /expenses` |
| List Expenses by Month | `GET /expenses/list?month=YYYY-MM` |

Validation:
- `amount` > 0 and numeric
- `category` required

---

## 🧪 TDD Evidence

Two full RED → GREEN cycles were completed and pushed to the repo:

- **Cycle 1 (Create Expense)**  
  - RED: validation test fails  
  - GREEN: POST `/expenses` passes

- **Cycle 2 (List by Month)**  
  - RED: filter test fails  
  - GREEN: GET `/expenses/list?month=` passes

Proof:  
- Branch: `feat/expenses`  
- Pull Request: _Expense MVP — TDD (2 Cycles)_  
- `pytest -q` shows all tests passing

---

## ▶️ Run the Project

```bash
git clone <repo-url>
cd family_budget_app_MVP
python3 -m venv .venv
source .venv/bin/activate      # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
python manage.py migrate
pytest -q                      # run tests
python manage.py runserver     # start server
