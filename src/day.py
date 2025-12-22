#!/usr/bin/env python3

import argparse
import sys
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

URL = 'https://finance.naver.com/item/sise_day.nhn'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4501.0 Safari/537.36'
}

def parse(bs):
    values = [span.text.strip().replace(',', '').replace('.', '-') for span in bs.find_all('span', class_='tah')]
    # 7 fields: date, close, delta, open, high, low, volume
    for i in range(0, len(values), 7):
        row = values[i:i+7]
        if len(row) == 7:
            yield {
                'date': row[0],
                'close': row[1],
                'delta': row[2],
                'open': row[3],
                'high': row[4],
                'low': row[5],
                'volume': row[6]
            }

async def fetch_symbol(session, symbol, date, semaphore):
    async with semaphore:
        try:
            params = {'code': symbol, 'page': 1}
            async with session.get(URL, params=params, headers=HEADERS, timeout=10) as response:
                if response.status != 200:
                    return None
                content = await response.read()
                bs = BeautifulSoup(content, 'lxml')

                for row in parse(bs):
                    if row['date'] == date and row['open'] != '0':
                        return '\t'.join([symbol, row['open'], row['high'], row['low'], row['close'], row['volume']])
                
                return None
        except Exception:
            return None

async def main_async(date, symbols, concurrency):
    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)
    semaphore = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_symbol(session, symbol, date, semaphore) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        for res in results:
            if res:
                print(res)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date', default=datetime.now().strftime('%Y-%m-%d'), help='format: YYYY-MM-DD')
    parser.add_argument('-c', '--concurrency', type=int, default=50, help='Max concurrent requests')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', type=argparse.FileType('r'), help='symbol file')
    group.add_argument('-s', '--symbol')
    args = parser.parse_args()

    symbols = [args.symbol] if args.symbol else [line.strip() for line in args.file if line.strip()]
    
    asyncio.run(main_async(args.date, symbols, args.concurrency))
