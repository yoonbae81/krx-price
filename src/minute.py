#!/usr/bin/env python3

import argparse
import sys
import re
import asyncio
import aiohttp
from datetime import datetime
from bs4 import BeautifulSoup

URL = 'https://finance.naver.com/item/sise_time.nhn'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4501.0 Safari/537.36'
}

def parse_rows(symbol, bs):
    # Performance: Avoid partition() if possible, but the structure is fixed
    values = [span.text.strip().replace(',', '') for span in bs.find_all('span', class_='tah')]
    if not values:
        return []
    
    result = []
    # 7 values per row: Time, Price, Chg, Open, High, Low, Vol
    for i in range(0, len(values), 7):
        row = values[i:i+7]
        if len(row) == 7:
            # Result format: [symbol, price, volume, time]
            result.append([symbol, row[1], row[6], row[0]])
    # Return in original order (newest first from page)
    return result

async def fetch_page(session, symbol, date_str, page, semaphore):
    async with semaphore:
        params = {
            'page': page,
            'code': symbol,
            'thistime': date_str.replace('-', '') + '235959'
        }
        try:
            async with session.get(URL, params=params, headers=HEADERS, timeout=10) as response:
                if response.status != 200:
                    return []
                text = await response.read()
                # Use lxml for speed
                bs = BeautifulSoup(text, 'lxml')
                return parse_rows(symbol, bs)
        except Exception:
            return []

async def fetch_symbol(session, symbol, date_str, semaphore):
    # 1. Fetch page 1 and get last page number
    params = {
        'page': 1,
        'code': symbol,
        'thistime': date_str.replace('-', '') + '235959'
    }
    try:
        async with session.get(URL, params=params, headers=HEADERS, timeout=10) as response:
            if response.status != 200:
                return
            text = await response.read()
            bs = BeautifulSoup(text, 'lxml')
            
            # Parse page 1 immediately
            all_results = parse_rows(symbol, bs)
            if not all_results:
                return

            # Determine last page
            pg_rr = bs.find('td', class_='pgRR')
            if pg_rr is None:
                last_page = 1
            else:
                match = re.search(r'page=([0-9]+)', pg_rr.a['href'])
                last_page = int(match.group(1)) if match else 1

            # 2. Fetch remaining pages (2..last_page) concurrently
            if last_page > 1:
                tasks = [fetch_page(session, symbol, date_str, pg, semaphore) for pg in range(2, last_page + 1)]
                other_pages = await asyncio.gather(*tasks)
                for page_results in other_pages:
                    all_results.extend(page_results)

            # 3. Dedup and sort
            # Use a set for dedup (based on time + symbol as unique key)
            unique_data = {}
            for res in all_results:
                # key is time (res[3])
                key = res[3]
                if key not in unique_data:
                    unique_data[key] = res
            
            # Sort by time (res[3]) reverse to match original 'last page to first' intended logic? 
            # Actually, the user's run.sh sorts by time. We'll just print them.
            for key in sorted(unique_data.keys()):
                print('\t'.join(unique_data[key]))
                    
    except Exception as e:
        print(f'[ERROR] Exception for {symbol}: {e}', file=sys.stderr)

async def main_async(date_str, symbols, concurrency):
    # Connector with limit=0 to use semaphore for flow control
    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)
    semaphore = asyncio.Semaphore(concurrency)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Process symbols with some concurrency too, but controlled
        # To avoid creating 2500+ tasks at once, we can chunk symbols
        # OR just use a global semaphore across all requests. 
        # The current fetch_symbol calls fetch_page which uses the same semaphore.
        tasks = [fetch_symbol(session, symbol, date_str, semaphore) for symbol in symbols]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date', default=datetime.now().strftime('%Y-%m-%d'), help='format: YYYY-MM-DD')
    parser.add_argument('-c', '--concurrency', type=int, default=50, help='Max concurrent requests')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', type=argparse.FileType('r'), help='symbol file')
    group.add_argument('-s', '--symbol')
    args = parser.parse_args()

    symbols = [args.symbol] if args.symbol else [line.strip() for line in args.file if line.strip()]
    
    # Use ProactorEventLoop on Windows if needed, but asyncio.run handles it in 3.8+
    asyncio.run(main_async(args.date, symbols, args.concurrency))
