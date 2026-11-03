"""Streamlit dashboard for the generated medallion outputs."""

from __future__ import annotations

import sys
import json
from pathlib import Path

import streamlit as st
import plotly.express as px

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import configured_path, load_config
from ai_analyzer import (
    build_summary_payload,
    payload_fingerprint,
    save_cached_summary,
    summarize_with_ollama,
)


config = load_config()
st.set_page_config(page_title="Spark Medallion Dashboard", layout="wide")


@st.cache_data(ttl=5)
def load_parquet(path: str):
    import pandas as pd

    return pd.read_parquet(path)


def get_dashboard_filters() -> tuple[tuple[str, ...], object | None, object | None]:
    import pandas as pd

    silver_path = configured_path("silver", "events")
    if not silver_path.exists():
        return (), None, None
    frame = load_parquet(str(silver_path))
    frame["event_date"] = pd.to_datetime(
        frame["event_date"], errors="coerce"
    ).dt.date
    min_date = frame["event_date"].min()
    max_date = frame["event_date"].max()
    with st.sidebar:
        st.header("Dashboard filters")
        event_types = sorted(frame["event_type"].dropna().unique())
        selected_types = st.multiselect(
            "Event types", event_types, default=event_types
        )
        selected_dates = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date = end_date = selected_dates
    return tuple(selected_types), start_date, end_date


selected_types, start_date, end_date = get_dashboard_filters()


