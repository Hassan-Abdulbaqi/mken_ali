from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import HttpResponse

from apps.accounts.decorators import procurement_committee_required, administrator_required
from apps.orders.models import Order, OrderItem
from .forms import PriceItemForm, AdminDecisionForm, BulkDecisionForm


# ============= Procurement Committee Views =============

@login_required
@procurement_committee_required
def pending_orders_view(request):
    """View orders pending pricing."""
    orders = Order.objects.filter(
        status=Order.Status.PENDING_PRICING
    ).select_related('department', 'created_by').order_by('-created_at')
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'procurement/pending_orders.html', {
        'page_obj': page_obj
    })


@login_required
@procurement_committee_required
def price_order_view(request, order_id):
    """Price items in an order."""
    order = get_object_or_404(
        Order.objects.select_related('department', 'created_by'),
        id=order_id,
        status=Order.Status.PENDING_PRICING
    )
    
    if request.method == 'POST':
        # Process price form for each item
        all_priced = True
        for item in order.items.all():
            price_field = f'price_{item.id}'
            if price_field in request.POST:
                try:
                    price = int(request.POST[price_field])
                    if price >= 0:
                        item.price = price
                        item.save()
                    else:
                        all_priced = False
                except (ValueError, TypeError):
                    all_priced = False
            else:
                if not item.price:
                    all_priced = False
        
        action = request.POST.get('action')
        
        if action == 'save':
            messages.success(request, 'تم حفظ الأسعار.')
            return redirect('procurement:price_order', order_id=order.id)
        
        elif action == 'forward':
            # Check all items are priced
            if not all_priced:
                unpriced = order.items.filter(price__isnull=True).count()
                if unpriced > 0:
                    messages.error(request, f'يجب تسعير جميع المواد قبل الإرسال. ({unpriced} مواد بدون سعر)')
                    return redirect('procurement:price_order', order_id=order.id)
            
            order.status = Order.Status.PENDING_APPROVAL
            order.priced_by = request.user
            order.priced_at = timezone.now()
            order.save()
            
            messages.success(request, 'تم إرسال الطلب للمدير للموافقة.')
            return redirect('procurement:pending_orders')
    
    return render(request, 'procurement/price_order.html', {
        'order': order
    })


@login_required
@procurement_committee_required
def decisions_view(request):
    """View orders with admin decisions."""
    orders = Order.objects.filter(
        status__in=[Order.Status.APPROVED, Order.Status.PARTIALLY_APPROVED, Order.Status.DECLINED, Order.Status.ACKNOWLEDGED]
    ).select_related('department', 'created_by', 'decided_by').order_by('-decided_at')
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'procurement/decisions.html', {
        'page_obj': page_obj
    })


@login_required
@procurement_committee_required
def acknowledge_order_view(request, order_id):
    """Acknowledge admin decision on an order."""
    order = get_object_or_404(
        Order,
        id=order_id,
        status__in=[Order.Status.APPROVED, Order.Status.PARTIALLY_APPROVED, Order.Status.DECLINED]
    )
    
    order.status = Order.Status.ACKNOWLEDGED
    order.save()
    
    messages.success(request, 'تم الإطلاع على قرار المدير.')
    return redirect('procurement:decisions')


