from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear, ExtractHour, ExtractDay
from django.shortcuts import render
from .models import *
from django.db.models import Count, Sum, Max, F


# Create your views here.
def index(request):
    # frecuencia de productos
    product_qtt = Product.objects.values('name').annotate(qtt=Sum('quantity')).order_by('name')
    # ingresos por producto
    product_income = Product.objects.values('name').annotate(qtt=Sum('quantity')*F('price')).order_by('name')
    # ingreso mensual
    income_month = Sale.objects.annotate(month=ExtractMonth('opened'), year=ExtractYear('opened')).values(
        'month', 'year').annotate(income=Sum('total'))

    # clientes por hora
    a_client_per_hour = []
    for i in range(25):
        client_per_hour = Sale.objects.annotate(inithour=ExtractHour('opened'), finhour=ExtractHour('closed')).filter(
            inithour__lte=i, finhour__gte=i).aggregate(Sum('diners'))
        if client_per_hour['diners__sum'] is not None:
            client_per_hour['hour'] = i
            a_client_per_hour += [client_per_hour]

    # ingreso promedio
    total_days = len(Sale.objects.annotate(day=ExtractDay('opened'), year=ExtractYear('opened'),
                                       month=ExtractMonth('opened')).values('day','month','year').distinct())
    income_per_pm = Payment.objects.values('type').annotate(income=Sum('amount')/total_days)


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
        'product_income': product_income
    }
    return render(request, 'main/index.html', context)
