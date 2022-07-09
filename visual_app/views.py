from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear, ExtractHour, ExtractDay, ExtractMinute
from django.shortcuts import render
from .models import *  # from visual_app.models import *
from django.db.models import Count, Sum, Max, F, When, Q
from django.db.models import Case, Value, When
from django.core.exceptions import ObjectDoesNotExist

# queries
s = Sale.objects
p = Product.objects
pm = Payment.objects

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
client_hour = s.annotate(inithour=ExtractHour('opened'), initmin=(ExtractMinute('opened')),
                       finhour=ExtractHour('closed'), finmin=(ExtractMinute('closed'))).annotate(
    stay_min=F('finmin') - F('initmin'),
    stay_hour=Case(
        When(stay_min__gt=0, then=F('finhour') - F('inithour')),
        When(stay_min__lte=0, then=F('finhour') - F('inithour') + 1),

    ))
stay_time = client_hour.values('stay_hour').annotate(Sum('diners'))

max_stay_time = stay_time.aggregate(Max('stay_hour'))

# ingreso promedio
total_days = len(s.annotate(day=ExtractDay('opened'), year=ExtractYear('opened'),
                            month=ExtractMonth('opened')).values('day', 'month', 'year').distinct())
income_per_pm = Payment.objects.values('type').annotate(income=Sum('amount') / total_days)

# obtengo todos los ingresos ordenados por mes y año desc
desc_income = income_month.order_by('-month', '-year')
months = desc_income.values('month', 'year')

# ventas y medio de pago
income = pm.values('sale_id','amount','type')

# ventas bien y mal cobradas
all_sales = list(pm.values('sale_id').annotate(sum=Sum('amount')).order_by('sale_id'))
all_sales2 = p.annotate(amount=F('price')*F('quantity'))
all_sales2 = list(all_sales2.values('sale_id').annotate(sum=Sum('amount')).order_by('sale_id'))

wrong_sales=[]
right_sales=[]
for i in range(len(all_sales)):
    a1 = all_sales[i]
    a2 = all_sales2[i]
    a1['right_amount'] = a2['sum']
    if a2['sum'] != a1['sum']:
        wrong_sales += [a1]
    else:
        right_sales += [a1]


# Create your views here.
def index(request):
    total_income = right_sales+wrong_sales
    if request.method == 'POST':
        # tipo de ventas
        requested_sale = request.POST["sale"]
        if requested_sale == "all":
            total_income = right_sales+wrong_sales
        elif requested_sale == "right":
            total_income = right_sales
        elif requested_sale == "wrong":
            total_income = wrong_sales

    # si no, muestro todas las ventas

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
        'all_months': months,
        'total_income': total_income,
        'products': p.all().values()[0:100],
        'clients': client_hour.values('sale_id', 'diners', 'stay_hour', 'total'),

    }
    return render(request, 'main/index.html', context)


# entrega número en string con separador de miles
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
    total_income = income_month.aggregate(Sum('income'))['income__sum']
    print(income_month.values('month', 'income'))
    num_of_waiters = len(s.annotate(month=ExtractMonth('opened')).values('waiter').distinct())
    num_of_cashiers = len(s.annotate(month=ExtractMonth('opened')).values('cashier').distinct())
    cost_of_food = total_income * 0.45
    total_cost = (num_of_waiters * 300000 + num_of_cashiers * 450000 + 1000000 + 1000000 + cost_of_food)
    total_profit = total_income - total_cost

    # calculo ingreso de mes actual y pasado---------------------------------------------------------------------------

    # si el método es POST, significa que se esocgió un mes
    if request.method == 'POST':
        # month_year
        requested_date = request.POST["month"].split("_")
        requested_month = requested_date[0]
        requested_year = requested_date[1]
    # si no, muestro info del último mes cronológico
    else:
        requested_month = desc_income[0:1].get()['month']
        requested_year = desc_income[0:1].get()['year']

    # ahora obtengo el ingreso del mes y si existe información de su mes anterior
    month_income = desc_income.filter(month=requested_month, year=requested_year).get()
    no_last_month = False

    # manejo de exceptions
    # si el mes es enero, debemos obtener diciembre como mes anterior y restarle 1 año al año actual
    if requested_month == '1':
        try:
            last_month_income = desc_income.filter(month=12, year=int(requested_year) - 1).get()
        except Sale.DoesNotExist:
            no_last_month = True
        else:
            last_month_income = last_month_income.get()
    # si no, solo obtengo el mes anterior, que es el mes actual menos 1
    else:
        try:
            last_month = int(requested_month) - 1
            last_month_income = desc_income.filter(month=last_month, year=requested_year)
        except Sale.DoesNotExist:
            no_last_month = True
        else:
            last_month_income = last_month_income.get()

    # obtengo los costos del mes actual---------------------------------------------------------------------------------
    m = s.annotate(month=ExtractMonth('opened')).filter(month=str(month_income['month']))
    num_of_waiters = len(m.values('cashier').distinct())
    num_of_cashiers = len(m.values('waiter').distinct())
    cost_of_food = month_income['income'] * 0.45

    # sueldos + renta + cuentas y mantenimiento + costo comida e iva
    cost_per_month = (num_of_waiters * 300000 + num_of_cashiers * 450000 + 1000000 + 1000000 + cost_of_food)

    # si no existe info del mes anterior, la diferencia es 0
    if no_last_month:
        difference = 0
    else:
        difference = ((month_income['income'] - last_month_income['income']) / last_month_income['income']) * 100

    # la diferencia es positiva
    pos_diff = None
    if difference > 0:
        pos_diff = 1
        difference = str(difference)[:min(4, len(str(difference)) - 1)]
    elif difference < 0:
        difference = str(difference)[:min(5, len(str(difference)) - 1)]

    # obtengo las ganancias y los meses para los labels
    profit = int(month_income['income'] - cost_per_month)


    # defino el ingreso del mes anterior dependiendo si existe info para ese mes
    if no_last_month:
        last_month_income = 0
    else:
        last_month_income = thousands(int(last_month_income['income']))

    # finalmente entrego todo
    context = {
        'month_income': thousands(int(month_income['income'])),
        'last_month_income': last_month_income,
        'cost_per_month': thousands(int(cost_per_month)),
        'profit': thousands(profit),
        'difference': difference,
        'pos_diff': pos_diff,
        'income_month': income_month.values('month', 'year'),
        'income': income_month.values('income'),
        'len2': len(income_month),
        'all_months': months,
        'no_last_month': no_last_month,
        'total_income': thousands(int(total_income)),
        'total_profit': thousands(int(total_profit)),
        'total_cost': thousands(int(total_cost)),
        'clientsph': a_client_per_hour,
        'len3': len(a_client_per_hour),
    }
    return render(request, 'main/home.html', context)
