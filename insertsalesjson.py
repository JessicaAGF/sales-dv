from visual_app.models import *
import json

f = open('ventas.json')
data = json.load(f)

for d in data:
    for pay in d['payments']:
        payment = Payment(sale_id=d['id'], amount=pay['amount'], type=pay['type'])
        payment.save()
    for pro in d['products']:
        product = Product(sale_id=d['id'], category=pro['category'], price=pro['price'], name=pro['name'],
                          quantity=pro['quantity'])
        product.save()
    sale = Sale.objects.create(closed=d['date_closed'], zone=d['zone'], waiter=d['waiter'], cashier=d['cashier'],
                               diners=d['diners'], opened=d['date_opened'], table=d['table'], total=d['total'],
                               sale_id=d['id'])
    sale.save()
