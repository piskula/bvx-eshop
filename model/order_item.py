class OrderItem:
    def __init__(self, title, amount, price):
        self.title = title
        self.amount = amount
        self.price = price

    def __str__(self):
        return "OrderItem(title=" + self.title + \
           ", amount=" + self.amount + \
           ", price=" + self.price + \
           ")"