def render_dashboard(
    selected_types: tuple[str, ...],
    start_date: object | None,
    end_date: object | None,
) -> None:
    st.title("Spark Medallion Dashboard")
    st.caption("Auto-refresh disabled. Use browser refresh or dashboard controls to update.")

    import pandas as pd

    silver_path = configured_path("silver", "events")
    gold_path = configured_path("gold", "daily_metrics")
    silver_frame = load_parquet(str(silver_path)) if silver_path.exists() else None
    gold_frame = load_parquet(str(gold_path)) if gold_path.exists() else None
    selected_product = st.session_state.get("selected_product")

    if silver_frame is not None:
        silver_frame["event_date"] = pd.to_datetime(
            silver_frame["event_date"], errors="coerce"
        ).dt.date
        if start_date is None or end_date is None:
            filtered_silver = silver_frame.iloc[0:0].copy()
        else:
            filtered_silver = silver_frame[
                silver_frame["event_type"].isin(selected_types)
                & silver_frame["event_date"].between(start_date, end_date)
            ].copy()
            if selected_product:
                filtered_silver = filtered_silver[
                    filtered_silver["product"] == selected_product
                ]
    else:
        filtered_silver = None

    if filtered_silver is not None and not filtered_silver.empty:
        total_events = len(filtered_silver)
        unique_users = filtered_silver["user_id"].nunique()
        total_amount = filtered_silver["amount"].sum()
        avg_amount = filtered_silver["amount"].mean()
        kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
        kpi_1.metric("Total events", f"{total_events:,}")
        kpi_2.metric("Unique users", f"{unique_users:,}")
        kpi_3.metric("Net amount", f"{total_amount:,.2f}")
        kpi_4.metric("Average amount", f"{avg_amount:,.2f}")

        st.subheader("Executive overview")
        daily = (
            filtered_silver.groupby("event_date", as_index=True)
            .agg(
                events=("event_id", "count"),
                unique_users=("user_id", "nunique"),
                net_amount=("amount", "sum"),
            )
            .sort_index()
        )
        product_mix = (
            filtered_silver.groupby("product", as_index=False)
            .agg(events=("event_id", "count"), net_amount=("amount", "sum"))
            .sort_values("events", ascending=False)
        )
        event_mix = (
            filtered_silver.groupby("event_type", as_index=False)
            .agg(events=("event_id", "count"), net_amount=("amount", "sum"))
            .sort_values("events", ascending=False)
            .set_index("event_type")
        )
        left, right = st.columns(2)
        with left:
            st.markdown("**Daily event and user trend**")
            st.line_chart(daily[["events", "unique_users"]])
        with right:
            st.markdown("**Product mix — click a bar to filter**")
            product_chart = px.bar(
                product_mix,
                x="product",
                y="events",
                color="product",
                title="Events by product",
            )
            selection = st.plotly_chart(
                product_chart,
                use_container_width=True,
                key="product_mix_chart",
                on_select="rerun",
                selection_mode=("points",),
            )
            points = selection.selection.get("points", []) if selection else []
            if points:
                clicked_product = points[0].get("x")
                if clicked_product in product_mix["product"].tolist():
                    st.session_state["selected_product"] = clicked_product
                    st.rerun()

        st.markdown("**Event type mix**")
        st.bar_chart(event_mix[["events"]])
        if selected_product:
            if st.button(f"Clear product filter: {selected_product}"):
                st.session_state.pop("selected_product", None)
                st.rerun()

        st.subheader("Financial and activity analysis")
        left, right = st.columns(2)
        with left:
            st.markdown("**Daily net amount**")
            st.area_chart(daily[["net_amount"]])
        with right:
            user_activity = (
                filtered_silver.groupby("user_id", as_index=False)
                .agg(events=("event_id", "count"), amount=("amount", "sum"))
                .sort_values("events", ascending=False)
                .head(15)
                .set_index("user_id")
            )
            st.markdown("**Top 15 users by activity**")
            st.bar_chart(user_activity[["events"]])

        with st.expander("Filtered data table"):
            st.dataframe(
                filtered_silver.sort_values("event_time", ascending=False).head(100),
                use_container_width=True,
            )
    else:
        st.warning("No data matches the selected filters.")

    audit_dir = Path(__file__).resolve().parents[1] / config["data_pipeline"]["audit_dir"]
    quality_dir = Path(__file__).resolve().parents[1] / config["data_pipeline"]["quality_dir"]
    if config["visualization"]["streamlit_audit_enabled"]:
        audits = sorted(audit_dir.glob("*.json"), reverse=True)
        if audits:
            latest_audit = json.loads(audits[0].read_text(encoding="utf-8"))
            st.metric("Last pipeline status", latest_audit["status"])
            st.caption(f"Run ID: {latest_audit['run_id']}")

    if config["visualization"]["streamlit_quality_metrics_enabled"]:
        reports = sorted(quality_dir.glob("*.json"), reverse=True)
        if reports:
            st.subheader("Data connection")
            st.success("Connected")

    if (
        config["ai_integration"]["ollama_enabled"]
        and config["ai_integration"]["send_gold_data_to_ollama"]
        and config["visualization"]["streamlit_show_ollama_response"]
    ):
        st.subheader("AI data analysis")
        bronze_path = configured_path("bronze", "events")
        if bronze_path.exists() and silver_frame is not None and gold_frame is not None:
            bronze_frame = load_parquet(str(bronze_path))
            if bronze_frame is None:
                st.info("Run the pipeline before requesting an AI summary.")
            else:
                payload = build_summary_payload(
                    bronze_frame,
                    silver_frame,
                    gold_frame,
                    config["ai_integration"]["max_rows"],
                )
                project_root = Path(__file__).resolve().parents[1]
                fingerprint = payload_fingerprint(payload)
                cache_key = f"ai_summary_{fingerprint}"
                cached_summary = st.session_state.get(cache_key)

                if cached_summary:
                    st.success("AI analysis for the current dataset")
                    st.markdown(cached_summary)

                if st.button("Generate new AI analysis", type="primary"):
                    with st.spinner("Ollama is analyzing all medallion layers..."):
                        try:
                            summary = summarize_with_ollama(payload, config)
                            save_cached_summary(project_root, fingerprint, summary)
                            st.session_state[cache_key] = summary
                            st.rerun()
                        except RuntimeError as exc:
                            st.error(str(exc))
        else:
            st.info("Run the pipeline before requesting an AI summary.")

    if not config["visualization"]["streamlit_layer_preview_enabled"]:
        return

    st.subheader("Layer previews")
    for layer, dataset in [
        ("bronze", "events"),
        ("silver", "events"),
        ("gold", "daily_metrics"),
    ]:
        path = configured_path(layer, dataset)
        if path.exists():
            frame = load_parquet(str(path))
            st.markdown(f"**{layer.title()}**")
            st.dataframe(frame.head(20), use_container_width=True)
            if layer == "gold" and config["visualization"]["streamlit_charts_enabled"]:
                st.line_chart(frame.set_index("event_date")[["event_count", "unique_users"]])
        else:
            st.info(f"{layer.title()} output is not available yet.")


render_dashboard(selected_types, start_date, end_date)
