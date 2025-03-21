import asyncio
import json
import websockets

from django.test import TestCase
from unittest.mock import patch, MagicMock, AsyncMock
from plugin.manager import plugin_manager
from whitebox_plugin_stratux.whitebox_plugin_stratux import should_emit


async def deactivate_websocket_loop_after_delay(plugin, delay):
    await asyncio.sleep(delay)
    plugin.is_active = False


class TestWhiteboxPluginStratux(TestCase):
    def setUp(self) -> None:
        plugin_manager.plugins = []
        plugin_manager.previously_discovered_plugins = {}
        plugin_manager.discover_plugins()

        self.plugin = next(
            (
                x
                for x in plugin_manager.plugins
                if x.__class__.__name__ == "WhiteboxPluginStratux"
            ),
            None,
        )
        return super().setUp()

    def test_plugin_loaded(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_initialization(self):
        self.assertEqual(self.plugin.name, "Stratux")
        self.assertEqual(self.plugin.STRATUX_URL, "ws://stratux:80")
        self.assertFalse(self.plugin.is_active)
        self.assertIsNone(self.plugin.traffic_task)
        self.assertIsNone(self.plugin.situation_task)

    @patch("plugin.utils.WhiteboxStandardAPI.register_event_callback")
    def test_event_callbacks_registered(self, mock_register_event_callback):
        self.plugin.whitebox.register_event_callback(
            "flight_start", self.plugin.on_flight_start
        )
        self.plugin.whitebox.register_event_callback(
            "flight_end", self.plugin.on_flight_end
        )

        mock_register_event_callback.assert_any_call(
            "flight_start", self.plugin.on_flight_start
        )
        mock_register_event_callback.assert_any_call(
            "flight_end", self.plugin.on_flight_end
        )

    async def test_on_flight_start(self):
        with (
            patch.object(self.plugin, "gather_traffic") as mock_gather_traffic,
            patch.object(self.plugin, "gather_situation") as mock_gather_situation,
            patch.object(self.plugin, "gather_status") as mock_gather_status,
        ):
            await self.plugin.on_flight_start(None)

            self.assertTrue(self.plugin.is_active)
            self.assertIsNotNone(self.plugin.traffic_task)
            self.assertIsNotNone(self.plugin.situation_task)
            mock_gather_traffic.assert_called_once()
            mock_gather_situation.assert_called_once()
            mock_gather_status.assert_called_once()

    async def test_on_flight_end(self):
        traffic_task_mock = MagicMock()
        traffic_task_mock.cancel = MagicMock()

        situation_task_mock = MagicMock()
        situation_task_mock.cancel = MagicMock()

        status_task_mock = MagicMock()
        status_task_mock.cancel = MagicMock()

        self.plugin.is_active = True
        self.plugin.traffic_task = traffic_task_mock
        self.plugin.situation_task = situation_task_mock
        self.plugin.status_task = status_task_mock

        await self.plugin.on_flight_end(None)

        self.assertFalse(self.plugin.is_active)

        traffic_task_mock.cancel.assert_called_once()
        situation_task_mock.cancel.assert_called_once()
        status_task_mock.cancel.assert_called_once()

        self.assertIsNone(self.plugin.traffic_task)
        self.assertIsNone(self.plugin.situation_task)
        self.assertIsNone(self.plugin.status_task)

    async def test_should_emit_with_throttle(self):
        self.assertTrue(await should_emit())

        emit_every = 2
        last_emit = asyncio.get_event_loop().time()

        self.assertFalse(await should_emit(emit_every, last_emit))

        await asyncio.sleep(2)
        self.assertTrue(await should_emit(emit_every, last_emit))

    @patch("websockets.connect")
    async def test_gather_situation(self, mock_connect):
        mock_ws = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_ws

        situation_data = {
            "GPSLatitude": 37.7749,
            "GPSLongitude": -122.4194,
            "GPSAltitudeMSL": 1000,
        }

        mock_ws.recv.side_effect = [
            json.dumps(situation_data),
            websockets.exceptions.ConnectionClosed(None, None),
        ]

        self.plugin.is_active = True
        self.plugin.whitebox.api.location.emit_location_update = AsyncMock()

        deactivate_task = asyncio.create_task(
            deactivate_websocket_loop_after_delay(self.plugin, 0.1)
        )
        await self.plugin.gather_situation(situation_data)
        await deactivate_task

        self.plugin.whitebox.api.location.emit_location_update.assert_called_with(
            37.7749, -122.4194, 1000
        )

    @patch("websockets.connect")
    async def test_gather_traffic(self, mock_connect):
        mock_ws = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_ws

        traffic_data = {
            "Tail": "N12345",
            "Icao_addr": "A12345",
            "Lat": 37.7749,
            "Lng": -122.4194,
        }

        mock_ws.recv.side_effect = [
            json.dumps(traffic_data),
            websockets.exceptions.ConnectionClosed(None, None),
        ]

        self.plugin.is_active = True
        self.plugin.whitebox.api.traffic.emit_traffic_update = AsyncMock()

        deactivate_task = asyncio.create_task(
            deactivate_websocket_loop_after_delay(self.plugin, 0.1)
        )
        await self.plugin.gather_traffic(traffic_data)
        await deactivate_task

        self.plugin.whitebox.api.traffic.emit_traffic_update.assert_called_with(
            traffic_data
        )

    @patch("websockets.connect")
    async def test_gather_status(self, mock_connect):
        mock_ws = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_ws

        status_data = {
            "GPS_connected": True,
            "GPS_solution": "No Fix",
            "GPS_detected_type": 25,
        }

        mock_ws.recv.side_effect = [
            json.dumps(status_data),
            websockets.exceptions.ConnectionClosed(None, None),
        ]

        self.plugin.is_active = True
        self.plugin.whitebox.api.status.emit_status_update = AsyncMock()

        deactivate_task = asyncio.create_task(
            deactivate_websocket_loop_after_delay(self.plugin, 0.1)
        )
        await self.plugin.gather_status(status_data)
        await deactivate_task

        self.plugin.whitebox.api.status.emit_status_update.assert_called_with(
            status_data
        )
