# 📥 CSV Sentiment Upload - User Guide

This guide explains how to use the **CSV Sentiment Analyzer** to process sets of text (reviews, tweets, customer feedback) and generate interactive dashboards.

## 🚀 Quick Start
1.  Navigate to **CSV Analyzer** in the left sidebar.
2.  Upload your CSV file (Drag & Drop).
3.  Select the **Text Column** that contains the content you want analyzed.
4.  Choose your **Sentiment Model** (Accurate vs. Fast).
5.  Click **Start Analysis**.

---

## 📋 CSV Requirements
To ensure the best results, your CSV file should follow these simple rules:

| Requirement | Details |
| :--- | :--- |
| **File Format** | Standard `.csv` files only. |
| **Encoding** | **UTF-8** is highly recommended to handle emojis and special characters. |
| **Size Limit** | Up to **200MB** via the dashboard. |
| **Columns** | Must contain at least one column with text. Other columns (Date, Location, User) are optional but help with visualizations. |

---

## 🧠 Model Selection: Accurate vs. Fast

### 🎯 Accurate Mode (Recommended)
*   **Technology:** BERT Ensemble (Deep Learning).
*   **Best for:** High-accuracy business decisions, understanding sarcasm, and complex sentences.
*   **Wait time:** ~1-2 minutes per 1000 rows.

### ⚡ Fast Mode
*   **Technology:** TextBlob (Rule-based).
*   **Best for:** Massive datasets where "direction" is more important than precision.
*   **Wait time:** Instant.

---

## 📊 Understanding the Results

### Visual Analytics
Once processing is complete, you can switch to the **CSV Dashboard** to see:
*   **Sentiment Distribution:** A breakdown of how your audience feels.
*   **Trend Over Time:** (Requires a Date column) See spikes in sentiment.
*   **Segment Breakdown:** (Requires a Category column) Compare sentiment across different product lines or regions.

### Word Clouds
The word cloud identifies the most common keywords present in your text. Larger words represent higher frequency.

### Exports
*   **Analyzed CSV:** Download the original data with 4 new columns: `sentiment_label`, `sentiment_polarity`, `sentiment_confidence`, and `sentiment_model`.

---

## ❓ Troubleshooting

### Connection Error during Upload
*   **Reason:** The file might exceed the 200MB limit or your network connection timed out.
*   **Fix:** Try splitting the CSV into smaller chunks or ensure you are using a stable connection.

### No Dates in Trend Chart
*   **Reason:** The system couldn't reliably detect a date format in your columns.
*   **Fix:** Ensure your date column is formatted as `YYYY-MM-DD` and select it in the sidebar on the dashboard page.

### Empty Word Cloud
*   **Reason:** Your text column might contain mostly numbers or very short words that the filter ignores (stop-words).

---

## 🛠️ Developer Integration
For advanced users, you can also trigger this via the API:
```bash
curl -X POST "http://localhost:8000/api/v1/csv/upload" \
     -H "X-API-Key: YOUR_KEY" \
     -F "file=@my_data.csv" \
     -F "text_column=content"
```
