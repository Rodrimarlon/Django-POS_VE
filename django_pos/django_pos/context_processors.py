from core.models import ExchangeRate
from datetime import date

def exchange_rate_context(request):
    today = date.today()
    exchange_rate_exists = ExchangeRate.objects.filter(date=today).exists()
    return {'exchange_rate_exists': exchange_rate_exists}
