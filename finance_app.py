from datetime import datetime
from openai import OpenAI
import streamlit as st
import yfinance as yf
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import matplotlib.pyplot as plt

client = OpenAI(api_key=st.secrets["OpenAI_key"])

# Set page layout to wide
st.set_page_config(layout="wide")

st.title('Stock Market Analysis Tool')

# Function to fetch stock data
def get_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# Sidebar for user inputs
st.sidebar.header('User Input Options')

# Input for number of stocks to compare
num_stocks = st.sidebar.number_input('Number of Stocks to Compare', min_value=2, max_value=10, value=2, step=1)

# Option to switch between tabs or columns
display_mode = st.sidebar.radio("Display Mode", ("Tabs", "Columns"))

# Date input for start and end date
start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.today().date())

# Validate the date range
if start_date >= end_date:
    st.sidebar.error('Error: End date must fall after start date.')
elif end_date > datetime.today().date():
    st.sidebar.error('Error: We can\'t predict the future yet. :)')

# Lists to hold stock tickers and data
selected_stocks = []
stock_data_list = []
combined_data = pd.DataFrame()
chart_images = []

# Function to create and save line charts with matplotlib
def save_line_chart(data, ticker, chart_number):
    fig, ax = plt.subplots()
    ax.plot(data.index, data)
    ax.set_title(f'{ticker} - Line Chart')
    ax.set_xlabel('Date')
    ax.set_ylabel('Close Price')

    chart_filename = f'chart_{chart_number}.png'
    plt.savefig(chart_filename)
    plt.close()
    chart_images.append(chart_filename)

# Loop to get inputs for each stock
for i in range(num_stocks):
    ticker = st.sidebar.text_input(f'Enter Stock Ticker {i+1}', 'AAPL').upper()
    selected_stocks.append(ticker)
    if start_date < end_date:
        stock_data = get_stock_data(ticker, start_date, end_date)
        stock_data_list.append(stock_data)
        combined_data[ticker] = stock_data['Close']

# Display stocks either in tabs or columns based on user choice
if display_mode == "Tabs":
    tabs = st.tabs([f'Stock {i+1}: {ticker}' for i, ticker in enumerate(selected_stocks)])
    for i, tab in enumerate(tabs):
        with tab:
            st.subheader(f"Displaying data for: {selected_stocks[i]}")
            if start_date < end_date:
                st.write(stock_data_list[i])
                chart_type = st.selectbox(f'Select Chart Type for {selected_stocks[i]}', ['Line', 'Bar', 'Area'], key=f'chart_{i}')
                if chart_type == 'Line':
                    st.line_chart(stock_data_list[i]['Close'])
                elif chart_type == 'Bar':
                    st.bar_chart(stock_data_list[i]['Close'])
                elif chart_type == 'Area':
                    st.area_chart(stock_data_list[i]['Close'])
                # Generate line chart for PDF
                if chart_type == 'Line':
                    save_line_chart(stock_data_list[i], selected_stocks[i], i)
else:
    cols = st.columns(num_stocks)
    for i, col in enumerate(cols):
        with col:
            st.subheader(f"Displaying data for: {selected_stocks[i]}")
            if start_date < end_date:
                st.write(stock_data_list[i])
                chart_type = st.selectbox(f'Select Chart Type for {selected_stocks[i]}', ['Line', 'Bar', 'Area'], key=f'chart_{i}')
                if chart_type == 'Line':
                    st.line_chart(stock_data_list[i]['Close'])
                elif chart_type == 'Bar':
                    st.bar_chart(stock_data_list[i]['Close'])
                elif chart_type == 'Area':
                    st.area_chart(stock_data_list[i]['Close'])
                # Generate line chart for PDF
                if chart_type == 'Line':
                    save_line_chart(stock_data_list[i], selected_stocks[i], i)

# Combined line chart for all selected stocks
if not combined_data.empty:
    st.subheader('Combined Stock Performance')
    chart_type2 = st.selectbox(f'Select Chart Type for combined stocks', ['Line', 'Bar', 'Area'], key=f'chart_{combined_data}')
    if chart_type2 == 'Line':
        st.line_chart(combined_data)
        # Generate line chart for PDF
        save_line_chart(combined_data, 'Combined', 'combined')
    elif chart_type2 == 'Bar':
        st.bar_chart(combined_data)
    elif chart_type2 == 'Area':
        st.area_chart(combined_data)

if st.button('Comparative Performance'):
    system_message = "You are a financial assistant that will retrieve a number of tables of financial market data and will summarize the comparative performance in text, in full detail with highlights for each stock, mention their advantages and disadvantages for this period and also have a conclusion with a markdown output. BE VERY STRICT ON YOUR OUTPUT"
    user_message = "This is the stock data:"
    for i, ticker in enumerate(selected_stocks):
        user_message += f"\n\nStock {i+1} ({ticker}):\n{stock_data_list[i]}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )
    generated_text = response.choices[0].message.content
    st.write(generated_text)

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    custom_styles = {
        'Title': styles['Title'],
        'Heading1': styles['Heading1'],
        'Heading2': ParagraphStyle(name='Heading2', fontSize=14, spaceAfter=12, fontName='Helvetica-Bold'),
        'BodyText': ParagraphStyle(name='BodyText', fontSize=12, fontName='Helvetica'),
        'Bullet': ParagraphStyle(name='Bullet', fontSize=12, fontName='Helvetica', bulletFontName='Helvetica', bulletFontSize=12, leftIndent=20, spaceBefore=6),
    }
    
    flowables = []

    # Add title
    flowables.append(Paragraph("Stock Market Analysis Tool", custom_styles['Title']))
    flowables.append(Spacer(1, 12))

    # Add generated text with custom formatting
    paragraphs = generated_text.split('\n')
    for paragraph in paragraphs:
        if paragraph.startswith('###'):
            flowables.append(Paragraph(paragraph[3:].strip(), custom_styles['Heading1']))
        elif paragraph.startswith('####'):
            flowables.append(Paragraph(paragraph[4:].strip(), custom_styles['Heading2']))
        elif paragraph.startswith('-'):
            flowables.append(Paragraph(f"• {paragraph[1:].strip()}", custom_styles['Bullet']))
        else:
            flowables.append(Paragraph(paragraph, custom_styles['BodyText']))
    
    flowables.append(Spacer(1, 12))

    # Add line charts to the PDF
    for chart in chart_images:
        flowables.append(Image(chart, width=400, height=300))
        flowables.append(Spacer(1, 12))

    doc.build(flowables)
    pdf_buffer.seek(0)

    # Download the PDF
    st.download_button(
        label="Download PDF",
        data=pdf_buffer,
        file_name=f"stock_analysis_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf",
        mime="application/pdf",
    )
