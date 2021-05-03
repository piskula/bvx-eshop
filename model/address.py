class Address:
    def __init__(self, name, company, line_1, line_2, city, postcode, country):
        self.name = name
        self.company = company
        self.line_1 = line_1
        self.line_2 = line_2
        self.city = city
        self.postcode = postcode
        self.country = country

    def __str__(self):
        return "Address(name=" + self.name + \
           ", company=" + self.company + \
           ", line_1=" + self.line_1 + \
           ", line_2=" + self.line_2 + \
           ", city=" + self.city + \
           ", postcode=" + self.postcode + \
           ", country=" + self.country + \
           ")"
