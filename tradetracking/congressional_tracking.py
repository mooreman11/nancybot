import datetime
import re

import xmltodict
import requests
import shutil
from PyPDF2 import PdfReader

from tradetracking.models import Filing
from tradetracking.serializers import FilingSerializer

corporation_codings = [
    'Inc.',
    'L.P.',
    'LLC',
    # 'Company',
    # 'Corporation'
]

purchase_whitelist = [
    'P (partial)',
    'P ',
]

sell_whitelist = [
    'S (partial)',
    'S ',
    'Sold',
]

options_whitelist = [
    'options'
]

call_whitelist = [
    'call'
]

put_whitelist = [
    'put'
]


class CongressionalData:
    def __init__(self):
        pass

    def request_file(self, year: int):
        file = f'{year}FD'
        url = f'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.ZIP'
        response = requests.get(url, stream=True)
        if response.status_code >= 400:
            raise Exception
        with open(f'./{file}.zip', "wb") as f:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        shutil.unpack_archive(f'{file}.zip', file)
        return file

    def parse_xml(self, file: str):
        xml_file_path = f'{file}/{file}.xml'
        with open(xml_file_path) as xml_file:
            data_dict = xmltodict.parse(xml_file.read())
            xml_file.close()
            data_dict = data_dict['FinancialDisclosure']['Member']
            for i in range(len(data_dict)):
                Prefix, Last, First, Suffix, FilingType, StateDst, Year, FilingDate, DocID = data_dict[i].values()
                data_dict[i] = {
                    'Prefix': Prefix,
                    'Last': Last,
                    'First': First,
                    'Suffix': Suffix,
                    'FilingType': FilingType,
                    'StateDst': StateDst,
                    'Year': int(Year),
                    'FilingDate': datetime.datetime.strptime(FilingDate, '%m/%d/%Y').date(),
                    'DocID': int(DocID)
                }
        return data_dict

    def send_congressional_data_to_db(self, data: dict):
        # validated_data = []
        # for item in data:
        #     try:
        #         serializer = FilingSerializer(data=item)
        #         if serializer.is_valid(raise_exception=True):
        #             validated_data.append(serializer.data)
        #     except Exception as e:
        #         print(e)
        serializer = FilingSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            return serializer.data
        return serializer.errors


def update_congressional_data():
    year = datetime.datetime.now().year
    method = CongressionalData()
    path = method.request_file(year)
    normalized_data = method.parse_xml(path)
    return method.send_congressional_data_to_db(normalized_data)


class CongresspersonTracking:
    def __init__(self):
        pass

    def check_db(self):
        objects = Filing.objects.filter(First='Nancy', Last='Pelosi')
        return objects

    def get_filing(self, DocID: str, year):
        text = ''
        response = requests.get(f'https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{year}/{DocID}.pdf')
        if response.status_code >= 400:
            raise Exception
        with open(f'filings/{DocID}.pdf', 'wb') as f:
            f.write(response.content)
            f.close()
        reader = PdfReader(f'filings/{DocID}.pdf')
        for page in reader.pages:
            text += page.extract_text()
        return text

    def get_transaction(self, data):
        transaction = ''
        for keyword_list in [purchase_whitelist, sell_whitelist]:
            for keyword in keyword_list:
                if data.find(keyword) > -1:
                    if keyword_list == purchase_whitelist:
                        transaction = 'P'
                    elif keyword_list == sell_whitelist:
                        transaction = 'S'
                    break
            if transaction != '':
                return transaction

    def get_stock(self, ticker: str, data: str, comments) -> dict:
        qty = ''
        transaction = self.get_transaction(data)
        for comment in comments:
            comment = comment[:comment.find('\n')]
            vals = comment.replace(',', '').split()
            for val in vals:
                if val.isnumeric():
                    qty = val
                    break
        trade = {
            'ticker': ticker,
            'transaction': transaction,
            'qty': qty,
        }
        return trade

    def get_option(self, ticker: str, data: str, comments) -> dict:
        qty = ''
        strike_price = 0
        purchase_date = ''
        expiration = ''
        transaction = self.get_transaction(data)
        for comment in comments:
            comment = comment[:comment.find('\n')]
            for keyword_list in [put_whitelist, call_whitelist]:
                for keyword in keyword_list:
                    if comment.find(keyword) > -1:
                        if keyword_list == put_whitelist:
                            transaction += 'p'
                            break
                        elif keyword_list == call_whitelist:
                            transaction += 'c'
                            break
                if len(transaction) == 2:
                    break
            vals = comment.replace(',', '').split()
            for val in vals:
                if val.isnumeric() and qty == 0:
                    qty = val
                if val.find('$') > -1 and strike_price == 0:
                    strike_price = val
                if qty != 0 and strike_price != 0:
                    break
            date_extract_pattern = "[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{2}"
            dates = re.findall(date_extract_pattern, comment)
            if len(dates) == 2:
                purchase_date = dates[0]
                expiration = dates[1]
        trade = {
            'ticker': ticker,
            'transaction': transaction,
            'qty': qty,
            'strike_price': strike_price,
            'purchase_date': purchase_date,
            'expiration': expiration,
        }
        return trade

    def extract_filing_data(self, file: str):
        trades = []
        file_start = file.find('Gains >\n$200?')
        file_end = file.find("For the complete list")
        file = file[file_start + 14:file_end]
        stocks = file.split('SP')  # exclusive to Nancy Pelosi
        for stock in stocks[1:]:
            first_line_end = stock.find('\n')
            start_index = stock.find('(')
            end_index = stock.find(')')
            comments = stock.split(':')
            ticker = stock[start_index + 1:end_index]
            if stock.find('[ST]') > -1:
                trades.append(self.get_stock(ticker, stock, comments))
            elif stock.find('[OP]') > -1:
                trades.append(self.get_option(ticker, stock, comments))
            else:
                print(stock[:first_line_end])
        for trade in trades:
            print(trade)
        return trades


def parse_congressperson():
    filings = []
    method = CongresspersonTracking()
    datasets = method.check_db()
    for dataset in datasets:
        filing_text = method.get_filing(dataset.DocID, dataset.Year)
        extracted_data = method.extract_filing_data(filing_text)
        filings.append(extracted_data)
    return filings
