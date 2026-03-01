"""
URL configuration for billing_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from billing.views import billing_page, generate_bill, get_product_details

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', billing_page, name="billing_page"),
    path('generate/', generate_bill, name="generate_bill"),
    path('get-product/', get_product_details, name='get_product_details'),
]