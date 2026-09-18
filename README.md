# ☕ Afficionado Coffee Roasters - Product Optimization & Revenue Contribution Analysis
### Unified Mentor Data Analyst Fellowship | Retail Analytics Driven Business Project

## Project Overview
A full end-to-end retail intelligence project analyzing **149,116 transaction line items** from Jan-Jun 2025 across 3 NYC locations (Lower Manhattan, Hell's Kitchen, Astoria) to answer: **What drives revenue?**

While transaction-level data existed, decisions were intuition-driven:
- No visibility into popularity vs profitability
- No category dependency insights
- No identification of low-impact menu items

This project delivers product-centric intelligence to support menu optimization and merchandising strategy.

## Dataset
**Source:** [Google Sheet - Afficionado Coffee Roasters](https://docs.google.com/spreadsheets/d/14CqwUgV3M37tz0ymk_utin29aDAKtdJA/edit?usp=sharing&ouid=109542648602084306654&rtpof=true&sd=true)

| Column | Description |
|---|---|
| transaction_id | Unique identifier per transaction |
| year | 2025 |
| transaction_time | HH:MM:SS |
| transaction_qty | Quantity purchased |
| unit_price | Price per unit |
| store_id | Store identifier (5,8,3) |
| store_location | Lower Manhattan, Hell's Kitchen, Astoria |
| Balance | Account balance |
| product_id | 1-80 unique |
| product_category | 9 categories |
| product_type | Variant within category |
| product_detail | Flavor/blend/size |

**Derived:** `Revenue = transaction_qty × unit_price`

**Size:** 149,116 rows, 80 unique products, 0 missing values

## Key KPIs & Findings (from full analysis)
| KPI | Value |
|---|---|
| Total Revenue | $698,812.33 |
| Total Units Sold | 214,470 |
| Total Transactions | 149,116 |
| Avg Revenue / Transaction | $4.69 |
| Unique Products | 80 |
| Top Category | Coffee 38.63% |
| Coffee + Tea | 66.74% of revenue |
| Products for 80% revenue | 42 (52.5% of menu) |
| Long-tail | 38 products = 20% revenue |
| True Hero Product | Dark Chocolate Lg - Hero Score 69.5 |

**Category Breakdown:**
- Coffee: $269,952 (38.63%)
- Tea: $196,405 (28.11%)
- Bakery: $82,315 (11.78%)
- Drinking Chocolate: $72,416 (10.36%)
- Coffee Beans: $40,085 (5.74%)
- Branded: $13,607 (1.95%)
- Loose Tea: $11,213 (1.60%)
- Flavours: $8,408 (1.20%)
- Packaged Chocolate: $4,407 (0.63%)

## Methodology
1. **Ingestion & Validation:** Load Excel, check missing (0), validate qty >0, price $0.80-$45
2. **Revenue Computation:** Transaction level, then aggregated by product/type/category
3. **Popularity Analysis:** Units sold per product, ranking, top/bottom performers
4. **Revenue Contribution:** Revenue per product, share %, comparison volume rank vs revenue rank
5. **Category & Type Performance:** Share by category, product-type within category, dependence
6. **Pareto Analysis:** Cumulative revenue, identify anchors vs long-tail, concentration ratio
7. **Hero Score:** Normalized composite: 0.4*Revenue + 0.4*Volume + 0.2*Efficiency (Revenue per unit)

## Project Structure
```
Afficionado_Project/
├── data/
│   ├── Afficionado_Coffee_Roasters_Full_149k.csv (generated synthetic approximating real)
│   ├── product_catalog.csv
│   └── sample_1000.csv
├── src/
│   ├── data_loader.py
│   ├── analysis.py
│   └── visualizations.py
├── app/
│   └── streamlit_app.py
├── reports/
│   ├── research_paper.md
│   └── executive_summary.md
├── notebooks/
│   └── EDA.ipynb
├── requirements.txt
└── README.md
```

## How to Run

```bash
# 1. Clone / download folder
cd Afficionado_Project

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place real dataset (if you have it) as data/Afficionado_Coffee_Roasters.xlsx
# Or use the generated synthetic CSV which already matches structure

# 4. Run Streamlit dashboard
streamlit run app/streamlit_app.py
```

Dashboard will open at http://localhost:8501

## Dashboard Features
- **KPI Cards:** Total revenue, units, transactions, unique products, top category, concentration
- **Top-N Slider:** Adjustable (5-30) for product ranking
- **Category Donut:** Revenue share by category
- **Pareto Chart:** With 80% threshold and anchor count
- **Volume vs Revenue Scatter:** Size = revenue share, color = category
- **Filters:** Category, product_type, store_location
- **Hero Products Table:** Composite scoring
- **Drill-down Table:** Full performance with download CSV

## Business Recommendations
**Immediate:**
- Promote Heroes: Dark Chocolate Lg, Sustainably Grown Organic Lg, Latte Rg
- Review Bottom 10: Dark Chocolate (no size), Spicy Eye Opener Chai, Guatemalan Sustainably Grown - consider removing or repricing
- Push Large sizes: Lg/Rg dominate - default upsell, menu highlighting
- Add Chocolate Variety: Only 1 type (Hot Chocolate) - introduce white chocolate, salted caramel

**Strategic:**
- Protect Coffee & Tea: 66.74% revenue - maintain quality, supplier redundancy
- Simplify Menu: 80 items too many - target 60 by removing long-tail
- Price Optimization: Earl Grey Rg high volume low revenue - test +$0.30 increase
- Barista Espresso Focus: 33.86% of coffee revenue - staff training, latte art, signature drinks

## Deliverables
- ✅ Streamlit Dashboard (this app)
- ✅ Research Paper (reports/research_paper.md)
- ✅ Executive Summary (reports/executive_summary.md)
- ✅ EDA Notebook

## Tech Stack
Python, Pandas, NumPy, Plotly, Streamlit, Matplotlib, Seaborn

---
*Prepared for Afficionado Coffee Roasters - Menu Optimization Project*
