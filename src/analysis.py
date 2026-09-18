"""
Product Optimization & Revenue Contribution Analysis
Core analytical functions
"""
import pandas as pd
import numpy as np

def product_popularity(df: pd.DataFrame) -> pd.DataFrame:
    """Total units sold per product, ranked."""
    agg = df.groupby(["product_id", "product_category", "product_type", "product_detail", "unit_price"]).agg(
        total_units=("transaction_qty", "sum"),
        total_transactions=("transaction_id", "count"),
        total_revenue=("Revenue", "sum")
    ).reset_index()
    agg = agg.sort_values("total_units", ascending=False)
    agg["volume_rank"] = agg["total_units"].rank(ascending=False, method="dense").astype(int)
    return agg

def revenue_contribution(df: pd.DataFrame, product_agg: pd.DataFrame = None) -> pd.DataFrame:
    """Total revenue per product + share % and efficiency."""
    if product_agg is None:
        product_agg = product_popularity(df)
    
    total_rev = product_agg["total_revenue"].sum()
    product_agg["revenue_share_pct"] = (product_agg["total_revenue"] / total_rev * 100).round(2)
    product_agg["revenue_rank"] = product_agg["total_revenue"].rank(ascending=False, method="dense").astype(int)
    product_agg["efficiency_score"] = (product_agg["total_revenue"] / product_agg["total_units"]).round(2)  # revenue per unit
    product_agg["product_efficiency_score"] = product_agg["total_revenue"] / 1  # per SKU, same as revenue here, but extensible
    
    # Hero Score: normalized composite of volume, revenue, efficiency
    for col in ["total_units", "total_revenue", "efficiency_score"]:
        min_v = product_agg[col].min()
        max_v = product_agg[col].max()
        product_agg[f"{col}_norm"] = (product_agg[col] - min_v) / (max_v - min_v + 1e-9)
    
    product_agg["hero_score"] = (
        0.4 * product_agg["total_revenue_norm"] +
        0.4 * product_agg["total_units_norm"] +
        0.2 * product_agg["efficiency_score_norm"]
    ) * 100
    product_agg["hero_score"] = product_agg["hero_score"].round(1)
    
    return product_agg.sort_values("total_revenue", ascending=False)

def category_performance(df: pd.DataFrame) -> pd.DataFrame:
    cat = df.groupby("product_category").agg(
        total_revenue=("Revenue", "sum"),
        total_units=("transaction_qty", "sum"),
        transactions=("transaction_id", "count"),
        unique_products=("product_id", "nunique")
    ).reset_index()
    total_rev = cat["total_revenue"].sum()
    cat["revenue_share_pct"] = (cat["total_revenue"] / total_rev * 100).round(2)
    return cat.sort_values("total_revenue", ascending=False)

def product_type_performance(df: pd.DataFrame) -> pd.DataFrame:
    pt = df.groupby(["product_category", "product_type"]).agg(
        total_revenue=("Revenue", "sum"),
        total_units=("transaction_qty", "sum"),
        unique_products=("product_id", "nunique")
    ).reset_index()
    # share within category
    cat_totals = df.groupby("product_category")["Revenue"].sum().to_dict()
    pt["share_within_category"] = pt.apply(lambda r: round(r["total_revenue"] / cat_totals[r["product_category"]] * 100, 2), axis=1)
    return pt.sort_values(["product_category", "total_revenue"], ascending=[True, False])

def pareto_analysis(product_agg: pd.DataFrame) -> pd.DataFrame:
    """80/20 analysis."""
    df = product_agg.sort_values("total_revenue", ascending=False).copy()
    df["cumulative_revenue"] = df["total_revenue"].cumsum()
    total = df["total_revenue"].sum()
    df["cumulative_pct"] = (df["cumulative_revenue"] / total * 100).round(2)
    df["is_80_pct"] = df["cumulative_pct"] <= 80
    # Find how many products for 80%
    n_80 = df[df["cumulative_pct"] <= 80].shape[0]
    # Include one more if next crosses 80
    if n_80 < len(df) and df.iloc[n_80]["cumulative_pct"] < 80:
        n_80 += 1
    # Edge: if first already over 80, ensure at least 1
    return df, n_80

def kpi_summary(df: pd.DataFrame, product_agg: pd.DataFrame, category_df: pd.DataFrame, n_80: int) -> dict:
    total_rev = df["Revenue"].sum()
    total_units = df["transaction_qty"].sum()
    total_trans = df["transaction_id"].nunique()
    unique_products = df["product_id"].nunique()
    avg_rev_per_trans = total_rev / total_trans if total_trans else 0
    top_category = category_df.iloc[0]["product_category"] if not category_df.empty else "N/A"
    top_category_share = category_df.iloc[0]["revenue_share_pct"] if not category_df.empty else 0
    
    concentration_ratio = round(n_80 / unique_products * 100, 1) if unique_products else 0
    long_tail_products = unique_products - n_80
    long_tail_revenue_pct = 100 - product_agg.sort_values("total_revenue", ascending=False).iloc[:n_80]["revenue_share_pct"].sum() if n_80 else 100
    
    return {
        "total_revenue": total_rev,
        "total_units": total_units,
        "total_transactions": total_trans,
        "unique_products": unique_products,
        "avg_revenue_per_transaction": avg_rev_per_trans,
        "top_category": top_category,
        "top_category_share": top_category_share,
        "products_for_80_pct": n_80,
        "concentration_ratio": concentration_ratio,
        "long_tail_products": long_tail_products,
        "long_tail_revenue_pct": round(long_tail_revenue_pct, 2)
    }

def volume_vs_revenue_mismatch(product_agg: pd.DataFrame) -> pd.DataFrame:
    """Identify products where volume rank != revenue rank"""
    df = product_agg.copy()
    df["rank_diff"] = df["volume_rank"] - df["revenue_rank"]
    # Positive diff = high volume, low revenue (low price), Negative = high price, low volume
    return df.sort_values("rank_diff", ascending=False)
