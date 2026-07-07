import simpy
import random
from src.config import SimulationConfig, Order, create_default_products, ORDER_PENDING, ORDER_PICKING, ORDER_PACKING, ORDER_QUALITY_CHECK, ORDER_SHIPPING, ORDER_COMPLETED
from src.order_generator import OrderGenerator
from src.inventory import InventoryManager
from src.worker import WorkerPool
from src.picking import PickingProcess
from src.packing import PackingProcess
from src.shipping import ShippingProcess

class WarehouseSimulation:
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.env = simpy.Environment()
        self.rng = random.Random(config.random_seed)
        
        self.products = create_default_products(50, config.random_seed)
        self.inventory = InventoryManager(self.products)
        self.workers = WorkerPool(self.env, config)
        self.picking = PickingProcess(self.env, config, self.inventory)
        self.packing = PackingProcess(self.env, config)
        self.shipping = ShippingProcess(self.env, config)
        
        self.orders: list[Order] = []
        self.completed_orders: list[Order] = []
        self.pending_orders: list[Order] = []
        self.order_generator = OrderGenerator(
            self.env, config, self.products, self._on_order_created
        )
    
    def _on_order_created(self, order: Order):
        self.orders.append(order)
        self.pending_orders.append(order)
        self.env.process(self._process_order(order))
    
    def _process_order(self, order: Order):
        allocated = self.inventory.allocate(order)
        if not allocated:
            self.pending_orders.remove(order)
            return
        
        order.state = ORDER_PICKING
        order.pick_start_time = self.env.now
        with self.workers.request() as req:
            yield req
            pick_time = self.picking.calculate_picking_time(order)
            yield self.env.timeout(pick_time)
        order.pick_end_time = self.env.now
        
        order.state = ORDER_PACKING
        order.pack_start_time = self.env.now
        self.packing.record_queue()
        with self.packing.request() as req:
            yield req
            pack_time = self.packing.get_packing_time()
            yield self.env.timeout(pack_time)
        order.pack_end_time = self.env.now
        
        order.state = ORDER_QUALITY_CHECK
        qc_time = self.config.quality_check_time
        yield self.env.timeout(qc_time)
        
        order.state = ORDER_SHIPPING
        order.ship_start_time = self.env.now
        self.shipping.record_queue()
        with self.shipping.request() as req:
            yield req
            ship_time = self.shipping.get_shipping_time()
            yield self.env.timeout(ship_time)
        order.ship_end_time = self.env.now
        
        order.state = ORDER_COMPLETED
        self.completed_orders.append(order)
        self.pending_orders.remove(order)
        self.shipping.ship_order(order)
    
    def run(self):
        self.order_generator.start()
        total_time = self.config.working_hours * 60 * self.config.simulation_days
        self.env.run(until=total_time)
