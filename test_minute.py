import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

MINUTE_URL = 'https://finance.naver.com/item/sise_time.nhn'
MINUTE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4501.0 Safari/537.36'
}

def parse_minute_rows(symbol, bs):
    values = [span.text.strip().replace(',', '') for span in bs.find_all('span', class_='tah')]
    print(f"DEBUG: Found {len(values)} values for {symbol}")
    if not values:
        return []
    
    result = []
    for i in range(0, len(values), 7):
        row = values[i:i+7]
        if len(row) == 7:
            result.append([symbol, row[1], row[6], row[0]])
    return result

async def main():
    async with aiohttp.ClientSession() as session:
        symbol = '005930' # Samsung Electronics
        params = {
            'page': 1,
            'code': symbol,
            'thistime': '20251223235959'
        }
        async with session.get(MINUTE_URL, params=params, headers=MINUTE_HEADERS) as response:
            print(f"DEBUG: Status {response.status}")
            print(f"DEBUG: Content-Type {response.headers.get('Content-Type')}")
            content = await response.read()
            # Try to decode with euc-kr
            try:
                text = content.decode('euc-kr')
                print("DEBUG: Decoded with euc-kr successfully")
            except:
                text = content.decode('utf-8', errors='ignore')
                print("DEBUG: Decoded with utf-8 (ignore errors)")
            
            bs = BeautifulSoup(text, 'lxml')
            spans = bs.find_all('span', class_='tah')
            print(f"DEBUG: Found {len(spans)} spans with class 'tah'")
            
            # Check row-by-row
            table = bs.find('table', class_='type2')
            if table:
                rows = table.find_all('tr')
                print(f"DEBUG: Found {len(rows)} tr tags in table.type2")
                for i, tr in enumerate(rows[:10]):
                    tds = tr.find_all('td')
                    if tds:
                        texts = [td.text.strip() for td in tds]
                        print(f"DEBUG: Row {i}: {texts}")
            else:
                print("DEBUG: table.type2 NOT FOUND")
            
            results = parse_minute_rows(symbol, bs)
            print(f"DEBUG: Final results count: {len(results)}")

if __name__ == '__main__':
    asyncio.run(main())
