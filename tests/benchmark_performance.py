"""Performance benchmarks for the SAR validator.

This module contains performance tests to ensure optimizations maintain
or improve execution speed. These tests are not part of the regular test
suite but can be run manually to validate performance improvements.
"""

import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sar_parser import validate_string


def generate_sar_xml(num_transactions: int) -> str:
    """Generate a SAR XML document with the specified number of transactions."""
    xml = """<SAR>
  <FilerInformation>
    <FilerName>Example Financial</FilerName>
  </FilerInformation>
  <Subjects>
    <Subject><Name>John Doe</Name></Subject>
  </Subjects>
  <Transactions>
"""
    for i in range(num_transactions):
        xml += f"""    <Transaction>
      <Date>2024-04-30</Date>
      <Amount currency="USD">{i}.50</Amount>
    </Transaction>
"""
    xml += """  </Transactions>
</SAR>
"""
    return xml


def benchmark_validation(num_transactions: int, num_iterations: int = 100) -> float:
    """Benchmark validation performance.
    
    Args:
        num_transactions: Number of transactions in the test document
        num_iterations: Number of times to run validation
        
    Returns:
        Average time per validation in milliseconds
    """
    xml_text = generate_sar_xml(num_transactions)
    
    start_time = time.perf_counter()
    for _ in range(num_iterations):
        result = validate_string(xml_text)
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    avg_time_ms = (total_time / num_iterations) * 1000
    
    return avg_time_ms


def main():
    """Run performance benchmarks."""
    print("SAR Validator Performance Benchmarks")
    print("=" * 60)
    
    test_cases = [
        (10, 1000),    # Small document, many iterations
        (100, 100),    # Medium document
        (1000, 10),    # Large document, fewer iterations
    ]
    
    for num_transactions, num_iterations in test_cases:
        avg_time = benchmark_validation(num_transactions, num_iterations)
        print(f"\n{num_transactions} transactions, {num_iterations} iterations:")
        print(f"  Average time: {avg_time:.4f} ms per validation")
        print(f"  Throughput: {1000/avg_time:.2f} validations/second")
    
    print("\n" + "=" * 60)
    print("Benchmark complete!")
    
    # Test with placeholder checking
    print("\nTesting placeholder detection performance...")
    xml_with_placeholders = """<SAR>
  <FilerInformation>
    <FilerName>Example Financial</FilerName>
  </FilerInformation>
  <Subjects>
    <Subject><Name>John Doe</Name></Subject>
  </Subjects>
  <Transactions>
"""
    placeholders = ["UNKNOWN", "PENDING", "NOT APPLICABLE", ""]
    for i in range(100):
        placeholder = placeholders[i % len(placeholders)]
        xml_with_placeholders += f"""    <Transaction>
      <Date>2024-04-30</Date>
      <Amount currency="USD">{placeholder}</Amount>
    </Transaction>
"""
    xml_with_placeholders += """  </Transactions>
</SAR>
"""
    
    start_time = time.perf_counter()
    for _ in range(100):
        result = validate_string(xml_with_placeholders)
    end_time = time.perf_counter()
    
    avg_time_ms = ((end_time - start_time) / 100) * 1000
    print(f"  100 transactions with placeholders: {avg_time_ms:.4f} ms per validation")
    print(f"  All placeholders correctly detected: {len(result.errors) == 100}")


if __name__ == "__main__":
    main()
