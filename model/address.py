class Address:
    def __init__(self, name, street, city):
        self.name = name
        self.street= street
        self.city = city

    def __str__(self):
        return "Address(name=" + self.name + \
           ", street=" + self.street + \
           ", city=" + self.city + \
           ")"
