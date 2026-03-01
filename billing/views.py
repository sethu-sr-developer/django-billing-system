from django.contrib import messages
from django.shortcuts import redirect, render
from django.db import transaction
from billing.models import Product, Customer, Bill, BillItem
from billing.utils import calculate_change
from django.core.mail import send_mail
import threading
from django.http import JsonResponse


def send_invoice_email_async(subject, message, recipient):
    thread = threading.Thread(
        target=send_mail,
        args=(subject, message, 'shop@example.com', [recipient])
    )
    thread.start()


def billing_page(request):
    products = Product.objects.all()
    return render(request, "billing/billing.html", {"products": products})


def generate_bill(request):

    if request.method == "POST":

        try:
            with transaction.atomic():

                email = request.POST.get("email")
                paid_amount = float(request.POST.get("paid_amount"))

                customer, _ = Customer.objects.get_or_create(email=email)

                bill = Bill.objects.create(
                    customer=customer,
                    total_amount=0,
                    paid_amount=paid_amount,
                    balance_amount=0
                )

                total_amount = 0

                product_ids = request.POST.getlist("product_id")
                quantities = request.POST.getlist("quantity")

                for pid, qty in zip(product_ids, quantities):

                    product = Product.objects.get(product_id=pid)
                    qty = int(qty)

                    if product.available_stock < qty:
                        raise ValueError("Insufficient stock for product " + product.name)

                    subtotal = product.unit_price * qty
                    tax = subtotal * (product.tax_percentage / 100)
                    total = subtotal + tax

                    BillItem.objects.create(
                        bill=bill,
                        product=product,
                        quantity=qty,
                        price_without_tax=subtotal,
                        tax_amount=tax,
                        total_price=total
                    )

                    product.available_stock -= qty
                    product.save()

                    total_amount += total

                balance = paid_amount - total_amount

                if balance < 0:
                    raise ValueError("Paid amount is less than total bill amount.")

                bill.total_amount = total_amount
                bill.balance_amount = balance
                bill.save()

                change_details = calculate_change(balance)

                send_invoice_email_async(
                    "Your Invoice",
                    f"Total: {total_amount}, Paid: {paid_amount}, Change: {balance}",
                    email
                )

                return render(request, "billing/bill_result.html", {
                    "bill": bill,
                    "change": change_details
                })

        except ValueError as e:
            messages.error(request, str(e))
            return redirect("billing_page")

        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, "Something went wrong. Please try again.")
            return redirect("billing_page")
        

def get_product_details(request):
    product_id = request.GET.get("product_id")

    try:
        product = Product.objects.get(product_id=product_id)

        return JsonResponse({
            "success": True,
            "unit_price": product.unit_price,
            "tax_percentage": product.tax_percentage
        })

    except Product.DoesNotExist:
        return JsonResponse({
            "success": False
        })