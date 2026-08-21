from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.session import Base, engine
from app.routes import (
    users, income, transactions, budgets, dashboard,
    goals, recurring_expenses, split_expenses,
)

# Import models so SQLAlchemy's Base.metadata knows about them before
# create_all runs below.
from app.models import (  # noqa: F401
    profile, income as income_model, transaction, budget,
    savings_goal, recurring_expense, split_expense,
)

# Create tables that don't exist yet. Fine while the schema is this small --
# once things get more complex we switch to Alembic migrations so schema
# changes are tracked and reversible instead of just "whatever create_all does".
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PocketWise API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(income.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(dashboard.router)
app.include_router(goals.router)
app.include_router(recurring_expenses.router)
app.include_router(split_expenses.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
