"""
☕ Afficionado Coffee Roasters - Product Optimization & Revenue Contribution Analysis
Streamlit Dashboard

Features:
- KPI Cards
- Filters: category, product_type, store_location, top-N slider
- Product ranking by volume & revenue
- Category revenue distribution
- Popularity vs Revenue scatter
- Pareto 80/20 analysis
- Drill-down tables
- Hero products identification
"""
import streamlit as st
import pandas as pd
import pathlib
import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from src.data_loader import load_and_prepare
from src.analysis import (
    product_popularity, revenue_contribution, category_performance,
    product_type_performance, pareto_analysis, kpi_summary, volume_vs_revenue_mismatch
)
from src.visualizations import (
    category_donut, top_products_bar, pareto_chart, volume_vs_revenue_scatter,
    store_performance, size_performance
)

st.set_page_config(page_title="Afficionado Coffee - Product Intelligence", layout="wide", page_icon="☕")

# --- Header ---
st.title("☕ Product Optimization & Revenue Contribution Analysis")
st.markdown("**Afficionado Coffee Roasters | 3 NYC Locations | 149,116 Transactions (Jan-Jun 2025)**")
st.markdown("---")

# --- Data Loading ---
@st.cache_data
def get_data():
    base = pathlib.Path(__file__).parent.parent
    # Try multiple possible locations
    possible_paths = [
        base / "data" / "Afficionado_Coffee_Roasters_Full_149k.csv",
        base / "data" / "sample_1000.csv",
        pathlib.Path("/mnt/data/Afficionado_Project/data/Afficionado_Coffee_Roasters_Full_149k.csv"),
        "https://docs.google.com/spreadsheets/d/14CqwUgV3M37tz0ymk_utin29aDAKtdJA/export?format=csv"
    ]
    for p in possible_paths:
        try:
            if str(p).startswith("http"):
                continue
            if pathlib.Path(p).exists():
                df = load_and_prepare(str(p))
                return df
        except Exception as e:
            continue
    # fallback: generate minimal demo data if not found
    st.warning("Real dataset not found - using demo sample. Place your CSV in data/ folder.")
    # Create small demo
    import numpy as np
    demo = pd.DataFrame({
        "transaction_id": range(1,101),
        "product_category": ["Coffee"]*50 + ["Tea"]*30 + ["Bakery"]*20,
        "product_type": ["Barista Espresso"]*50 + ["Brewed Chai tea"]*30 + ["Scone"]*20,
        "product_detail": ["Latte Rg"]*20 + ["Earl Grey Rg"]*30 + ["Dark chocolate Lg"]*25 + ["Oatmeal Scone"]*25,
        "product_id": [1]*20 + [40]*30 + [56]*25 + [60]*25,
        "unit_price": [4.25]*20 + [2.5]*30 + [4.5]*25 + [3.0]*25,
        "transaction_qty": [1]*100,
        "store_location": ["Lower Manhattan"]*60 + ["Hell's Kitchen"]*40,
        "Revenue": [4.25]*20 + [2.5]*30 + [4.5]*25 + [3.0]*25,
        "size": ["Regular"]*50 + ["Large"]*50
    })
    return demo

df = get_data()

# --- Sidebar Filters ---
st.sidebar.header("🔧 Filters")
all_categories = ["All"] + sorted(df["product_category"].unique().tolist())
selected_category = st.sidebar.selectbox("Category", all_categories)

if selected_category != "All":
    filtered_df = df[df["product_category"] == selected_category]
    product_types = ["All"] + sorted(filtered_df["product_type"].unique().tolist())
else:
    filtered_df = df
    product_types = ["All"] + sorted(df["product_type"].unique().tolist())

selected_type = st.sidebar.selectbox("Product Type", product_types)

store_locations = ["All"] + sorted(df["store_location"].unique().tolist())
selected_store = st.sidebar.selectbox("Store Location", store_locations)

top_n = st.sidebar.slider("Top-N Products", min_value=5, max_value=30, value=10, step=1)

# Apply filters
if selected_type != "All":
    filtered_df = filtered_df[filtered_df["product_type"] == selected_type]
if selected_store != "All":
    filtered_df = filtered_df[filtered_df["store_location"] == selected_store]

st.sidebar.markdown("---")
st.sidebar.info(f"Filtered transactions: **{len(filtered_df):,}** / {len(df):,}")

# --- Analysis ---
prod_agg_raw = product_popularity(filtered_df)
prod_agg = revenue_contribution(filtered_df, prod_agg_raw)
cat_df = category_performance(filtered_df)
type_df = product_type_performance(filtered_df)
pareto_df, n_80 = pareto_analysis(prod_agg)
kpis = kpi_summary(filtered_df, prod_agg, cat_df, n_80)

# --- KPI Cards ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Revenue", f"${kpis['total_revenue']:,.0f}")
col2.metric("Total Units", f"{kpis['total_units']:,}")
col3.metric("Transactions", f"{kpis['total_transactions']:,}")
col4.metric("Unique Products", f"{kpis['unique_products']}")
col5.metric("Top Category", f"{kpis['top_category']} ({kpis['top_category_share']}%)")

col6, col7, col8, col9 = st.columns(4)
col6.metric("Avg per Transaction", f"${kpis['avg_revenue_per_transaction']:.2f}")
col7.metric("Products for 80% Rev", f"{kpis['products_for_80_pct']} ({kpis['concentration_ratio']}%)")
col8.metric("Long-tail Products", f"{kpis['long_tail_products']}")
col9.metric("Long-tail Rev %", f"{kpis['long_tail_revenue_pct']}%")

