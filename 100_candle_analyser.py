import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import telebot
from selenium.common.exceptions import TimeoutException  # Add this import
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from datetime import date
import requests
 
# Returns the current local date
today = date.today()
def csv_to_pdf(csv_file, pdf_file):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Create a PDF document
    pdf = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []
    
    # Convert DataFrame to a list of lists
    data = [df.columns.to_list()] + df.values.tolist()
    
    # Create a table with the data
    table = Table(data)
    
    # Add style to the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    
    table.setStyle(style)
    
    # Add the table to the elements list
    elements.append(table)
    
    # Build the PDF
    pdf.build(elements)

    return pdf_file



bot1 = telebot.TeleBot(API_KEY, parse_mode=None)


# Set up the Selenium WebDriver (you may need to specify the path to your WebDriver)
driver = webdriver.Chrome()

# List of stock symbols and names (replace this with the actual list you have)
stocks = ['aclbsl', 'adbl', 'ahl', 'ahpc', 'akjcl', 'akpl', 'albsl', 'alicl', 'anlb', 'api', 'avyan', 'barun', 'bbc', 'bedc', 'bfc', 'bgwt', 'bhdc', 'bhl', 'bhpl', 'bnhc', 'bnl', 'bnt', 'bpcl', 'cbbl', 'cfcl', 'cgh', 'chcl', 'chdc', 'chl', 'cit', 'city', 'ckhl', 'cli', 'corbl', 'cycl', 'czbil', 'ddbl', 'dhpl', 'dlbs', 'dolti', 'dordi', 'ebl', 'edbl', 'ehpl', 'enl', 'fmdbl', 'fowad', 'gbbl', 'gbime', 'gblbs', 'gcil', 'gfcl', 'ghl', 'gilb', 'glbsl', 'glh', 'gmfbs', 'gmfil', 'grdbl', 'gufl', 'gvl', 'hathy', 'hbl', 'hdhpc', 'hdl', 'hei', 'hhl', 'hidcl', 'hlbsl', 'hli', 'hppl', 'hrl', 'hurja', 'icfc', 'igi', 'ihl', 'ilbs', 'ili', 'jalpa', 'jbbl', 'jblb', 'jfl', 'joshi', 'jslbb', 'kbl', 'kbsh', 'kdl', 'kkhc', 'klbsl', 'kmcdb', 'kpcl', 'krbl', 'ksbbl', 'lbbl', 'lec', 'licn', 'llbs', 'lsl', 'luk', 'makar', 'mandu', 'mbjc', 'mbl', 'mchl', 'mdb', 'mehl', 'mel', 'men', 'mero', 'mfil', 'mhcl', 'mhl', 'mhnl', 'mkcl', 'mkhc', 'mkhl', 'mkjc', 'mklb', 'mlbbl', 'mlbl', 'mlbs', 'mlbsl', 'mmkjl', 'mnbbl', 'mpfl', 'mshl', 'mslb', 'nabbc', 'nabil', 'nadep', 'nbl', 'nesdo', 'nfs', 'ngpl', 'nhdl', 'nhpc', 'nica', 'nicl', 'niclbsl', 'nifra', 'nil', 'nimb', 'nlg', 'nlic', 'nlicl', 'nmb', 'nmbmf', 'nmfbs', 'nmlbbl', 'nric', 'nrm', 'nrn', 'ntc', 'nubl', 'nyadi', 'ohl', 'pcbl', 'pfl', 'phcl', 'pmhpl', 'pmli', 'ppcl', 'ppl', 'prin', 'profl', 'prvu', 'radhi', 'rawa', 'rbcl', 'rfpl', 'rhgcl', 'rhpl', 'ridi', 'rlfl', 'rnli', 'rsdc', 'ruru', 'sabsl', 'sadbl', 'sahas', 'salico', 'samaj', 'sanima', 'sapdbl', 'sarbtm', 'sbi', 'sbl', 'scb', 'sdlbsl', 'sfcl', 'sghc', 'sgic', 'shel', 'shine', 'shivm', 'shl', 'shlb', 'shpc', 'sicl', 'sifc', 'sigs2', 'sigs3', 'sikles', 'sindu', 'sjcl', 'sjlic', 'skbbl', 'slbbl', 'slbsl', 'smata', 'smb', 'smfbs', 'smh', 'smhl', 'smjc', 'snli', 'sona', 'spc', 'spdl', 'sphl', 'spil', 'spl' , 'srli', 'sshl', 'stc', 'swbbl', 'swmf', 'tamor', 'tpc', 'trh', 'tshl', 'tvcl', 'uail', 'uhewa', 'ulbsl', 'ulhc', 'umhl', 'umrh', 'unhpl', 'unl', 'unlb', 'upcl', 'upper', 'ushec', 'ushl', 'uslb', 'vlbs', 'vlucl', 'wnlb']
# stocks =   ['lec', 'licn', 'llbs', 'lsl', 'luk', 'makar', 'mandu', 'mbjc', 'mbl', 'mchl', 'mdb', 'mehl', 'mel', 'men', 'mero', 'mfil', 'mhcl', 'mhl', 'mhnl', 'mkcl', 'mkhc', 'mkhl', 'mkjc', 'mklb', 'mlbbl', 'mlbl', 'mlbs', 'mlbsl', 'mmkjl', 'mnbbl', 'mpfl', 'mshl', 'mslb', 'nabbc', 'nabil', 'nadep', 'nbl', 'nesdo', 'nfs', 'ngpl', 'nhdl', 'nhpc', 'nica', 'nicl', 'niclbsl', 'nifra', 'nil', 'nimb', 'nlg', 'nlic', 'nlicl', 'nmb', 'nmbmf', 'nmfbs', 'nmlbbl', 'nric', 'nrm', 'nrn', 'ntc', 'nubl', 'nyadi', 'ohl', 'pcbl', 'pfl', 'phcl', 'pmhpl', 'pmli', 'ppcl', 'ppl', 'prin', 'profl', 'prvu', 'radhi', 'rawa', 'rbcl', 'rfpl', 'rhgcl', 'rhpl', 'ridi', 'rlfl', 'rnli', 'rsdc', 'ruru', 'sabsl', 'sadbl', 'sahas', 'salico', 'samaj', 'sanima', 'sapdbl', 'sarbtm', 'sbi', 'sbl', 'scb', 'sdlbsl', 'sfcl', 'sghc', 'sgic', 'shel', 'shine', 'shivm', 'shl', 'shlb', 'shpc', 'sicl', 'sifc', 'sigs2', 'sigs3', 'sikles', 'sindu', 'sjcl', 'sjlic', 'skbbl', 'slbbl', 'slbsl', 'smata', 'smb', 'smfbs', 'smh', 'smhl', 'smjc', 'snli', 'sona', 'spc', 'spdl', 'sphl', 'spil', 'spl' , 'srli', 'sshl', 'stc', 'swbbl', 'swmf', 'tamor', 'tpc', 'trh', 'tshl', 'tvcl', 'uail', 'uhewa', 'ulbsl', 'ulhc', 'umhl', 'umrh', 'unhpl', 'unl', 'unlb', 'upcl', 'upper', 'ushec', 'ushl', 'uslb', 'vlbs', 'vlucl', 'wnlb']



