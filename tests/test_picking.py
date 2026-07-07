import sys
import os
import simpy
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import SimulationConfig, Product, Order
from src.inventory import InventoryManager
from src.picking import PickingProcess

def test_travel_distance():
    config = SimulationConfig()
    products = [
        Product(product_id=1, name="A", quantity=10, location=(50.0, 50.0), reorder_level=5),
        Product(product_id=2, name="B", quantity=10, location=(150.0, 100.0), reorder_level=5),
    ]
    inv = InventoryManager(products)
    env = simpy.Environment()
    picker = PickingProcess(env, config, inv)
    
    distance = picker.calculate_travel_distance([1, 2])
    packing = (150.0, 0.0)
    p1_to_p2 = ((50-150)**2 + (50-100)**2)**0.5
    p2_to_packing = ((150-150)**2 + (100-0)**2)**0.5
    packing_to_p1 = ((150-50)**2 + (0-50)**2)**0.5
    expected = packing_to_p1 + p1_to_p2 + p2_to_packing
    assert abs(distance - expected) < 0.01, f"Expected {expected}, got {distance}"

def test_single_item_distance():
    config = SimulationConfig()
    products = [Product(product_id=1, name="A", quantity=10, location=(100.0, 50.0), reorder_level=5)]
    inv = InventoryManager(products)
    env = simpy.Environment()
    picker = PickingProcess(env, config, inv)
    
    distance = picker.calculate_travel_distance([1])
    to_item = ((150-100)**2 + (0-50)**2)**0.5
    back = ((100-150)**2 + (50-0)**2)**0.5
    expected = to_item + back
    assert abs(distance - expected) < 0.01

if __name__ == "__main__":
    test_travel_distance()
    test_single_item_distance()
    print("All picking tests passed!")
