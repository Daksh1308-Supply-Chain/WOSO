# Future Enhancements — Roadmap & TODO

> Tracking progress for Section 19 of the PRD.
> **Status:** 🟢 Planned | 🟡 In Progress | ✅ Complete | 🔴 Blocked

---

## Phase 1 — Core Improvements

| # | Enhancement | Priority | Complexity | Status | Notes |
|---|---|---|---|---|---|
| 1 | Multi-shift / break scheduling | High | Medium | 🟢 | Model multiple shifts with staggered breaks, handover logic |
| 2 | Variable walking speeds by worker type | High | Low | 🟢 | Add configurable speed per worker (e.g., trainee vs experienced) |
| 3 | Warehouse heat maps | Medium | Medium | 🟢 | Plot pick frequency density on warehouse layout |

---

## Phase 2 — Intelligence & Automation

| # | Enhancement | Priority | Complexity | Status | Notes |
|---|---|---|---|---|---|
| 4 | AGV (Automated Guided Vehicle) simulation | High | High | 🟢 | Model AGVs as SimPy resources with charging, routing, collision avoidance |
| 5 | Robot picker simulation | Medium | High | 🟢 | Autonomous picking robots vs human workers — cost/time tradeoffs |
| 6 | Machine learning for worker scheduling | Medium | High | 🟢 | Predict shift demand, optimize worker allocation using historical patterns |
| 7 | AI-based demand forecasting | Medium | High | 🟢 | Time-series forecast of order volume to pre-allocate resources |

---

## Phase 3 — Integration & Scale

| # | Enhancement | Priority | Complexity | Status | Notes |
|---|---|---|---|---|---|
| 8 | Multi-warehouse network simulation | High | High | 🟢 | Connect multiple warehouses, cross-docking, inter-warehouse transfers |
| 9 | Real-time dashboard with live data | Medium | Medium | 🟢 | WebSocket/Streamlit live-updating dashboard during simulation |
| 10 | Digital Twin integration | Low | Very High | 🟢 | Synchronize simulation state with real warehouse IoT/sensor data |
| 11 | RFID-enabled warehouse model | Low | Medium | 🟢 | Item-level tracking, location updates, cycle counting |
| 12 | ERP integration | Low | Very High | 🟢 | API connectors to WMS/ERP systems for real data feed |

---

## Details & Implementation Ideas

### 1. Multi-shift / Break Scheduling

- Extend `SimulationConfig` with `shifts: List[Shift]` dataclass
- Each shift has start time, end time, lunch break duration
- Workers become unavailable during breaks
- Handover logic passes pending orders between shifts

```python
@dataclass
class Shift:
    name: str
    start_hour: float  # e.g., 6.0 = 6:00 AM
    end_hour: float    # e.g., 14.0 = 2:00 PM
    break_start: float = 12.0
    break_duration: float = 0.5
```

### 2. Variable Walking Speeds

- Add `walking_speed: float` field to a `Worker` dataclass
- WorkerPool assigns workers with heterogeneous speeds
- PickingProcess uses the assigned worker's speed

### 3. Warehouse Heat Maps

- Track pick frequency per product location during simulation
- Overlay heat map on warehouse grid using matplotlib `imshow` or hexbin
- Identify hot zones vs underutilized storage areas

### 4. AGV Simulation

- SimPy `Container` or `Resource` for AGV fleet
- Routing logic: nearest available AGV, charge level tracking, recharge stations
- Compare AGV vs human picking costs

### 5. Robot Picker Simulation

- Dedicated robot resource with different speed/cost params
- Mixed model: robots handle high-volume aisles, humans handle variable items
- KPI: cost per pick, robot utilization, human-robot handoff time

### 6. ML Worker Scheduling

- Collect simulation data: orders per hour, pick times, wait times
- Train model (e.g., random forest, LSTM) to predict optimal staffing
- Output: recommended worker count per hour/shift

### 7. AI Demand Forecasting

- Generate synthetic historical order data from simulation
- Apply Prophet, ARIMA, or LSTM to forecast next-day demand
- Feed forecast back into simulation config for proactive resource allocation

### 8. Multi-Warehouse Network

- Multiple `WarehouseSimulation` instances connected via `simpy.Store`
- Cross-docking: orders routed through intermediate warehouses
- Transport time between warehouses configurable

### 9. Real-Time Dashboard

- Extend Streamlit dashboard with `st.empty()` + loop for live updates
- Display current simulation time, orders in progress, queue lengths
- Use `st.line_chart` for time-series KPIs

### 10. Digital Twin

- MQTT/Kafka integration for real sensor data
- Simulation starts from current warehouse state (not empty)
- Live comparison: simulated vs actual throughput

### 11. RFID Model

- Each item gets an RFID read event at each process step
- Track item-level cycle time, dwell time in storage
- Simulation of read failures/retries

### 12. ERP Integration

- REST API connector to pull real orders, inventory, worker schedules
- Push simulation recommendations back to ERP
- OData/GraphQL interfaces

---

## Changelog

| Date | Change |
|---|---|
| 2026-07-07 | Initial future enhancements roadmap created |
