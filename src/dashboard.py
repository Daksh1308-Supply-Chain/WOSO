import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.config import SimulationConfig
from src.warehouse import WarehouseSimulation
from src.analytics import Analytics

st.set_page_config(page_title="Warehouse Simulation Dashboard", layout="wide")
st.title(":factory: Warehouse Operations Simulation Dashboard")

with st.sidebar:
    st.header("Configuration")
    num_workers = st.slider("Number of Workers", 1, 20, 5)
    num_packing = st.slider("Packing Stations", 1, 10, 3)
    num_forklifts = st.slider("Forklifts", 1, 10, 2)
    orders_per_hour = st.slider("Orders per Hour", 5, 60, 20)
    seed = st.number_input("Random Seed", value=42, step=1)
    
    if st.button("Run Simulation", type="primary"):
        st.session_state.run = True
    else:
        st.session_state.run = False

col1, col2, col3, col4 = st.columns(4)

if st.session_state.get('run'):
    config = SimulationConfig(
        num_workers=num_workers,
        num_packing_stations=num_packing,
        num_forklifts=num_forklifts,
        orders_per_hour=orders_per_hour,
        random_seed=seed
    )
    
    with st.spinner("Running simulation..."):
        sim = WarehouseSimulation(config)
        sim.run()
    
    total_time = config.working_hours * 60 * config.simulation_days
    worker_util = sim.workers.get_utilization(total_time)
    
    analytics = Analytics(config)
    kpis = analytics.compute_kpis(sim.orders, sim.completed_orders, total_time, worker_util)
    
    col1.metric("Orders Completed", kpis.get('orders_completed', 0))
    col2.metric("Avg Completion Time", f"{kpis.get('avg_completion_time', 0):.1f} min")
    col3.metric("Worker Utilization", f"{kpis.get('worker_utilization', 0):.1f}%")
    col4.metric("Throughput/Day", kpis.get('throughput_per_day', 0))
    
    df = analytics.create_dataframe(sim.completed_orders)
    
    tab1, tab2, tab3 = st.tabs(["Charts", "Order Data", "KPIs"])
    
    with tab1:
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        if not df.empty:
            axes[0, 0].hist(df['completion_time'], bins=20, color='steelblue', edgecolor='black')
            axes[0, 0].set_title('Order Completion Times')
            
            axes[0, 1].hist(df['pick_duration'], bins=15, color='coral', edgecolor='black')
            axes[0, 1].set_title('Picking Duration')
            
            axes[0, 2].hist(df['pack_duration'], bins=15, color='green', edgecolor='black', alpha=0.7)
            axes[0, 2].set_title('Packing Duration')
        
        metrics = ['avg_completion_time', 'avg_pick_time', 'avg_pack_time', 'avg_waiting_time']
        values = [kpis.get(m, 0) for m in metrics]
        axes[1, 0].bar(['Completion', 'Picking', 'Packing', 'Waiting'], values, color=['steelblue', 'coral', 'green', 'orange'])
        axes[1, 0].set_title('Average Times (minutes)')
        
        t_values = [kpis.get('orders_completed', 0), kpis.get('orders_pending', 0), kpis.get('throughput_per_day', 0)]
        axes[1, 1].bar(['Completed', 'Pending', 'Throughput'], t_values, color=['green', 'red', 'blue'])
        axes[1, 1].set_title('Order Statistics')
        
        util = kpis.get('worker_utilization', 0)
        axes[1, 2].bar(['Worker Util'], [util], color='purple')
        axes[1, 2].set_ylim(0, 100)
        axes[1, 2].axhline(y=85, color='r', linestyle='--', label='Max Target')
        axes[1, 2].axhline(y=70, color='g', linestyle='--', label='Min Target')
        axes[1, 2].legend()
        axes[1, 2].set_title('Worker Utilization')
        
        plt.tight_layout()
        st.pyplot(fig)
    
    with tab2:
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No orders completed.")
    
    with tab3:
        st.json(kpis)

else:
    st.info("Configure parameters in the sidebar and click 'Run Simulation'")
