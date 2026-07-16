import simpy
import random
from typing import List, Optional
from src.config import SimulationConfig, Order, create_default_products, ORDER_PENDING, ORDER_PICKING, ORDER_PACKING, ORDER_QUALITY_CHECK, ORDER_SHIPPING, ORDER_COMPLETED
from src.order_generator import OrderGenerator
from src.inventory import InventoryManager
from src.worker import WorkerPool
from src.picking import PickingProcess
from src.packing import PackingProcess
from src.shipping import ShippingProcess
from src.costing import CostTracker
from src.agv import AGVManager
from src.robot_picker import RobotPool

class WarehouseSimulation:
    def __init__(self, config: SimulationConfig, forecast_rates: Optional[List[float]] = None):
        self.config = config
        self.env = simpy.Environment()
        self.rng = random.Random(config.random_seed)
        
        self.products = create_default_products(50, config.random_seed)
        self.inventory = InventoryManager(self.products)
        self.workers = WorkerPool(self.env, config)
        self.picking = PickingProcess(self.env, config, self.inventory)
        self.packing = PackingProcess(self.env, config)
        self.shipping = ShippingProcess(self.env, config)
        self.agv_manager = AGVManager(self.env, config)
        self.robot_pool = RobotPool(self.env, config)
        
        self.cost_tracker = CostTracker(config.cost_config)

        self.orders: list[Order] = []
        self.completed_orders: list[Order] = []
        self.pending_orders: list[Order] = []
        self.forecast_rates = forecast_rates
        self.order_generator = OrderGenerator(
            self.env, config, self.products, self._on_order_created,
            forecast_rates=forecast_rates
        )
    
    def _on_order_created(self, order: Order):
        self.orders.append(order)
        self.pending_orders.append(order)
        self.env.process(self._process_order(order))

    def _choose_transport_method(self, order: Order) -> str:
        mode = self.config.agv_mode
        if mode == "disabled" or self.config.num_agvs == 0:
            return "human"
        if mode == "agv_only":
            return "agv"
        distance = self.picking.calculate_travel_distance(order.items)
        return "agv" if distance > self.config.agv_distance_threshold else "human"

    def _process_order(self, order: Order):
        allocated = self.inventory.allocate(order)
        if not allocated:
            self.pending_orders.remove(order)
            return

        order.state = ORDER_PICKING
        order.pick_start_time = self.env.now
        if self.robot_pool.order_is_robot_eligible(order.items):
            with self.robot_pool.request() as req:
                yield req
                pick_time = self.picking.calculate_robot_picking_time(order)
                self.cost_tracker.record_robot_time(pick_time)
                yield self.env.timeout(pick_time)
        elif self._choose_transport_method(order) == "agv":
            with self.agv_manager.request() as req:
                yield req
                pick_time = self.picking.calculate_agv_picking_time(order)
                self.cost_tracker.record_agv_time(pick_time)
                yield self.env.timeout(pick_time)
        else:
            with self.workers.request() as req:
                yield req
                worker_speed = self.workers.get_next_worker_speed()
                pick_time = self.picking.calculate_picking_time(order, worker_speed)
                self.cost_tracker.record_labor_time(pick_time)
                yield self.env.timeout(pick_time)
        order.pick_end_time = self.env.now
        
        order.state = ORDER_PACKING
        order.pack_start_time = self.env.now
        self.packing.record_queue()
        with self.packing.request() as req:
            yield req
            pack_time = self.packing.get_packing_time()
            self.cost_tracker.record_labor_time(pack_time)
            yield self.env.timeout(pack_time)
        order.pack_end_time = self.env.now
        
        order.state = ORDER_QUALITY_CHECK
        qc_time = self.config.quality_check_time
        self.cost_tracker.record_labor_time(qc_time)
        yield self.env.timeout(qc_time)
        
        order.state = ORDER_SHIPPING
        order.ship_start_time = self.env.now
        self.shipping.record_queue()
        with self.shipping.request() as req:
            yield req
            ship_time = self.shipping.get_shipping_time()
            self.cost_tracker.record_labor_time(ship_time)
            yield self.env.timeout(ship_time)
        order.ship_end_time = self.env.now
        
        order.state = ORDER_COMPLETED
        self.cost_tracker.record_completed_order()
        self.completed_orders.append(order)
        self.pending_orders.remove(order)
        self.shipping.ship_order(order)
    
    def run(self):
        self.order_generator.start()
        last_hour = max(s.end_hour for s in self.config.shifts) if self.config.shifts else self.config.working_hours
        total_time = last_hour * 60 * self.config.simulation_days
        self.env.run(until=total_time)
        self.cost_tracker.record_rent(self.config.simulation_days)
        forklift_minutes = total_time * (self.config.num_forklifts / max(1, self.config.num_workers))
        self.cost_tracker.record_forklift_time(forklift_minutes)
