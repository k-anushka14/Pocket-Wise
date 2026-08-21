from enum import Enum


class ExpenseCategory(str, Enum):
    food = "food"
    cafe = "cafe"
    transport = "transport"
    education = "education"
    shopping = "shopping"
    entertainment = "entertainment"
    hostel = "hostel"
    recharge = "recharge"
    subscriptions = "subscriptions"
    personal_care = "personal_care"
    health = "health"
    gifts = "gifts"
    groceries = "groceries"
    other = "other"


class PaymentMethod(str, Enum):
    upi = "upi"
    cash = "cash"
    debit_card = "debit_card"
    credit_card = "credit_card"
    bank_transfer = "bank_transfer"
    other = "other"


class ExpenseType(str, Enum):
    need = "need"
    want = "want"


class IncomeSource(str, Enum):
    pocket_money = "pocket_money"
    weekly_allowance = "weekly_allowance"
    scholarship = "scholarship"
    internship_stipend = "internship_stipend"
    freelance = "freelance"
    gift = "gift"
    other = "other"


class RecurrenceFrequency(str, Enum):
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class SortField(str, Enum):
    date = "date"
    amount = "amount"


class SortDirection(str, Enum):
    asc = "asc"
    desc = "desc"

class GoalPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class SplitDirection(str, Enum):
    owed_to_me = "owed_to_me"
    i_owe = "i_owe"


class SplitStatus(str, Enum):
    pending = "pending"
    paid = "paid"