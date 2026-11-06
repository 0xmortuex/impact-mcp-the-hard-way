from shop.cart import Cart


def test_cart():
    assert Cart().total() >= 0
