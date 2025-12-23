#!/usr/bin/env python3
"""
Orchestration script for KRX market data collection.
Coordinates symbol, day, and minute data collection modules.
"""

import sys
import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / 'src'
if not src_path.exists():
    src_path = Path('/app/src')
sys.path.insert(0, str(src_path))

# Import the collection modules
from symbol import fetch_symbols
from day import collect_day_data
from minute import collect_minute_data


async def main_async(date, output_dir, concurrency):
    """Main orchestration: symbols -> (day || minute) for each market"""
    print(f'[INFO] Starting market data collection for {date}', file=sys.stderr)
    
    output_path = Path(output_dir)
    
    # Step 1: Fetch symbols
    print('[INFO] Fetching symbols for KOSPI and KOSDAQ...', file=sys.stderr)
    kospi_symbols, kosdaq_symbols = await asyncio.gather(
        fetch_symbols('KOSPI'),
        fetch_symbols('KOSDAQ')
    )
    
    total_symbols = len(kospi_symbols or []) + len(kosdaq_symbols or [])
    print(f'[INFO] Total symbols discovered: {total_symbols} (KOSPI: {len(kospi_symbols or [])}, KOSDAQ: {len(kosdaq_symbols or [])})', file=sys.stderr)
    
    if total_symbols == 0:
        print('[ERROR] No symbols found for either market, exiting', file=sys.stderr)
        return 1
    
    # Step 2: Prepare tasks
    # We maintain an explicit mapping to avoid index confusion
    task_map = {}
    if kospi_symbols:
        task_map['KOSPI_DAY'] = collect_day_data(date, kospi_symbols, concurrency)
        task_map['KOSPI_MINUTE'] = collect_minute_data(date, kospi_symbols, concurrency)
    
    if kosdaq_symbols:
        task_map['KOSDAQ_DAY'] = collect_day_data(date, kosdaq_symbols, concurrency)
        task_map['KOSDAQ_MINUTE'] = collect_minute_data(date, kosdaq_symbols, concurrency)
    
    # Step 3: Execute tasks
    keys = list(task_map.keys())
    print(f'[INFO] Dispatching {len(keys)} collection tasks...', file=sys.stderr)
    results_list = await asyncio.gather(*[task_map[k] for k in keys])
    
    # Map results back to their types
    named_results = dict(zip(keys, results_list))
    
    # Step 4: Combine results
    day_results = []
    minute_results = []
    
    for key, data in named_results.items():
        count = len(data)
        print(f'[INFO] Task {key} finished: collected {count} records', file=sys.stderr)
        if 'DAY' in key:
            day_results.extend(data)
        else:
            minute_results.extend(data)
    
    print(f'[INFO] Final counts - Day: {len(day_results)}, Minute: {len(minute_results)}', file=sys.stderr)
    
    # Step 5: Save results
    day_file = output_path / 'day' / f'{date}.txt'
    minute_file = output_path / 'minute' / f'{date}.txt'
    
    # Save day data
    day_file.parent.mkdir(parents=True, exist_ok=True)
    with open(day_file, 'w') as f:
        for line in sorted(day_results):
            f.write(line + '\n')
    print(f'[INFO] Day data saved to {day_file}', file=sys.stderr)
    
    # Save minute data
    minute_file.parent.mkdir(parents=True, exist_ok=True)
    with open(minute_file, 'w') as f:
        # Sort by time (4th column)
        sorted_lines = sorted(minute_results, key=lambda x: x.split('\t')[3] if len(x.split('\t')) > 3 else '')
        for line in sorted_lines:
            f.write(line + '\n')
    print(f'[INFO] Minute data saved to {minute_file}', file=sys.stderr)
    
    return 0


def main():
    """Entry point for orchestration"""
    # Use environment variables or defaults
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')
    
    # Use fixed internal paths (Docker paths)
    output_dir = Path('/data')
    concurrency = 20
    
    try:
        exit_code = asyncio.run(main_async(date, str(output_dir), concurrency))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print('\n[INFO] Interrupted by user', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'[ERROR] Unexpected error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
