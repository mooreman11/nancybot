import datetime

from celery import shared_task

from tradetracking.models import Filing, Trade
from tradetracking.scraper import CongressionalData, CongresspersonTracking
from tradetracking.serializers import TradeSerializer


@shared_task
def update_congressional_data():
    year = datetime.datetime.now().year
    method = CongressionalData()
    path = method.request_file(year)
    normalized_data = method.parse_xml(path)
    method.send_congressional_data_to_db(normalized_data)
    filings = Filing.objects.filter(FilingType='P')
    method = CongresspersonTracking()
    for filing in filings:
        filing = filing.objects.filter(DocID=filing.DocID)
        if not filing:
            filing_text = method.get_filing(filing.DocID, filing.Year)
            extracted_data = method.extract_filing_data(filing_text)
            serializer = TradeSerializer(extracted_data, many=True)
            if serializer.is_valid():
                serializer.save()


@shared_task
def get_congressman_data(first, last, active_positions=True, history=False):
    filings = Filing.objects.filter(First__iexact=first, Last__iexact=last, FilingType='P')
    if active_positions is True:
        positions = {}
        for filing in filings:
            trades = Trade.objects.filter(DocID=filing.DocID)
            for trade in trades:
                share_qty = 0
                calls_qty = 0
                puts_qty = 0
                invested = positions.get(trade.Ticker)
                if trade.Transaction == 'S' and invested:
                    share_qty -= trade.Quantity
                elif trade.Transaction == 'P':
                    share_qty += trade.Quantity
                elif trade.Transaction == 'Sc' and invested:
                    calls_qty -= trade.Quantity
                elif trade.Transaction == 'Pc':
                    calls_qty += trade.Quantity
                elif trade.Transaction == 'Sp' and invested:
                    puts_qty -= trade.Quantity
                elif trade.Transaction == 'Pp':
                    puts_qty += trade.Quantity
                if invested:
                    positions[trade.Ticker] = {
                        'share_qty': share_qty if positions[trade.Ticker]['share_qty'] + share_qty >= 0 else 0,
                        'calls_qty': share_qty if positions[trade.Ticker]['calls_qty'] + share_qty >= 0 else 0,
                        'puts_qty': share_qty if positions[trade.Ticker]['puts_qty'] + share_qty >= 0 else 0,
                    }
                else:
                    positions[trade.Ticker] = {
                        'share_qty': share_qty if share_qty >= 0 else 0,
                        'calls_qty': calls_qty if calls_qty >= 0 else 0,
                        'puts_qty': puts_qty if puts_qty >= 0 else 0,
                    }
        return active_positions
    else:
        trades = []
        for filing in filings:
            trades += Trade.objects.filter(DocID=filing.DocID)
        return trades
