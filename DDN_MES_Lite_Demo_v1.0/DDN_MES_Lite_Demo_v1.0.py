import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="MES Lite", layout="wide", page_icon="🏭")
st.title("🏭 MES Lite — Hardware Manufacturing")
st.caption("Production planning, WIP tracking, inventory, quality, and OEE in one lightweight app.")


def init_state() -> None:
    if "work_orders" not in st.session_state:
        st.session_state.work_orders = pd.DataFrame(
            [
                {
                    "wo_id": "WO-1001",
                    "product": "Controller Board",
                    "planned_qty": 500,
                    "completed_qty": 120,
                    "status": "In Progress",
                    "work_center": "SMT-01",
                    "due_date": "2026-05-10",
                },
                {
                    "wo_id": "WO-1002",
                    "product": "Power Module",
                    "planned_qty": 300,
                    "completed_qty": 0,
                    "status": "Planned",
                    "work_center": "ASSY-02",
                    "due_date": "2026-05-12",
                },
            ]
        )

    if "inventory" not in st.session_state:
        st.session_state.inventory = pd.DataFrame(
            [
                {"part_no": "PCB-CTRL-A", "description": "Control PCB", "on_hand": 680, "reorder_point": 300, "uom": "pcs"},
                {"part_no": "IC-MCU-48", "description": "Microcontroller", "on_hand": 240, "reorder_point": 500, "uom": "pcs"},
                {"part_no": "CONN-USB-C", "description": "USB-C Connector", "on_hand": 1200, "reorder_point": 400, "uom": "pcs"},
            ]
        )

    if "quality" not in st.session_state:
        st.session_state.quality = pd.DataFrame(
            [
                {"lot_id": "LOT-7781", "station": "ICT", "tested": 120, "fails": 4, "defect": "Solder Bridge"},
                {"lot_id": "LOT-7782", "station": "FCT", "tested": 80, "fails": 2, "defect": "Firmware Flash"},
            ]
        )

    if "downtime" not in st.session_state:
        st.session_state.downtime = pd.DataFrame(
            [
                {"machine": "SMT-01", "minutes": 35, "reason": "Feeder jam"},
                {"machine": "ASSY-02", "minutes": 15, "reason": "Material wait"},
            ]
        )


init_state()