@login_required
@procurement_committee_required
def export_order_pdf(request, order_id):
    """Export approved order as PDF receipt."""
    order = get_object_or_404(
        Order.objects.select_related('department', 'created_by', 'priced_by', 'decided_by'),
        id=order_id,
        status__in=[Order.Status.APPROVED, Order.Status.PARTIALLY_APPROVED, Order.Status.ACKNOWLEDGED]
    )
    
    # Import PDF libraries
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO
    import os
    
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        has_arabic = True
    except ImportError:
        has_arabic = False
    
    # Register Arabic font
    arabic_font_name = 'Arabic'
    font_registered = False
    
    # Try to find and register an Arabic-compatible font
    font_paths = [
        # Windows fonts
        'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/tahoma.ttf',
        'C:/Windows/Fonts/segoeui.ttf',
        # Common Arabic fonts on Windows
        'C:/Windows/Fonts/arabtype.ttf',
        'C:/Windows/Fonts/tradbdo.ttf',
        'C:/Windows/Fonts/simpbdo.ttf',
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(arabic_font_name, font_path))
                font_registered = True
                break
            except Exception:
                continue
    
    # Fallback to default if no Arabic font found
    if not font_registered:
        arabic_font_name = 'Helvetica'
    
    def reshape_arabic(text):
        """Reshape Arabic text for proper RTL display."""
        if has_arabic and text:
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)
        return str(text) if text else ''
    
    # Create PDF buffer
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title style with Arabic font
    title_style = ParagraphStyle(
        'ArabicTitle',
        parent=styles['Title'],
        fontName=arabic_font_name,
        fontSize=18,
        alignment=1,  # Center
        spaceAfter=20
    )
    
    # Normal style with Arabic font
    normal_style = ParagraphStyle(
        'ArabicNormal',
        parent=styles['Normal'],
        fontName=arabic_font_name,
        fontSize=11,
        alignment=2,  # Right
        spaceAfter=10
    )
    
    # Header
    title = reshape_arabic(f'سند شراء رقم {order.id}')
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Order Info - 2 columns, 3 rows layout
    # Each cell contains "value label:" format for RTL
    decided_by_text = reshape_arabic(str(order.decided_by)) if order.decided_by else ''
    decided_at_text = order.decided_at.strftime('%Y/%m/%d') if order.decided_at else ''
    priced_by_text = reshape_arabic(str(order.priced_by)) if order.priced_by else ''
    
    info_data = [
        # Row 1: الشعبة | منشئ الطلب
        [
            reshape_arabic(str(order.created_by)) + ' :' + reshape_arabic('منشئ الطلب'),
            reshape_arabic(order.department.name) + ' :' + reshape_arabic('الشعبة'),
        ],
        # Row 2: تاريخ الإنشاء | موافقة السيد المدير
        [
            decided_by_text + ' :' + reshape_arabic('موافقة السيد المدير'),
            order.created_at.strftime('%Y/%m/%d') + ' :' + reshape_arabic('تاريخ الإنشاء'),
        ],
        # Row 3: تاريخ امر الشراء | وحدة المشتريات
        [
            priced_by_text + ' :' + reshape_arabic('وحدة المشتريات'),
            decided_at_text + ' :' + reshape_arabic('تاريخ امر الشراء'),
        ],
    ]
    
    info_table = Table(info_data, colWidths=[8*cm, 8*cm], hAlign='RIGHT')
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),  # All cells right-aligned for RTL
        ('FONTNAME', (0, 0), (-1, -1), arabic_font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 1*cm))
    
    # Items Table Header
    items_header = [
        reshape_arabic('الإجمالي'),
        reshape_arabic('السعر'),
        reshape_arabic('الكمية الموافق عليها'),
        reshape_arabic('الكمية المطلوبة'),
        reshape_arabic('المادة'),
        '#'
    ]
    
    items_data = [items_header]
    
    # Items data
    total = 0
    row_num = 1
    for item in order.items.exclude(item_status='declined'):
        qty = item.approved_quantity if item.approved_quantity is not None else item.quantity
        item_total = (item.price or 0) * qty
        total += item_total
        
        items_data.append([
            f'{item_total:,.0f}',
            f'{item.price:,.0f}' if item.price else '-',
            str(qty),
            str(item.quantity),
            reshape_arabic(item.item_name),
            str(row_num)
        ])
        row_num += 1
    
    # Total row
    items_data.append([
        f'{total:,.0f}',
        '',
        '',
        '',
        reshape_arabic('الإجمالي'),
        ''
    ])
    
    items_table = Table(items_data, colWidths=[2.5*cm, 2.5*cm, 3*cm, 2.5*cm, 5.5*cm, 1*cm])
    items_table.setStyle(TableStyle([
        # Font for all cells
        ('FONTNAME', (0, 0), (-1, -1), arabic_font_name),
        
        # Header style
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.03, 0.29, 0.49)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows style
        ('ALIGN', (0, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
        ('ALIGN', (5, 1), (5, -1), 'CENTER'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        
        # Total row style
        ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.9, 0.9, 0.9)),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.8, 0.8, 0.8)),
        ('BOX', (0, 0), (-1, -1), 2, colors.Color(0.03, 0.29, 0.49)),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 1*cm))
    
    # Admin notes if any
    if order.admin_notes:
        elements.append(Paragraph(reshape_arabic('ملاحظات المدير:'), normal_style))
        elements.append(Paragraph(reshape_arabic(order.admin_notes), normal_style))
    
    # Footer
    elements.append(Spacer(1, 2*cm))
    footer_text = reshape_arabic(f'تم إنشاء هذا الإيصال بتاريخ {timezone.now().strftime("%Y/%m/%d %H:%M")}')
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName=arabic_font_name,
        fontSize=9,
        alignment=1,
        textColor=colors.gray
    )
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF content
    pdf = buffer.getvalue()
    buffer.close()
    
    # Return PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}_receipt.pdf"'
    response.write(pdf)
    
    return response


