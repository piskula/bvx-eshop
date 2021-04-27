from datetime import datetime


class Order:
    def __init__(self, date, title, number, total, order_items, address):
        self.date = datetime.fromisoformat(date)
        self.title = title
        self.number = number
        self.total = total
        self.order_items = order_items
        self.address = address

    def __str__(self):
        return "Order(date=" + self.date.strftime("%d %b %H:%M") + \
           ", title=" + self.title + \
           ", number=" + self.number + \
           ", total=" + str(self.total) + \
           ", order_items_amount=" + str(len(self.order_items)) + \
           ", address=" + str(self.address) + \
           ")"
