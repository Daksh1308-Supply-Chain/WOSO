from typing import List, Dict
from src.config import Order, Product

class InventoryManager:
    def __init__(self, products: List[Product]):
        self.products: Dict[int, Product] = {p.product_id: p for p in products}

    def allocate(self, order: Order) -> bool:
        can_fulfill = True
        for pid in order.items:
            if pid not in self.products or self.products[pid].quantity <= 0:
                can_fulfill = False
                break
        if can_fulfill:
            for pid in order.items:
                self.products[pid].quantity -= 1
        return can_fulfill

    def get_product_location(self, product_id: int):
        return self.products[product_id].location

    def get_stock_level(self, product_id: int) -> int:
        return self.products[product_id].quantity

    def restock(self, product_id: int, quantity: int = 50):
        if product_id in self.products:
            self.products[product_id].quantity += quantity

    def get_low_stock_products(self) -> List[int]:
        return [pid for pid, p in self.products.items() if p.quantity <= p.reorder_level]