st.markdown("---")

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Product Ranking", "📦 Category Analysis", "⚖️ Volume vs Revenue", "📈 Pareto & Risk", "🔍 Drill-Down & Hero Products"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig_vol = top_products_bar(prod_agg, metric="total_units", top_n=top_n, title=f"Top {top_n} by Volume (Popularity)")
        st.plotly_chart(fig_vol, use_container_width=True)
    with c2:
        fig_rev = top_products_bar(prod_agg, metric="total_revenue", top_n=top_n, title=f"Top {top_n} by Revenue (Profitability)")
        st.plotly_chart(fig_rev, use_container_width=True)
    
    st.markdown("### Least Selling Products (Bottom 10 by Volume)")
    bottom = prod_agg.sort_values("total_units").head(10)
    st.dataframe(bottom[["product_detail","product_category","total_units","total_revenue","revenue_share_pct"]], use_container_width=True)

with tab2:
    c1, c2 = st.columns([1,1])
    with c1:
        fig_cat = category_donut(cat_df)
        st.plotly_chart(fig_cat, use_container_width=True)
        st.dataframe(cat_df, use_container_width=True)
    with c2:
        st.markdown("#### Product Type Contribution within Category")
        st.dataframe(type_df, use_container_width=True, height=400)
        # Store performance
        fig_store, store_df = store_performance(filtered_df)
        st.plotly_chart(fig_store, use_container_width=True)

with tab3:
    fig_scatter = volume_vs_revenue_scatter(prod_agg)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("#### Volume Rank vs Revenue Rank Mismatch (Price Opportunity)")
    mismatch = volume_vs_revenue_mismatch(prod_agg)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**High Volume, Low Revenue** (Underpriced / Popular but cheap)")
        st.dataframe(mismatch.head(10)[["product_detail","total_units","total_revenue","volume_rank","revenue_rank","rank_diff","efficiency_score"]], use_container_width=True)
    with c2:
        st.markdown("**Low Volume, High Revenue** (Premium / High price)")
        st.dataframe(mismatch.tail(10)[["product_detail","total_units","total_revenue","volume_rank","revenue_rank","rank_diff","efficiency_score"]], use_container_width=True)

    # Size analysis
    fig_size, size_df = size_performance(filtered_df)
    if fig_size:
        st.plotly_chart(fig_size, use_container_width=True)

with tab4:
    fig_pareto = pareto_chart(pareto_df, n_80)
    st.plotly_chart(fig_pareto, use_container_width=True)
    
    st.markdown(f"""
    **Pareto Insight:** Only **{n_80} out of {kpis['unique_products']} products ({kpis['concentration_ratio']}%)** drive 80% of revenue.
    This is **not classic 80/20** (which would be ~16 products). Revenue is more distributed = healthier menu balance, 
    but **{kpis['long_tail_products']} products** in the long tail generate only **{kpis['long_tail_revenue_pct']}%** revenue - candidates for review.
    """)
    
    st.markdown("#### Revenue Anchors vs Long Tail")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Revenue Anchors (Top {n_80})** - Protect these!")
        st.dataframe(pareto_df.head(n_80)[["product_detail","product_category","total_revenue","cumulative_pct","revenue_share_pct"]], use_container_width=True)
    with c2:
        st.markdown(f"**Long Tail (Bottom {kpis['long_tail_products']})** - Review / Optimize")
        st.dataframe(pareto_df.tail(kpis['long_tail_products'])[["product_detail","product_category","total_revenue","cumulative_pct","revenue_share_pct"]], use_container_width=True)

with tab5:
    st.markdown("### 🏆 Hero Products (Composite Score: 40% Revenue + 40% Volume + 20% Efficiency)")
    hero_df = prod_agg.sort_values("hero_score", ascending=False).head(top_n)
    st.dataframe(hero_df[["product_detail","product_category","product_type","total_units","total_revenue","revenue_share_pct","efficiency_score","hero_score"]], use_container_width=True)
    
    st.markdown("### Full Product Performance Table")
    st.dataframe(
        prod_agg[["product_id","product_detail","product_category","product_type","unit_price","total_units","total_transactions","total_revenue","revenue_share_pct","volume_rank","revenue_rank","efficiency_score","hero_score"]].sort_values("hero_score", ascending=False),
        use_container_width=True,
        height=600
    )
    csv = prod_agg.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Product Performance CSV", csv, "product_performance.csv", "text/csv")

# --- Footer Insights ---
st.markdown("---")
st.markdown("""
### 💡 Key Business Insights (Based on full dataset 149k records)
- **Coffee is King:** 38.63% revenue share - protect supply chain & quality
- **Size Matters:** Regular (Rg) and Large (Lg) dominate top sellers - Small sizes underperform consistently
- **Volume ≠ Revenue:** Earl Grey Rg #1 in volume (4,708 units) but #26 in revenue - pricing opportunity
- **True Hero:** Dark Chocolate Lg (69.5 hero score) balances volume, revenue, efficiency
- **Menu Risk:** 52.5% of menu drives 80% revenue - healthy vs classic 80/20, but 38 long-tail products need review
- **Chocolate Gap:** Drinking Chocolate has only Hot Chocolate type - add variety (white chocolate, mocha flavors)
- **Bakery Power:** Scones = 44.79% of bakery revenue - focus bakery merchandising here
""")

st.markdown("---")
st.caption("Built for Afficionado Coffee Roasters | Product Optimization & Revenue Contribution Analysis | Tools: Python, Pandas, Plotly, Streamlit")
