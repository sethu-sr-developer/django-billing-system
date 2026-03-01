from django.db import models


# Product model stores all sellable items in the shop
class Product(models.Model):
    product_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    available_stock = models.IntegerField()
    unit_price = models.FloatField()
    tax_percentage = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.product_id})"


# Customer model stores unique customers by email
class Customer(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


# Bill model represents a single purchase transaction
class Bill(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.FloatField()
    paid_amount = models.FloatField()
    balance_amount = models.FloatField()

    def __str__(self):
        return f"Bill #{self.id} - {self.customer.email}"


# BillItem stores individual product entries under a bill
class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_without_tax = models.FloatField()
    tax_amount = models.FloatField()
    total_price = models.FloatField()


# Denomination model stores available currency units in shop
class Denomination(models.Model):
    value = models.IntegerField(unique=True)
    available_count = models.IntegerField()

    def __str__(self):
        return str(self.value)