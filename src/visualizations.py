"""
Visualization helpers using Plotly
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def category_donut(cat_df):
    fig = px.pie(cat_df, values="total_revenue", names="product_category", 
                 hole=0.5, title="Revenue Share by Category",
                 color_discrete_sequence=px.colors.sequential.RdBu)
    fig.update_traces(textinfo="percent+label", hovertemplate="%{label}: $%{value:,.0f} (%{percent})")
    fig.update_layout(height=400)
    return fig

def top_products_bar(product_agg, metric="total_revenue", top_n=10, title=None):
    df = product_agg.sort_values(metric, ascending=False).head(top_n)
    x_col = metric
    y_col = "product_detail"
    color_col = "product_category"
    fig = px.bar(df, x=x_col, y=y_col, orientation="h", color=color_col,
                 title=title or f"Top {top_n} by {metric.replace('_',' ').title()}",
                 hover_data=["total_units", "total_revenue", "revenue_share_pct"])
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=400 + top_n*15)
    return fig

def pareto_chart(pareto_df, n_80):
    df = pareto_df.copy()
    df["product_index"] = range(1, len(df)+1)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["product_index"], y=df["total_revenue"], name="Revenue per Product", marker_color="#8B4513"))
    fig.add_trace(go.Scatter(x=df["product_index"], y=df["cumulative_pct"], name="Cumulative %", yaxis="y2", mode="lines+markers", line=dict(color="#D2691E", width=3)))
    # 80% line
    fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="80% Threshold", secondary_y=True)
    fig.add_vline(x=n_80, line_dash="dot", line_color="green", annotation_text=f"{n_80} products = 80%")
    fig.update_layout(
        title=f"Pareto Analysis: {n_80} products drive 80% revenue ({n_80/len(df)*100:.1f}% of menu)",
        xaxis_title="Products ranked by revenue",
        yaxis_title="Revenue",
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0,100]),
        height=500
    )
    return fig

def volume_vs_revenue_scatter(product_agg):
    fig = px.scatter(product_agg, x="total_units", y="total_revenue", 
                     size="revenue_share_pct", color="product_category",
                     hover_name="product_detail", hover_data=["hero_score", "efficiency_score"],
                     title="Popularity vs Profitability (Size = Revenue Share)",
                     labels={"total_units":"Units Sold (Popularity)", "total_revenue":"Revenue (Profitability)"})
    fig.update_layout(height=500)
    return fig

def store_performance(df):
    store_df = df.groupby("store_location").agg(total_revenue=("Revenue","sum"), total_units=("transaction_qty","sum"), transactions=("transaction_id","count")).reset_index()
    fig = px.bar(store_df, x="store_location", y="total_revenue", color="store_location",
                 title="Revenue by Store Location", text_auto=".2s")
    fig.update_layout(height=400)
    return fig, store_df

def size_performance(df):
    if "size" not in df.columns:
        return None, None
    size_df = df.groupby("size").agg(total_revenue=("Revenue","sum"), total_units=("transaction_qty","sum")).reset_index()
    fig = px.bar(size_df, x="size", y="total_units", color="size", title="Performance by Size")
    return fig, size_df
