import logging
import unittest

from sar_parser.pipeline import SARProcessor

VALID_SAR_XML = """\
<SAR>
  <FilingInformation>
    <FilingType>Initial</FilingType>
  </FilingInformation>
  <FilerInformation>
    <FilerName>Example Financial</FilerName>
  </FilerInformation>
  <Subjects>
    <Subject>
      <Name>John Doe</Name>
    </Subject>
  </Subjects>
  <Transactions>
    <Transaction>
      <Amount>100.00</Amount>
    </Transaction>
  </Transactions>
</SAR>
"""


class ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class FakeMetricsRecorder:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def record(self, name: str, value: float = 1.0, *, correlation_id: str | None = None, **labels: str) -> None:
        self.events.append({
            "name": name,
            "value": value,
            "correlation_id": correlation_id,
            "labels": labels,
        })


class FakeTransactionManager:
    def __init__(self, *, should_raise_commit: bool = False) -> None:
        self.should_raise_commit = should_raise_commit
        self.calls: list[str] = []

    def begin(self) -> None:
        self.calls.append("begin")

    def commit(self) -> None:
        self.calls.append("commit")
        if self.should_raise_commit:
            raise RuntimeError("commit failure")

    def rollback(self) -> None:
        self.calls.append("rollback")


class FakeRepository:
    def __init__(self, *, should_raise: bool = False) -> None:
        self.should_raise = should_raise
        self.saved_payloads: list[tuple[str, str]] = []

    def save(self, xml_text: str, correlation_id: str) -> None:
        self.saved_payloads.append((xml_text, correlation_id))
        if self.should_raise:
            raise RuntimeError("storage failure")


class SARProcessorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metrics = FakeMetricsRecorder()
        self.txn = FakeTransactionManager()
        self.repository = FakeRepository()
        self.handler = ListHandler()
        self.logger = logging.getLogger("sar_processor_tests")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)

    def tearDown(self) -> None:
        self.logger.removeHandler(self.handler)

    def test_process_runs_validation_and_commits(self) -> None:
        processor = SARProcessor(
            repository=self.repository,
            transactions=self.txn,
            metrics=self.metrics,
            logger=self.logger,
        )

        result = processor.process(VALID_SAR_XML, correlation_id="abc-123")

        self.assertTrue(result.is_valid)
        self.assertEqual(self.txn.calls, ["begin", "commit"])
        self.assertEqual(self.repository.saved_payloads, [(VALID_SAR_XML, "abc-123")])
        self.assertTrue(any(record.correlation_id == "abc-123" for record in self.handler.records))
        metric_names = {event["name"] for event in self.metrics.events}
        self.assertIn("sar.storage.transaction_committed", metric_names)
        self.assertIn("sar.request.completed", metric_names)

    def test_process_short_circuits_on_validation_error(self) -> None:
        processor = SARProcessor(
            repository=self.repository,
            transactions=self.txn,
            metrics=self.metrics,
            logger=self.logger,
        )

        invalid_xml = "<SAR><FilerInformation /></SAR>"
        result = processor.process(invalid_xml, correlation_id="abc-123")

        self.assertFalse(result.is_valid)
        self.assertEqual(self.txn.calls, [])
        metric_names = {event["name"] for event in self.metrics.events}
        self.assertIn("sar.request.rejected", metric_names)
        self.assertNotIn("sar.storage.saved", metric_names)

    def test_rolls_back_on_storage_failure(self) -> None:
        processor = SARProcessor(
            repository=FakeRepository(should_raise=True),
            transactions=self.txn,
            metrics=self.metrics,
            logger=self.logger,
        )

        with self.assertRaises(RuntimeError):
            processor.process(VALID_SAR_XML, correlation_id="abc-123")

        self.assertEqual(self.txn.calls, ["begin", "rollback"])
        metric_names = {event["name"] for event in self.metrics.events}
        self.assertIn("sar.storage.failed", metric_names)
        self.assertTrue(any(record.correlation_id == "abc-123" for record in self.handler.records))

    def test_rolls_back_when_commit_fails(self) -> None:
        processor = SARProcessor(
            repository=self.repository,
            transactions=FakeTransactionManager(should_raise_commit=True),
            metrics=self.metrics,
            logger=self.logger,
        )

        with self.assertRaises(RuntimeError):
            processor.process(VALID_SAR_XML, correlation_id="abc-123")

        self.assertEqual(processor.transactions.calls, ["begin", "commit", "rollback"])
        metric_names = {event["name"] for event in self.metrics.events}
        self.assertIn("sar.storage.failed", metric_names)


if __name__ == "__main__":
    unittest.main()
