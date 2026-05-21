# How to Use the Data Explorer

The **Data Explorer** is the primary search engine for finding data fields on WorldQuant BRAIN. Since unique and high-quality data is the raw material of quantitative research, mastering the Data Explorer is crucial to finding predictive signals.

---

## 1. Finding High-Quality Fields

When searching for data, look for these three key indicators:
*   **Coverage ($\ge 75\%$)**: The percentage of stocks in your target universe (e.g. `TOP3000`) that have valid data for this field. Lower coverage fields ($<30\%$) lead to concentrated portfolios that fail weight compliance checks.
*   **History Length ($\ge 10$ Years)**: The longer the data history, the more robust and reliable your historical simulation backtests will be.
*   **Region Matching**: Make sure the field is active in your target region. If you are simulating in the `USA` region, check that the field supports US assets.

---

## 2. Searching and Filtering Tips

Use these techniques to navigate the massive database of fields:

### A. Use Descriptive Tags
*   Filter by broad data categories like **Fundamentals** (`#fundamental`), **Prices** (`#price`), **Alternative** (`#alternative`), or **Analyst Estimates** (`#estimates`).
*   Click the **Alpha Generation** tag (`#alpha`) to filter specifically for fields that have historically shown the highest predictive signal in WorldQuant's research.

### B. Search for Complementary Fields
*   Instead of looking at isolated price signals, search for fields that can be combined.
*   *Example*: Combine a fundamental earnings field (`ebitda`) with a market capitalization field (`enterprise_value`) to build a normalized valuation ratio: `enterprise_value / ebitda`.

### C. Check Point-in-Time Delay Labels
*   Check when the data is released to the public. For quarterly fundamental fields, look at the release lag (e.g., $15$ or $45$ days after quarter end). Ensure your alpha's `delay` parameter is set to `1` so the simulator does not trade on earnings before they are officially published.
