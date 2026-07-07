import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import Product, Order
from src.inventory import InventoryManager

def test_allocate_sufficient_stock():
    products = [Product(product_id=1, name="Test", quantity=10, location=(10.0, 10.0), reorder_level=5)]
    inv = InventoryManager(products)
    order = Order(order_id=1, items=[1], arrival_time=0.0)
    assert inv.allocate(order) == True
    assert inv.get_stock_level(1) == 9

def test_allocate_insufficient_stock():
    products = [Product(product_id=1, name="Test", quantity=0, location=(10.0, 10.0), reorder_level=5)]
    inv = InventoryManager(products)
    order = Order(order_id=1, items=[1], arrival_time=0.0)
    assert inv.allocate(order) == False

def test_restock():
    products = [Product(product_id=1, name="Test", quantity=5, location=(10.0, 10.0), reorder_level=10)]
    inv = InventoryManager(products)
    inv.restock(1, 50)
    assert inv.get_stock_level(1) == 55

def test_low_stock():
    products = [Product(product_id=1, name="Test", quantity=3, location=(10.0, 10.0), reorder_level=5)]
    inv = InventoryManager(products)
    low = inv.get_low_stock_products()
    assert 1 in low

def test_get_location():
    products = [Product(product_id=1, name="Test", quantity=10, location=(25.5, 30.0), reorder_level=5)]
    inv = InventoryManager(products)
    assert inv.get_product_location(1) == (25.5, 30.0)

if __name__ == "__main__":
    test_allocate_sufficient_stock()
    test_allocate_insufficient_stock()
    test_restock()
    test_low_stock()
    test_get_location()
    print("All inventory tests passed!")
