price = 99
quantity = int(input('Enter quantity:'))
total = quantity * price
discount = 0
if 10 <= quantity <= 19:
    discount = total * 0.1
elif 20 <= quantity <= 49:
    discount = total * 0.2
elif 50 <= quantity <= 99:
    discount = total * 0.3
elif quantity >= 100:
    discount = total * 0.4
print('Discount ', discount)
print('Total amount after the discount: ', total - discount)