# remove_list = (['adlb', 'ail', 'akbsl', 'amfi', 'bhbl', 'bokl', 'bpw', 'cbl', 'cefl', 'dbbl', 'eblcp', 'eic', 'gdbl', 'gic', 'gimes1', 'glicl', 'hamro', 'hath', 'hgi', 'jbnl', 'jefl', 'jli', 'kadbl', 'kebl', 'klbs', 'kmfl', 'knbl', 'lbl', 'lfc', 'lgil', 'mega', 'mmfdb', 'msmbs', 'nabilp', 'nagro', 'nbb', 'nbbl', 'nccb', 'ncdb', 'nib', 'nidc', 'nlbbl', 'nlo', 'nnlb', 'nslb', 'odbl', 'pic', 'picl', 'plic', 'purbl', 'rbs', 'rli', 'rmdc', 'rrhp', 'rulb', 'sbblj', 'sdesi', 'seos', 'sffil', 'sgi', 'shbl', 'sic', 'sil', 'slbs', 'sli', 'slicl', 'smfdb', 'spars', 'srbl', 'srs', 'syfl', 'tmdbl', 'ufl', 'uic', 'uli'])
# stocks = [i for i in stocks if i not in remove_list]
# stocks = sorted(stocks)

wait_time = 3
# Base URL for the stock detail page
base_url = 'https://merolagani.com/CompanyDetail.aspx?symbol='
# Function to extract table data
def extract_table_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table
    table = soup.find('table', {'class': 'table table-bordered table-striped table-hover'})
    
    # Check if table exists
    if not table:
        print("Table not found")
        return []

    # Initialize a list to store the table data
    data = []

    # Process the table rows
    rows = table.find_all('tr')
    print(len(rows))
    for row in rows:
        cells = row.find_all('td')

        cells_text = []
        for cell in cells:
            entry = cell.get_text(strip=True) 
            if "/" not in entry:
                
                cells_text.append(float(entry.replace(",", "")))
            else:
                cells_text.append((entry))


        data.append(cells_text)

    return data


