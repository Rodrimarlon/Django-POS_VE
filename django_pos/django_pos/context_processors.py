from core.models import ExchangeRate
from django.utils import timezone

def exchange_rate_context(request):
    today = timezone.now().date()
    exchange_rate_exists = ExchangeRate.objects.filter(date=today).exists()
    return {'exchange_rate_exists': exchange_rate_exists}
