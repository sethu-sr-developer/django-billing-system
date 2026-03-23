from django.contrib import messages
from django.shortcuts import redirect, render
from django.db import transaction
from billing.models import Product, Customer, Bill, BillItem, Denomination
from billing.utils import calculate_change
from django.core.mail import send_mail
import threading
from django.http import JsonResponse


# Async email sending
def send_invoice_email_async(subject, message, recipient):
    thread = threading.Thread(
        target=send_mail,
        args=(subject, message, 'shop@example.com', [recipient])
    )
    thread.start()


# Billing page
def billing_page(request):
    products = Product.objects.all()
    denominations = Denomination.objects.all()
    return render(request, "billing/billing.html", {
        "products": products,
        "denominations": denominations
    })


# Generate bill
def generate_bill(request):

    if request.method == "POST":

        try:
            with transaction.atomic():

                # Get customer details
                email = request.POST.get("email")
                paid_amount = float(request.POST.get("paid_amount"))

                customer, _ = Customer.objects.get_or_create(email=email)

                # Create initial bill
                bill = Bill.objects.create(
                    customer=customer,
                    total_amount=0,
                    paid_amount=paid_amount,
                    balance_amount=0
                )

                total_amount = 0

                # Get product inputs
                product_ids = request.POST.getlist("product_id")
                quantities = request.POST.getlist("quantity")

                # Loop through products
                for pid, qty in zip(product_ids, quantities):

                    product = Product.objects.get(product_id=pid)
                    qty = int(qty)

                    # Stock validation
                    if product.available_stock < qty:
                        raise ValueError(f"Insufficient stock for product {product.name}")

                    # Calculation
                    subtotal = product.unit_price * qty
                    tax = subtotal * (product.tax_percentage / 100)
                    total = subtotal + tax

                    # Save bill item
                    BillItem.objects.create(
                        bill=bill,
                        product=product,
                        quantity=qty,
                        price_without_tax=subtotal,
                        tax_amount=tax,
                        total_price=total
                    )

                    # Update stock
                    product.available_stock -= qty
                    product.save()

                    total_amount += total

                # Calculate balance
                balance = paid_amount - total_amount

                if balance < 0:
                    raise ValueError("Paid amount is less than total bill amount.")

                # Update bill
                bill.total_amount = total_amount
                bill.balance_amount = balance
                bill.save()

                # 🔥 Update denomination from UI
                denominations = Denomination.objects.all()

                for denom in denominations:
                    count = int(request.POST.get(f"denom_{denom.value}", 0))
                    denom.available_count = count
                    denom.save()

                # 🔥 Calculate change with validation
                try:
                    change_details = calculate_change(balance)
                except Exception as e:
                    raise ValueError(str(e))

                # Send email asynchronously
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


# AJAX API for product details
def get_product_details(request):
    product_id = request.GET.get("product_id")

    try:
        product = Product.objects.get(product_id=product_id)

        return JsonResponse({
            "success": True,
            "unit_price": product.unit_price,
            "tax_percentage": product.tax_percentage,
            "name": product.name
        })

    except Product.DoesNotExist:
        return JsonResponse({
            "success": False
        })


def customer_purchases(request):

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            customer = Customer.objects.get(email=email)
            bills = Bill.objects.filter(customer=customer).order_by('-created_at')

            return render(request, "billing/customer_purchases.html", {
                "bills": bills,
                "email": email
            })

        except Customer.DoesNotExist:
            messages.error(request, "Customer not found")
            return redirect("billing_page")

    return render(request, "billing/customer_search.html")

def bill_detail(request, bill_id):
    bill = Bill.objects.get(id=bill_id)

    return render(request, "billing/bill_detail.html", {
        "bill": bill
    })