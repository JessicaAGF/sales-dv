from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear, ExtractHour
from django.shortcuts import render
from .models import *
from django.db.models import Count, Sum, Max


# Create your views here.
def index(request):
    product_qtt = Product.objects.values('name').order_by('name').annotate(qtt=Sum('quantity'))
    # products_name1 = Product.objects.values('name').order_by('name').distinct()
    # product_cat_qtt = Product.objects.values('name', 'category').order_by('category').annotate(qtt=Sum('quantity'))
    # product_qtt = Product.objects.raw('SELECT name, SUM(quantity) AS qtt FROM visual_app_Product GROUP BY name')
    income_month = Sale.objects.annotate(month=ExtractMonth('opened'), year=ExtractYear('opened')).values(
        'month', 'year').annotate(income=Sum('total'))

    a_client_per_hour = []
    for i in range(25):
        client_per_hour = Sale.objects.annotate(inithour=ExtractHour('opened'), finhour=ExtractHour('closed')).filter(
            inithour__lte=i, finhour__gte=i).aggregate(Sum('diners'))
        if client_per_hour['diners__sum'] is not None:
            client_per_hour['hour'] = i
            a_client_per_hour += [client_per_hour]


    context = {
        'product_name': product_qtt.values('name'),
        'product_qtt': product_qtt.values('qtt'),
        'len1': len(product_qtt),
        'income_month': income_month.values('month', 'year'),
        'income': income_month.values('income'),
        'len2': len(income_month),
        'clientsph': a_client_per_hour,
        'len3': len(a_client_per_hour),
    }
    return render(request, 'main/index.html', context)