skipped_list = []
dead_list = []


def readWebpages():
    for symbol in stocks:

        print("Processing", symbol, )

        # Navigate to the stock detail page
        driver.get(base_url + symbol)

        # Wait for the "Price History" tab to load and be clickable
        history_tab_xpath = "//a[@id='ctl00_ContentPlaceHolder1_CompanyDetail1_lnkHistoryTab']"
        try:
            history_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, history_tab_xpath))
            )
        except TimeoutException:
            print(f"Timeout while waiting for history tab for {symbol}")
            continue
        
        # Click on the "Price History" tab
        history_tab.click()
        # print("clicked")
        # print("waiting ", symbol)
        # Wait for the table to be present
        table_xpath = "//table[@class='table table-bordered table-striped table-hover']"
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, table_xpath))
            )
        except TimeoutException:
            print(f"Timeout while waiting for table for {symbol}")
            continue
        print("sleeping ", symbol)

        time.sleep(wait_time)
        # Extract the table data
        html_content = driver.page_source
        table_data = extract_table_data(html_content)

        errorFlag = False
        while not table_data:
            try:
                history_tab.click()
            except Exception as e:
                skipped_list.append(symbol)
                
                bot1.send_message(800851598, "skipping this:"+ str(skipped_list))
                errorFlag  = True
                break


            time.sleep(wait_time)
            # Extract the table data
            html_content = driver.page_source
            table_data = extract_table_data(html_content)

        if errorFlag:
            continue

        if len(table_data)!=101:
            bot1.send_message(800851598, base_url + symbol)
        if len(table_data)<5:
            continue

        # Convert the data to a DataFrame
        df = pd.DataFrame(table_data, columns=[
            '#', 'Date', 'LTP', '% Change', 'High', 'Low', 'Open', 'Qty', 'Turnover'
        ])
        df.to_csv(f'csvs/{symbol}_table_data.csv', index=False)




readWebpages()

# Initialize a list to store data for df2
df2_data = []
days = 30
# Iterate through each stock
for symbol in stocks:
    # Read CSV file
    try:
        df = pd.read_csv(f'csvs/{symbol}_table_data.csv')
        # if  "2024/06/" not in df['Date'].iloc[1]  :
        #     print("df['Date'].iloc[1]", df['Date'].iloc[1])
        #     dead_list.append(symbol)
        avg_volume = df['Qty'][:days].mean()

        # Get the latest day's volume
        latest_volume = df['Qty'].iloc[1]  # Assuming the latest day is the first row
        latest_volume2 = df['Qty'].iloc[2]  # Assuming the latest day is the first row
        latest_volume3 = df['Qty'].iloc[3]  # Assuming the latest day is the first row

        # Calculate volume ratio
        volume_ratio = latest_volume / avg_volume
        volume_ratio2 = latest_volume2 / avg_volume
        volume_ratio3 = latest_volume3 / avg_volume

        # Add data to df2_data
        df2_data.append({
            'Symbol': symbol,
            f'{days}_days_avg_': f'{avg_volume:.2f}',
            'Ratio': f'{volume_ratio:.2f}',
            'Ratio2': f'{volume_ratio2:.2f}',
            'link': "https://nepsealpha.com/trading/chart?symbol="+  symbol.upper(),

        })

    except KeyError as e:
        print(f"KeyError for {symbol}: {e}")
    except Exception as e:
        print(f"An error occurred for {symbol}: {e}")

df2 = pd.DataFrame(df2_data)
df2_sorted = df2.sort_values(by='Ratio', ascending=False)
df2_sorted.to_csv('report_table_data.csv', index=False)

pdf_file = csv_to_pdf('report_table_data.csv', f'report_table_data_{str(today)}.pdf')
# bot1.send_document(800851598, './')

files = {"document": open(pdf_file, 'rb')}
resp = requests.post("https://api.telegram.org/bot" + API_KEY +
                             "/sendDocument?chat_id=" + "800851598",
                             files=files)
print("dead_list", dead_list)

driver.quit()

