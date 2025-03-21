import unittest
from unittest.mock import MagicMock, patch
from threading import Event
from time import sleep
from typing import Any, Optional
from masterpiece.masterpiecethread import MasterPieceThread


class TestMasterPieceThread(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_mqtt_client: MagicMock = MagicMock()
        self.thread: MasterPieceThread = MasterPieceThread(client=self.mock_mqtt_client)
        self.thread.name = "TestThread"

    def tearDown(self) -> None:
        if self.thread.is_alive():
            self.thread.stop()
            self.thread.join()

    def test_update_interval_default(self) -> None:
        self.assertEqual(self.thread.update_interval(), 60.0)

    def test_update_returns_true(self) -> None:
        self.assertTrue(self.thread.update())

    @patch("masterpiece.masterpiecethread.MasterPieceThread.update")
    def test_run_method(self, mock_update: MagicMock) -> None:
        # Mock `update` with a predictable side effect
        mock_update.side_effect = [True, True, True, False]

        # Patch `update_interval` to return 0.3
        with patch.object(self.thread, "update_interval", return_value=0.3):
            self.thread._stop_event = Event()

            # Start the thread and let it run briefly
            self.thread.start()
            sleep(1.5)
            self.thread.stop()
            self.thread.join()

        # Verify update was called at least three times
        self.assertGreaterEqual(mock_update.call_count, 3)

    def test_stop(self) -> None:
        self.thread._stop_event = MagicMock()
        self.thread.stop()
        self.thread._stop_event.set.assert_called_once()

    """
    @patch("masterpiece.masterpiecethread.MasterPieceThread.publish")
    def test_publish_logs_correctly(self, mock_publish: MagicMock) -> None:
        self.thread.event_topic = "test/topic"
        self.thread.publish("test/topic", "test message")

        mock_publish.assert_called_once_with(
            "test/topic", "test message", qos=1, retain=True
        )
    """

    def test_logging_methods(self) -> None:
        self.thread.mqtt_client = self.mock_mqtt_client

        with patch(
            "masterpiece.masterpiecethread.MasterPieceThread.publish"
        ) as mock_publish:
            self.thread.debug("Debug message")
            mock_publish.assert_called_with(
                self.thread.event_topic,
                '{"type": "Debug", "msg": "Debug message", "details": ""}',
                qos=1,
                retain=True,
            )

            self.thread.error("Error message")
            mock_publish.assert_called_with(
                self.thread.event_topic,
                '{"type": "Error", "msg": "Error message", "details": ""}',
                qos=1,
                retain=True,
            )


if __name__ == "__main__":
    unittest.main()