# ============= Administrator Views =============

@login_required
@administrator_required
def admin_pending_view(request):
    """View orders pending admin approval."""
    orders = Order.objects.filter(
        status=Order.Status.PENDING_APPROVAL
    ).select_related('department', 'created_by', 'priced_by').order_by('-priced_at')
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'procurement/admin_pending.html', {
        'page_obj': page_obj
    })


@login_required
@administrator_required
def admin_review_view(request, order_id):
    """Review and decide on an order."""
    order = get_object_or_404(
        Order.objects.select_related('department', 'created_by', 'priced_by'),
        id=order_id,
        status=Order.Status.PENDING_APPROVAL
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve_all':
            # Approve all items
            order.items.update(
                item_status=OrderItem.ItemStatus.APPROVED,
                approved_quantity=None  # Use original quantity
            )
            order.status = Order.Status.APPROVED
            order.admin_notes = request.POST.get('admin_notes', '')
            order.decided_by = request.user
            order.decided_at = timezone.now()
            order.save()
            
            messages.success(request, 'تمت الموافقة على جميع المواد.')
            return redirect('procurement:admin_pending')
        
        elif action == 'decline_all':
            # Decline all items
            order.items.update(item_status=OrderItem.ItemStatus.DECLINED)
            order.status = Order.Status.DECLINED
            order.admin_notes = request.POST.get('admin_notes', '')
            order.decided_by = request.user
            order.decided_at = timezone.now()
            order.save()
            
            messages.success(request, 'تم رفض الطلب.')
            return redirect('procurement:admin_pending')
        
        elif action == 'save_decisions':
            # Process individual item decisions
            has_approved = False
            has_declined = False
            has_modified = False
            
            for item in order.items.all():
                status_field = f'status_{item.id}'
                qty_field = f'qty_{item.id}'
                note_field = f'note_{item.id}'
                
                if status_field in request.POST:
                    new_status = request.POST[status_field]
                    item.item_status = new_status
                    
                    if new_status == 'approved':
                        has_approved = True
                        item.approved_quantity = item.quantity
                    elif new_status == 'declined':
                        has_declined = True
                        item.approved_quantity = 0
                    elif new_status == 'modified':
                        has_modified = True
                        try:
                            item.approved_quantity = int(request.POST.get(qty_field, item.quantity))
                        except (ValueError, TypeError):
                            item.approved_quantity = item.quantity
                    
                    item.admin_note = request.POST.get(note_field, '')
                    item.save()
            
            # Determine overall order status
            if has_declined and not has_approved and not has_modified:
                order.status = Order.Status.DECLINED
            elif has_approved and not has_declined and not has_modified:
                order.status = Order.Status.APPROVED
            else:
                order.status = Order.Status.PARTIALLY_APPROVED
            
            order.admin_notes = request.POST.get('admin_notes', '')
            order.decided_by = request.user
            order.decided_at = timezone.now()
            order.save()
            
            messages.success(request, 'تم حفظ القرارات.')
            return redirect('procurement:admin_pending')
    
    return render(request, 'procurement/admin_review.html', {
        'order': order
    })


@login_required
@administrator_required
def admin_history_view(request):
    """View history of admin decisions."""
    orders = Order.objects.filter(
        decided_by__isnull=False
    ).select_related('department', 'created_by', 'decided_by').order_by('-decided_at')
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'procurement/admin_history.html', {
        'page_obj': page_obj
    })
