# Stock Market Analysis Tool

This repository contains a **Streamlit** web application for interactive stock market analysis.

The app lets you:

- Compare **2–10 stocks** over a chosen date range.
- View price data in **tabs or side-by-side columns**.
- Plot **line, bar, or area charts** of closing prices.
- See a **combined performance chart** for all selected tickers.
- Generate an **AI-written comparative performance report** using OpenAI (GPT-3.5-Turbo).
- Export a **PDF report** containing the AI summary and the generated charts.

This project was built during the **Workearly AI Programming Summer School**.

## Features

### Data fetching & comparison

- Fetches historical data for each ticker using **[yfinance](https://pypi.org/project/yfinance/)**.
- User controls:
  - Number of stocks to compare (**2–10**).
  - **Start date** and **end date** (must be valid; no future dates).
  - Ticker symbol for each stock (e.g. `AAPL`, `MSFT`, `TSLA`).
- Data is stored in:
  - A per-stock list (`stock_data_list`) with full OHLCV data.
  - A combined `DataFrame` (`combined_data`) containing only the **Close** prices for all stocks.

### Layout modes

You can choose how to display each stock:

- **Tabs mode**
  - Each stock appears in its own tab.
  - Inside each tab you see:
    - The raw `DataFrame` from yfinance.
    - A selectable chart type (**Line / Bar / Area**) for the Close price.

- **Columns mode**
  - Each stock is rendered in its own column.
  - Same data and chart options as tabs, but displayed side-by-side.

### Charts

For each stock:

- You can choose **one chart type**:
  - **Line chart** (`st.line_chart`)
  - **Bar chart** (`st.bar_chart`)
  - **Area chart** (`st.area_chart`)
- When you choose a **line chart** for a stock, the app also creates a **Matplotlib** line chart and saves it as `chart_<index>.png` so it can be embedded later in the PDF report.

For all stocks together:

- The app builds a `combined_data` DataFrame with Close prices for each ticker.
- You can display a **combined Line/Bar/Area chart**:
  - If you choose **Line**, a Matplotlib version of the combined line chart is also saved for the PDF.

### AI-generated comparative performance report

When you click the **“Comparative Performance”** button:

1. The app builds a detailed **system prompt** explaining that the model is a strict financial assistant.
2. It builds a **user message** that contains the full price tables for each selected stock (as text).
3. It calls the OpenAI Chat Completions API:

   - **Client:** `OpenAI` (from `openai` package)  
   - **Model:** `gpt-3.5-turbo`

4. The AI response is shown in the Streamlit app using `st.write`.

The prompt instructs the model to:

- Summarize the **comparative performance** of the stocks.
- Highlight **advantages and disadvantages** of each over the selected period.
- Provide a **conclusion** in **Markdown-style** output.

### PDF report export

After generating the AI summary, the app:

1. Creates a PDF in memory using **reportlab**.
2. Adds:
   - A title: _“Stock Market Analysis Tool”_.
   - The generated text, parsed line-by-line:
     - Lines starting with `###` → main headings.
     - Lines starting with `####` → sub-headings.
     - Lines starting with `-` → bullet points.
     - Everything else → body text.
3. Adds all previously generated **line chart images** (`chart_*.png`) to the PDF.
4. Exposes a **“Download PDF”** button so the user can save:

   ```text
   stock_analysis_report_YYYYMMDDHHMMSS.pdf
