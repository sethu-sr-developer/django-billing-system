from billing.models import Denomination

# Calculates change using greedy algorithm
def calculate_change(balance_amount):
    denominations = Denomination.objects.order_by('-value')
    result = {}

    for denom in denominations:
        if balance_amount <= 0:
            break

        required = balance_amount // denom.value
        usable = min(required, denom.available_count)

        if usable > 0:
            result[denom.value] = int(usable)
            balance_amount -= denom.value * usable

    # if balance_amount > 0:
    #     raise Exception("Insufficient denomination available")

    return result