from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear, ExtractHour, ExtractDay, ExtractMinute
from django.shortcuts import render
from .models import * #from visual_app.models import *
from django.db.models import Count, Sum, Max, F, When
from django.db.models import Case, Value, When

# queries
s = Sale.objects
p = Product.objects

# frecuencia de productos
product_qtt = p.values('name').annotate(qtt=Sum('quantity')).order_by('name')
# ingresos por producto
product_income = p.values('name').annotate(qtt=Sum('quantity') * F('price')).order_by('name')
# ingreso mensual
income_month = s.annotate(month=ExtractMonth('opened'), year=ExtractYear('opened')).values('month', 'year').annotate(
    income=Sum('total'))

# clientes por hora
a_client_per_hour = []
for i in range(25):
    client_per_hour = s.annotate(inithour=ExtractHour('opened'), finhour=ExtractHour('closed')).filter(
        inithour__lte=i, finhour__gte=i).aggregate(Sum('diners'))
    if client_per_hour['diners__sum'] is not None:
        client_per_hour['hour'] = i
        a_client_per_hour += [client_per_hour]

# frecuencia de ventas y clientes por horas de estadía
stay_time = s.annotate(inithour=ExtractHour('opened'), initmin=(ExtractMinute('opened')),
                       finhour=ExtractHour('closed'), finmin=(ExtractMinute('closed'))).annotate(
    stay_min=F('finmin') - F('initmin'),
    stay_hour=Case(
        When(stay_min__gt=0, then=F('finhour') - F('inithour')),
        When(stay_min__lte=0, then=F('finhour') - F('inithour') + 1),

    )).values('stay_hour').annotate(Sum('diners'))

max_stay_time = stay_time.aggregate(Max('stay_hour'))

print(stay_time)

# ingreso promedio
total_days = len(s.annotate(day=ExtractDay('opened'), year=ExtractYear('opened'),
                            month=ExtractMonth('opened')).values('day', 'month', 'year').distinct())
income_per_pm = Payment.objects.values('type').annotate(income=Sum('amount') / total_days)


# Create your views here.
def index(request):
    context = {
        'product_name': product_qtt.values('name'),
        'product_qtt': product_qtt.values('qtt'),
        'len1': len(product_qtt),
        'income_month': income_month.values('month', 'year'),
        'income': income_month.values('income'),
        'len2': len(income_month),
        'clientsph': a_client_per_hour,
        'len3': len(a_client_per_hour),
        'avg_income_ppm': income_per_pm,
        'product_income': product_income,
        'stay_time': stay_time,
        'max_stay_time': max_stay_time,
    }
    return render(request, 'main/index.html', context)


def thousands(num):
    threesum = len(str(num)) // 3
    start = len(str(num)) - threesum * 3

    to_sep = str(num)[start:]
    rest = ''
    for i in range(threesum):
        rest += '.' + to_sep[i * 3:(i + 1) * 3]

    if len(str(num)) % 3 == 0:
        return rest[1:]
    return str(num)[0:start] + rest

def home(request):
    if request.method == 'POST':
        #month_year
        requested_month = request.POST["month"]

        #ingresos
        desc_income = income_month.order_by('-month', '-year')
        last_month_income = desc_income[0:1].get()
        last_last_month_income = desc_income[1:2].get()

        #costos
        num_of_waiters = len(s.annotate(month=ExtractMonth('opened')).filter(month=str(last_month_income['month'])).values(
            'cashier').distinct())
        num_of_cashiers = len(s.annotate(month=ExtractMonth('opened')).filter(month=str(last_month_income['month'])).values(
            'waiter').distinct())
        cost_of_food = last_month_income['income'] * 0.45

        # sueldos + renta + cuentas y mantenimiento + costo comida e iva
        cost_per_month = (num_of_waiters * 300000 + num_of_cashiers * 450000 + 1000000 + 1000000 + cost_of_food)
        difference = ((last_month_income['income'] - last_last_month_income['income']) / last_last_month_income['income'])*100
        pos_diff = None
        if difference > 0:
            pos_diff = 1
        profit = int(last_month_income['income'] - cost_per_month)
        difference = str(difference)[:4]

        months = desc_income.values('month', 'year')

        context = {
            'last_month_income': thousands(int(last_month_income['income'])),
            'last_last_month_income': thousands(int(last_last_month_income['income'])),
            'cost_per_month': thousands(int(cost_per_month)),
            'profit': thousands(profit),
            'difference': difference,
            'pos_diff': pos_diff,
            'income_month': income_month.values('month', 'year'),
            'income': income_month.values('income'),
            'len2': len(income_month),
            'all_months': months,
        }
    return render(request, 'main/home.html', context)
