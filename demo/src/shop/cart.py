from .pricing import total
from shop.models import Item


class Cart:
    def total(self):
        return total([Item()])
