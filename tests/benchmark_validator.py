#!/usr/bin/env python3
"""Performance benchmark for SAR validator improvements.

This script demonstrates the performance improvements made to the validator:
- Caching findall() results to avoid redundant XPath searches
- Optimizing placeholder value checking
"""

import sys
import timeit
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sar_parser import validate_string


# Small SAR document
SMALL_SAR = """
<SAR>
  <FilerInformation>
    <FilerName>Example Financial</FilerName>
  </FilerInformation>
  <Subjects>
    <Subject><Name>John Doe</Name></Subject>
  </Subjects>
  <Transactions>
    <Transaction><Amount currency="USD">1000.50</Amount></Transaction>
  </Transactions>
</SAR>
"""

# Larger SAR document with multiple transactions (more realistic)
LARGE_SAR = """
<SAR>
  <FilerInformation>
    <FilerName>Example Financial</FilerName>
  </FilerInformation>
  <Subjects>
    <Subject><Name>John Doe</Name></Subject>
    <Subject><Name>Jane Smith</Name></Subject>
    <Subject><Name>Bob Johnson</Name></Subject>
  </Subjects>
  <Transactions>
    <Transaction><Amount currency="USD">1000.50</Amount></Transaction>
    <Transaction><Amount currency="USD">2000.75</Amount></Transaction>
    <Transaction><Amount currency="USD">3000.00</Amount></Transaction>
    <Transaction><Amount currency="USD">4000.25</Amount></Transaction>
    <Transaction><Amount currency="USD">5000.50</Amount></Transaction>
    <Transaction><Amount currency="USD">6000.75</Amount></Transaction>
    <Transaction><Amount currency="USD">7000.00</Amount></Transaction>
    <Transaction><Amount currency="USD">8000.25</Amount></Transaction>
    <Transaction><Amount currency="USD">9000.50</Amount></Transaction>
    <Transaction><Amount currency="USD">10000.75</Amount></Transaction>
  </Transactions>
</SAR>
"""


def benchmark(xml_doc, iterations=10000):
    """Benchmark validation performance."""
    time = timeit.timeit(lambda: validate_string(xml_doc), number=iterations)
    avg_ms = time / iterations * 1000
    per_sec = iterations / time
    return avg_ms, per_sec


if __name__ == "__main__":
    print("SAR Validator Performance Benchmark")
    print("=" * 60)
    
    print("\n1. Small SAR document (1 transaction):")
    avg_ms, per_sec = benchmark(SMALL_SAR, 10000)
    print(f"   Average time: {avg_ms:.4f} ms")
    print(f"   Throughput:   {per_sec:,.0f} validations/sec")
    
    print("\n2. Large SAR document (10 transactions, 3 subjects):")
    avg_ms, per_sec = benchmark(LARGE_SAR, 10000)
    print(f"   Average time: {avg_ms:.4f} ms")
    print(f"   Throughput:   {per_sec:,.0f} validations/sec")
    
    print("\n" + "=" * 60)
    print("Performance improvements implemented:")
    print("  ✓ Cached findall() results to avoid redundant XPath searches")
    print("  ✓ Optimized placeholder checking with fast path for None/empty")
    print("  ✓ Reduced string operations in validation loops")
    print("=" * 60)
