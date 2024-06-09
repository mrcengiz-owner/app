from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Company
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import pytz, io

@login_required
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # Hatalı giriş
            return render(request, 'login.html', {'error': 'Kullanıcı adı veya şifre yanlış'})
    else:
        return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')  # Kullanıcıyı çıkış yaptıktan sonra anasayfaya yönlendir

@login_required
def orderlist(request):
    today = timezone.now().date()
    companies = Company.objects.all()
    total_orders = Order.objects.filter(created_at__date=today).count()

    company_orders = []
    for company in companies:
        total_orders_for_company = Order.objects.filter(company=company, created_at__date=today).count()
        company_orders.append({
            'company': company,
            'total_orders': total_orders_for_company
        })

    context = {
        'company_orders': company_orders,
        'total_orders': total_orders,
    }

    return render(request, 'order_list.html', context)



@login_required
def firma(request):
    companies = Company.objects.all()
    return render(request, 'firma.html', {'companies': companies})

@login_required
def create_order(request):
    if request.method == 'POST':
        product_ids = request.POST.getlist('products')
        for product_id in product_ids:
            quantity = request.POST.get(f'quantities_{product_id}', 1)
            product = Product.objects.get(id=product_id)
            company = product.company  # Firma bilgisini ürün nesnesinden al
            Order.objects.create(product=product, quantity=quantity, company=company)  # Firma bilgisini de siparişe ekle
        return redirect('order_page')
    return redirect('home')
@login_required
def order_page(request):
    if request.method == 'POST':
        product_id = request.POST['product_id']
        quantity = request.POST['quantity']
        product = Product.objects.get(id=product_id)
        Order.objects.create(product=product, quantity=quantity)
    
    local_tz = pytz.timezone('Europe/Berlin')
    now = timezone.now().astimezone(local_tz)
    today = now.date()
    
    start_of_day = local_tz.localize(timezone.datetime.combine(today, timezone.datetime.min.time()))
    end_of_day = local_tz.localize(timezone.datetime.combine(today, timezone.datetime.max.time()))
    
    orders = Order.objects.filter(created_at__range=(start_of_day, end_of_day))
    
    # Paginator'u oluşturun
    paginator = Paginator(orders, 200)  # Sayfa başına 100 sipariş gösterilecek

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # Eğer sayfa numarası bir tamsayı değilse, ilk sayfayı getirin
        page_obj = paginator.page(1)
    except EmptyPage:
        # Eğer sayfa numarası çok büyükse, son sayfayı getirin
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'order_page.html', {'page_obj': page_obj})



@login_required
def download_all_orders_pdf(request):
    today = timezone.now().date()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="all_orders.pdf"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Tablo başlıkları
    data = [["Product Code", "Product Name", "Quantity", "Company", "Size", "Date"]]

    # Belirli bir tarihteki tüm siparişleri al
    orders = Order.objects.filter(created_at__date=today)
    for order in orders:
        data.append([
            str(order.product.product_code),
            str(order.product.name),
            str(order.quantity),
            str(order.company.name),
            str(order.product.size),
            order.created_at.strftime('%d/%m/%Y')
        ])

    # Tabloyu oluştur
    table = Table(data, colWidths=[80, 120, 60, 100, 80])  # Kolon genişliklerini ayarlayın
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 12),  # Verilerin yazı boyutunu ayarlayın
    ]))

    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response

@login_required
def download_company_orders_pdf(request, company_id):
    today = timezone.now().date()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="company_{company_id}_orders.pdf"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Tablo başlıkları
    data = [["Product Code", "Product Name", "Quantity", "Company", "Size", "Date"]]

    # Belirtilen firmaya ait belirli bir tarihteki siparişleri al
    orders = Order.objects.filter(company_id=company_id, created_at__date=today)
    for order in orders:
        data.append([
            str(order.product.product_code),
            str(order.product.name),
            str(order.quantity),
            str(order.company.name),
            str(order.product.size),
            order.created_at.strftime('%d/%m/%Y')
        ])

    # Tabloyu oluştur
    table = Table(data, colWidths=[80, 120, 60, 100, 80])  # Kolon genişliklerini ayarlayın
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 12),  # Verilerin yazı boyutunu ayarlayın
    ]))

    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response
