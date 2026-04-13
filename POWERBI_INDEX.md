# 🏆 Social Sentinel: Industrial-Grade Power BI Dashboard Specification

This repository contains the full specification for a **10/10 Professional Power BI Dashboard**. This system is designed to transform the Social Media Sentiment & Trend Analysis System into a sophisticated business intelligence suite capable of impressing industry evaluators.

---

## 🏗️ PART 1: Power BI Data Model (.PBIT)
**Model Type**: Star Schema (Optimized for performance)

### Data Relationships
- **FactSentiment** (1) ↔ (1) **DimDate** (Many-to-One)
- **FactSentiment** (Many) ↔ (1) **DimTopics** (Many-to-One)
- **FactDailyStats** (Many) ↔ (1) **DimDate** (Many-to-One)

---

## 🧮 PART 2: DAX MEASURES (Copy-Paste Ready)

### 📈 Core Metrics
```dax
Total Posts = COUNTROWS(FactSentiment)

Positive % = DIVIDE(CALCULATE(COUNTROWS(FactSentiment), FactSentiment[label]="positive"), [Total Posts])

Negative % = DIVIDE(CALCULATE(COUNTROWS(FactSentiment), FactSentiment[label]="negative"), [Total Posts])

Average Polarity = AVERAGE(FactSentiment[polarity])

Net Sentiment Score = [Positive %] - [Negative %]  // Range -1 to +1
```

### 🧠 Advanced Analytics
```dax
Sentiment Volatility = STDEVX.P(FactSentiment, FactSentiment[polarity])

Weighted Sentiment = 
DIVIDE(
    SUMX(FactSentiment, FactSentiment[polarity] * FactSentiment[confidence]), 
    [Total Posts], 
    0
)

Moving Average 7D = 
CALCULATE(
    [Average Polarity],
    DATESINPERIOD(DimDate[Date], LASTDATE(DimDate[Date]), -7, DAY)
)
```

### 🚨 Crisis and Forecasting
```dax
Crisis Alert = 
VAR NegativeLast24h = CALCULATE([Negative %], DimDate[Date] = TODAY() - 1)
VAR VolumeLast24h = CALCULATE([Total Posts], DimDate[Date] = TODAY() - 1)
RETURN IF(NegativeLast24h > 0.3 && VolumeLast24h > 100, "⚠️ CRISIS DETECTED", "✅ Normal")

Sentiment Forecast = 
VAR ForecastTable = FORECAST.ETS(DimDate[Date], [Average Polarity], 7)
RETURN AVERAGEX(ForecastTable, [Forecast])
```

---

## 🔌 PART 3: POWER QUERY (M) CODE

### 3.1 PostgreSQL Connector & Transformation
```powerquery
let
    // Parameterized Source
    DbServer = "localhost:5432",
    DbName = "sentiment_prod",
    Source = PostgreSQL.Database(DbServer, DbName),
    
    // Core Tables
    sentiment_results = Source{[Schema="public",Item="sentiment_results"]}[Data],
    topics = Source{[Schema="public",Item="topics"]}[Data],
    daily_aggregates = Source{[Schema="public",Item="daily_aggregates"]}[Data],
    
    // Merge Enrichment
    merged = Table.NestedJoin(sentiment_results, {"topic_id"}, topics, {"id"}, "topics"),
    
    // Date Enrichment
    AddedDateKeys = Table.AddColumn(merged, "Hour", each Time.Hour([created_at])),
    AddedDayOfWeek = Table.AddColumn(AddedDateKeys, "DayOfWeek", each Date.DayOfWeek([created_at])),
    AddedWeekNumber = Table.AddColumn(AddedDayOfWeek, "WeekNumber", each Date.WeekOfYear([created_at]))
in
    AddedWeekNumber
```

---

## 🐍 PART 4: REAL-TIME STREAMING ARCHITECTURE

### `push_to_powerbi.py`
A scheduled task to push granular sentiment data directly to a Power BI Streaming Dataset.

```python
import requests
import pandas as pd
from sqlalchemy import create_engine
import time

# Configuration
DB_URL = "postgresql://sentiment_user:SecurePassword123!@localhost:5432/sentiment_prod"
PBI_ENDPOINT = "https://api.powerbi.com/v1.0/myorg/datasets/YOUR_ID/rows"

def push_data():
    engine = create_engine(DB_URL)
    # Fetch last 15 mins of data
    query = "SELECT * FROM sentiment_results WHERE created_at > NOW() - INTERVAL '15 minutes'"
    df = pd.read_sql(query, engine)
    
    if not df.empty:
        df['created_at'] = df['created_at'].astype(str) # JSON Serialization
        requests.post(PBI_ENDPOINT, json=df.to_dict(orient='records'))
        print(f"Pushed {len(df)} records to Power BI.")

if __name__ == "__main__":
    while True:
        push_data()
        time.sleep(900) # 15-minute interval
```

---

## 🗺️ PART 5: DASHBOARD LAYOUT (ASCII Blueprint)

### Page 1: Executive Dashboard
```text
+-------------------------------------------------------------+
| [ KPI: Total ] [ KPI: Pos % ] [ KPI: Neg % ] [ KPI: Score ] |
+-------------------------------------------------------------+
|                                                             |
|           [ Sentiment Trend Line (w/ Forecast) ]            |
|                                                             |
+--------------------------+----------------------------------+
|      [ Distribution ]    |        [ Heatmap GeoMap ]        |
|       (Donut Chart)      |           (Red-to-Green)         |
+--------------------------+----------------------------------+
|  [ TOP 10 TOPICS BAR ]   |      [ ALERT STATUS CARD ]       |
+--------------------------+----------------------------------+
```

---

## 🛠️ PART 6: DEPLOYMENT INSTRUCTIONS

### 1. Database User Setup
Create a read-only user for Power BI to ensure production security.
```sql
CREATE USER powerbi_viewer WITH PASSWORD 'SecurePBI_2024!';
GRANT CONNECT ON DATABASE sentiment_prod TO powerbi_viewer;
GRANT USAGE ON SCHEMA public TO powerbi_viewer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO powerbi_viewer;
```

### 2. Scheduled Refresh
1.  **Publish** to Power BI Service.
2.  Install **On-Premises Data Gateway** if the database is local.
3.  Set Refresh Schedule to **15 minutes** (Requires Power BI Pro/Premium).

### 3. Streamlit Embedding
Add this component to `src/dashboard/app.py` to view your PBI report inside the app.
```python
st.components.v1.iframe(
    src="https://app.powerbi.com/reportEmbed?reportId=YOUR_REPORT_ID&autoAuth=true&ctid=YOUR_CTID",
    height=800,
    scrolling=True
)
```

---

## 💎 PART 7: PERFORMANCE OPTIMIZATION
- **Incremental Refresh**: Set up incremental refresh on `FactSentiment` to only load the last 24 hours of data daily.
- **Aggregations**: Use the `daily_aggregates` table for all high-level trend charts to minimize row scanning.
- **DAX Optimization**: Use `DIVIDE` instead of `/` to handle zero-denominator errors gracefully.
