from django.shortcuts import render
from .models import *
from django.db.models import Count, Sum


# Create your views here.
def index(request):

    #products_name1 = Product.objects.values('name').order_by('name').distinct()
    product_qtt = Product.objects.values('name').order_by('name').annotate(qtt=Sum('quantity'))
    #product_qtt = Product.objects.raw('SELECT name, SUM(quantity) AS qtt FROM visual_app_Product GROUP BY name')

    context = {
        'product_name': product_qtt.values('name'),
        'product_qtt': product_qtt.values('qtt'),
        'len1': len(product_qtt),
    }
    return render(request, 'main/index.html',context)