# Sidebar
st.sidebar.header("Plant Controls")
plant = st.sidebar.selectbox("Plant", ["Plant A", "Plant B"])
shift = st.sidebar.selectbox("Shift", ["Day", "Swing", "Night"])
st.sidebar.write(f"**Now:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

# KPI row
wo_df = st.session_state.work_orders
inv_df = st.session_state.inventory
q_df = st.session_state.quality

open_wos = (wo_df["status"] != "Closed").sum()
completion = (wo_df["completed_qty"].sum() / wo_df["planned_qty"].sum() * 100) if wo_df["planned_qty"].sum() else 0
first_pass_yield = ((q_df["tested"].sum() - q_df["fails"].sum()) / q_df["tested"].sum() * 100) if q_df["tested"].sum() else 0
low_stock = (inv_df["on_hand"] < inv_df["reorder_point"]).sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Open Work Orders", int(open_wos))
c2.metric("Schedule Completion", f"{completion:.1f}%")
c3.metric("First Pass Yield", f"{first_pass_yield:.2f}%")
c4.metric("Low-Stock Parts", int(low_stock))

# Tabs
ops_tab, inv_tab, quality_tab, oee_tab = st.tabs(["Work Orders", "Inventory", "Quality", "OEE / Downtime"])

with ops_tab:
    st.subheader("Work Order Management")
    st.dataframe(wo_df, use_container_width=True)

    with st.form("add_wo"):
        st.markdown("### Add Work Order")
        c1, c2, c3 = st.columns(3)
        wo_id = c1.text_input("WO ID", value=f"WO-{1000 + len(wo_df) + 1}")
        product = c2.text_input("Product", value="New Assembly")
        work_center = c3.text_input("Work Center", value="ASSY-01")

        c4, c5, c6 = st.columns(3)
        planned_qty = c4.number_input("Planned Qty", min_value=1, value=100, step=10)
        due_date = c5.date_input("Due Date")
        status = c6.selectbox("Status", ["Planned", "In Progress", "On Hold", "Closed"])

        submit_wo = st.form_submit_button("Add Work Order")
        if submit_wo:
            new_row = {
                "wo_id": wo_id,
                "product": product,
                "planned_qty": int(planned_qty),
                "completed_qty": 0,
                "status": status,
                "work_center": work_center,
                "due_date": str(due_date),
            }
            st.session_state.work_orders = pd.concat([wo_df, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Added {wo_id}")

with inv_tab:
    st.subheader("Inventory & Material Availability")
    inv_view = inv_df.copy()
    inv_view["status"] = inv_view.apply(lambda r: "LOW" if r["on_hand"] < r["reorder_point"] else "OK", axis=1)
    st.dataframe(inv_view, use_container_width=True)

    with st.form("inventory_txn"):
        st.markdown("### Post Material Transaction")
        part = st.selectbox("Part", inv_df["part_no"].tolist())
        txn_type = st.radio("Type", ["Issue", "Receive"], horizontal=True)
        qty = st.number_input("Quantity", min_value=1, value=10)
        post = st.form_submit_button("Post")

        if post:
            idx = st.session_state.inventory.index[st.session_state.inventory["part_no"] == part][0]
            sign = -1 if txn_type == "Issue" else 1
            st.session_state.inventory.at[idx, "on_hand"] = max(0, int(st.session_state.inventory.at[idx, "on_hand"] + sign * qty))
            st.success(f"{txn_type} posted for {part}: {qty}")

with quality_tab:
    st.subheader("Quality Tracking")
    q_view = q_df.copy()
    q_view["yield_%"] = ((q_view["tested"] - q_view["fails"]) / q_view["tested"] * 100).round(2)
    st.dataframe(q_view, use_container_width=True)

    with st.form("quality_log"):
        st.markdown("### Log Inspection Result")
        c1, c2, c3 = st.columns(3)
        lot_id = c1.text_input("Lot ID", value=f"LOT-{7800 + len(q_df) + 1}")
        station = c2.selectbox("Station", ["AOI", "ICT", "FCT", "Final QA"])
        defect = c3.text_input("Top Defect", value="None")

        c4, c5 = st.columns(2)
        tested = c4.number_input("Units Tested", min_value=1, value=50)
        fails = c5.number_input("Units Failed", min_value=0, max_value=int(tested), value=0)

        submit_q = st.form_submit_button("Add Quality Record")
        if submit_q:
            row = {"lot_id": lot_id, "station": station, "tested": int(tested), "fails": int(fails), "defect": defect}
            st.session_state.quality = pd.concat([q_df, pd.DataFrame([row])], ignore_index=True)
            st.success(f"Logged quality result for {lot_id}")

with oee_tab:
    st.subheader("OEE Snapshot")
    planned_minutes = st.number_input("Planned Production Time (min)", min_value=1, value=480)
    runtime_minutes = max(0, planned_minutes - int(st.session_state.downtime["minutes"].sum()))

    total_planned = wo_df["planned_qty"].sum()
    total_completed = wo_df["completed_qty"].sum()
    good_units = q_df["tested"].sum() - q_df["fails"].sum()

    availability = runtime_minutes / planned_minutes if planned_minutes else 0
    performance = (total_completed / total_planned) if total_planned else 0
    quality = (good_units / q_df["tested"].sum()) if q_df["tested"].sum() else 0
    oee = availability * performance * quality * 100

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Availability", f"{availability*100:.1f}%")
    m2.metric("Performance", f"{performance*100:.1f}%")
    m3.metric("Quality", f"{quality*100:.1f}%")
    m4.metric("OEE", f"{oee:.1f}%")

    st.markdown("### Downtime Log")
    st.dataframe(st.session_state.downtime, use_container_width=True)

st.divider()
st.caption(f"Configured for {plant} • {shift} shift. Data is session-scoped for demo use.")
