from typing import Dict, List, Optional, Any, Callable, Union
import json
import asyncio
import aiohttp
import nats
from datetime import datetime
from dataclasses import dataclass
from sseclient import SSEClient
from threading import Thread
from queue import Queue
import nkeys
import tempfile
import os


@dataclass
class DeviceInfo:
    id: str
    device_id: str
    type: str
    name: Optional[str]
    status: str
    last_active: Optional[datetime]


class Page:
    def __init__(self, client: "HerdClient", device: "Device", tab_id: int):
        self.client = client
        self.device = device
        self.tab_id = int(tab_id) if isinstance(tab_id, str) else tab_id
        if not isinstance(self.tab_id, int):
            raise ValueError("Invalid tab_id: must be convertible to integer")
        self.tab = None

    @property
    def id(self) -> int:
        return self.tab_id

    @property
    def url(self) -> str:
        return self.tab.get("url", "") if self.tab else ""

    @property
    def title(self) -> str:
        return self.tab.get("title", "") if self.tab else ""

    @property
    def active(self) -> bool:
        return self.tab.get("active", False) if self.tab else False

    async def goto(self, url: str, options: Dict = None) -> None:
        """Navigate to a URL"""
        wait_until = (
            options.get("waitForNavigation", "networkidle2")
            if options
            else "networkidle2"
        )

        response = await self._execute_with_navigation(
            wait_until, "Tabs.updateTab", {"id": self.tab_id, "data": {"url": url}}
        )

        tab = response.get("result")
        if tab:
            self.update_info(tab)

        # Small delay to ensure page is ready
        await asyncio.sleep(0.5)

    async def querySelector(self, selector: str) -> Optional[Dict]:
        """Alias for $"""
        return await self.Q(selector)

    async def querySelectorAll(self, selector: str) -> List[Dict]:
        """Alias for $$"""
        return await self.QQ(selector)

    async def Q(self, selector: str, root_selector: str = None) -> Optional[Dict]:
        """Query the page for a single element (serialized)"""
        response = await self.client.send_command(
            self.device.device_id,
            "Page.$",
            {"tabId": self.tab_id, "selector": selector, "rootSelector": root_selector},
        )
        return response.get("result")

    async def QQ(self, selector: str, root_selector: str = None) -> List[Dict]:
        """Query the page for multiple elements (serialized)"""
        response = await self.client.send_command(
            self.device.device_id,
            "Page.$$",
            {"tabId": self.tab_id, "selector": selector, "rootSelector": root_selector},
        )
        return response.get("result", [])

    async def extract(self, config: Dict | str) -> Optional[Dict]:
        """Extract an element from the page"""
        is_string = isinstance(config, str)
        if is_string:
            config = {"value": config}

        response = await self.client.send_command(
            self.device.device_id,
            "Page.extract",
            {"tabId": self.tab_id, "config": config},
        )

        if is_string:
            return response.get("result", {})["value"]
        else:
            return response.get("result", {})

    async def find(self, selector: str, options: Dict = None) -> Optional[Dict]:
        """Find an element on the page"""
        response = await self.client.send_command(
            self.device.device_id,
            "Page.find",
            {"tabId": self.tab_id, "selector": selector, "options": options or {}},
        )
        return response.get("result")

    async def click(self, selector: str, options: Dict = None) -> None:
        """Click an element"""
        asyncio.create_task(
            self._execute_with_navigation(
                options.get("waitForNavigation") if options else None,
                "Page.click",
                {
                    "tabId": self.tab_id,
                    "selector": selector,
                    "options": options or {},
                },
            )
        )

    async def type(self, selector: str, text: str, options: Dict = None) -> None:
        """Type text into a form field"""
        asyncio.create_task(
            self._execute_with_navigation(
                options.get("waitForNavigation") if options else None,
                "Page.type",
                {
                    "tabId": self.tab_id,
                    "selector": selector,
                    "text": text,
                    "options": options or {},
                },
            )
        )

    async def focus(self, selector: str, options: Dict = None) -> None:
        """Focus an element"""
        asyncio.create_task(
            self._execute_with_navigation(
                options.get("waitForNavigation") if options else None,
                "Page.focus",
                {"tabId": self.tab_id, "selector": selector},
            )
        )

    async def blur(self, selector: str, options: Dict = None) -> None:
        """Blur an element"""
        asyncio.create_task(
            self._execute_with_navigation(
                options.get("waitForNavigation") if options else None,
                "Page.blur",
                {"tabId": self.tab_id, "selector": selector},
            )
        )

    async def hover(self, selector: str, options: Dict = None) -> None:
        """Hover over an element"""
        asyncio.create_task(
            self._execute_with_navigation(
                options.get("waitForNavigation") if options else None,
                "Page.hover",
                {"tabId": self.tab_id, "selector": selector},
            )
        )

    async def scroll_into_view(self, selector: str, options: Dict = None) -> None:
        """Scroll element into view"""
        asyncio.create_task(
            self._execute_with_navigation(
                options.get("waitForNavigation") if options else None,
                "Page.scrollIntoView",
                {"tabId": self.tab_id, "selector": selector},
            )
        )

    async def scroll(self, x: int, y: int, options: Dict = None) -> None:
        """Scroll element into view"""
        asyncio.create_task(
            self._execute_with_navigation(
                options.get("waitForNavigation") if options else None,
                "Page.scroll",
                {"tabId": self.tab_id, "x": x, "y": y},
            )
        )

    async def set_value(
        self, selector: str, value: Union[str, bool], options: Dict = None
    ) -> None:
        """Set value of form element"""
        asyncio.create_task(
            self._execute_with_navigation(
                options.get("waitForNavigation") if options else None,
                "Page.setValue",
                {"tabId": self.tab_id, "selector": selector, "value": value},
            )
        )

    async def dispatch_event(
        self, selector: str, event_name: str, detail: Any = None, options: Dict = None
    ) -> None:
        """Dispatch an event"""
        asyncio.create_task(
            self._execute_with_navigation(
                options.get("waitForNavigation") if options else None,
                "Page.dispatchEvent",
                {
                    "tabId": self.tab_id,
                    "selector": selector,
                    "eventName": event_name,
                    "detail": detail,
                },
            )
        )

    async def drag(
        self, source_selector: str, target_selector: str, options: Dict = None
    ) -> None:
        """Drag and drop elements"""
        asyncio.create_task(
            self._execute_with_navigation(
                options.get("waitForNavigation") if options else None,
                "Page.drag",
                {
                    "tabId": self.tab_id,
                    "sourceSelector": source_selector,
                    "targetSelector": target_selector,
                },
            )
        )

    async def close(self) -> None:
        """Close the page"""
        await self.client.send_command(
            self.device.device_id, "Tabs.closeTab", {"id": self.tab_id}
        )

    async def wait_for_navigation(self, condition: str) -> None:
        """Wait for navigation to complete"""
        await self.client.send_command(
            self.device.device_id,
            "Page.waitForNavigation",
            {"tabId": self.tab_id, "condition": condition},
        )

    async def _execute_with_navigation(
        self, wait_for_navigation: Optional[str], command: str, payload: Dict
    ) -> None:
        """Execute a command with optional navigation wait"""
        if wait_for_navigation:
            # Start navigation wait first
            navigation_promise = asyncio.create_task(
                self.wait_for_navigation(wait_for_navigation)
            )
            # Fire the command
            result = await self.client.send_command(
                self.device.device_id, command, payload
            )
            # Wait for navigation to complete
            await navigation_promise
            return result
        else:
            try:
                return await self.client.send_command(
                    self.device.device_id, command, payload
                )
            except:
                pass
            await asyncio.sleep(0.1)

    def update_info(self, tab: Dict) -> None:
        """Update tab information"""
        self.tab = tab


class Device:
    def __init__(self, client: "HerdClient", info: DeviceInfo):
        self.client = client
        self.info = info
        self.page_map = {}
        self._event_handlers = []

    @property
    def id(self) -> str:
        return self.info.id

    @property
    def device_id(self) -> str:
        return self.info.device_id

    @property
    def type(self) -> str:
        return self.info.type

    @property
    def name(self) -> Optional[str]:
        return self.info.name

    @property
    def status(self) -> str:
        return self.info.status

    @property
    def last_active(self) -> Optional[datetime]:
        return self.info.last_active

    def update_info(self, info: DeviceInfo) -> None:
        self.info = info

    async def new_page(self) -> Page:
        response = await self.client.send_command(
            self.device_id, "Tabs.createTab", {"url": "about:blank", "active": False}
        )
        tab = response.get("result", {})
        tab_id = int(tab["id"]) if isinstance(tab["id"], str) else tab["id"]

        page = Page(self.client, self, tab_id)
        self.page_map[tab_id] = page
        page.update_info(tab)
        return page

    async def list_pages(self) -> List[Page]:
        response = await self.client.send_command(self.device_id, "Tabs.getTabs")
        tabs = response.get("result", [])

        pages = []
        for tab_info in tabs:
            tab_id = (
                int(tab_info["id"])
                if isinstance(tab_info["id"], str)
                else tab_info["id"]
            )
            page = self.page_map.get(tab_id)
            if not page:
                page = Page(self.client, self, tab_id)
                self.page_map[tab_id] = page
            page.update_info(tab_info)
            pages.append(page)
        return pages

    async def get_page(self, page_id: int) -> Page:
        pages = await self.list_pages()
        page = next((p for p in pages if p.id == page_id), None)
        if not page:
            raise ValueError(f"Page {page_id} not found")
        return page

    def on_event(self, callback: Callable[[Dict], None]) -> Callable[[], None]:
        return self.client.subscribe_to_device_events(self.device_id, callback)

    def on(self, event_name: str, callback: Callable[[Dict], None]) -> "Device":
        unsubscribe = self.client.subscribe_to_device_event(
            self.device_id, event_name, callback
        )
        self._event_handlers.append(unsubscribe)
        return self

    async def close(self) -> None:
        pages = await self.list_pages()
        await asyncio.gather(*[page.close() for page in pages])
        self.page_map.clear()

        for handler in self._event_handlers:
            handler()
        self._event_handlers.clear()

        await self.client.send_command(self.device_id, "Device.close")


class HerdClient:
    def __init__(self, token: str, base_url: str = "https://herd.garden"):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.device_map = {}
        self.nats_connection = None
        self.nats_url = None
        self.nats_service_user_jwt = None
        self.nats_account_id = None
        self._session = None
        self._initialized = False

    async def _ensure_session(self):
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                }
            )

    async def _request(self, path: str, method="GET", **kwargs) -> Dict:
        await self._ensure_session()
        async with self._session.request(
            method, f"{self.base_url}{path}", **kwargs
        ) as response:
            if not response.ok:
                error = await response.json()
                raise Exception(
                    f"Request failed: {error.get('error', {}).get('message', response.reason)}"
                )
            return await response.json()

    async def initialize(self):
        if self._initialized:
            return

        # Get user info and NATS credentials
        me_data = await self._request("/api/auth/me")
        self.nats_url = me_data.get("natsUrl")

        service_user_data = await self._request("/api/auth/service-user-jwt")
        self.nats_service_user_jwt = service_user_data.get("natsServiceUserJwt")
        self.nats_account_id = service_user_data.get("natsAccountId")

        # Connect to NATS
        await self._connect_to_nats()
        self._initialized = True

    async def _connect_to_nats(self) -> None:
        """Connect to NATS server."""
        try:
            # Create a temporary file for the credentials
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
                f.write(self.nats_service_user_jwt)
                creds_path = f.name

            try:
                # Connect to NATS with credentials file
                self.nats_connection = await nats.connect(
                    self.nats_url,
                    user_credentials=creds_path,
                    name=f"acc_{self.nats_account_id}",
                    max_reconnect_attempts=10,
                    reconnect_time_wait=1000,
                    # timeout=20000,
                )
                print("[HerdClient] Welcome to the Herd!")
            finally:
                # Clean up the temporary file
                os.unlink(creds_path)
        except Exception as e:
            print(f"[HerdClient] Failed to connect to NATS: {str(e)}")
            raise

    async def send_command(
        self, device_id: str, command: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send a command to a device and wait for the response."""
        try:
            # Remove 'device-' prefix if it exists to avoid duplication
            device_id = device_id.replace("device-", "")
            subject = f"device-{device_id}.{command}"
            response = await self.nats_connection.request(
                subject,
                json.dumps(payload).encode(),
                timeout=60,  # Increase timeout to 60 seconds
            )
            return json.loads(response.data.decode())
        except Exception as e:
            print(
                f"[HerdClient] Failed to send command {command} to device {device_id}: {e}"
            )
            raise

    async def list_devices(self) -> List[Device]:
        devices_data = await self._request("/api/devices")
        devices = []
        for info in devices_data:
            device_info = DeviceInfo(
                id=info["id"],
                device_id=info["deviceId"],
                type=info["type"],
                name=info.get("name"),
                status=info["status"],
                last_active=(
                    datetime.fromisoformat(info["lastActive"])
                    if info.get("lastActive")
                    else None
                ),
            )

            device = self.device_map.get(info["deviceId"])
            if not device:
                device = Device(self, device_info)
                self.device_map[info["deviceId"]] = device
            else:
                device.update_info(device_info)
            devices.append(device)
        return devices

    async def get_device(self, device_id: str) -> Device:
        devices = await self.list_devices()
        device = next((d for d in devices if d.device_id == device_id), None)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        return device

    async def register_device(
        self, device_id: str, device_type: str, name: str = None
    ) -> DeviceInfo:
        response = await self._request(
            "/api/devices/register",
            method="POST",
            json={"deviceId": device_id, "type": device_type, "name": name},
        )
        return DeviceInfo(**response)

    def subscribe_to_device_events(
        self, device_id: str, callback: Callable[[Dict], None]
    ) -> Callable[[], None]:
        def event_listener():
            client = SSEClient(
                f"{self.base_url}/api/devices/{device_id}/events",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            for event in client:
                try:
                    data = json.loads(event.data)
                    callback(data)
                except Exception as e:
                    print(f"Error processing event: {e}")

        thread = Thread(target=event_listener, daemon=True)
        thread.start()

        def cleanup():
            # Note: SSEClient doesn't provide a clean way to stop.
            # In a production environment, you'd want to implement a proper
            # shutdown mechanism here.
            pass

        return cleanup

    def subscribe_to_device_event(
        self, device_id: str, event_name: str, callback: Callable[[Dict], None]
    ) -> Callable[[], None]:
        def event_listener():
            client = SSEClient(
                f"{self.base_url}/api/devices/{device_id}/events/{event_name}",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            for event in client:
                try:
                    data = json.loads(event.data)
                    callback(data)
                except Exception as e:
                    print(f"Error processing event: {e}")

        thread = Thread(target=event_listener, daemon=True)
        thread.start()

        def cleanup():
            # Note: SSEClient doesn't provide a clean way to stop.
            # In a production environment, you'd want to implement a proper
            # shutdown mechanism here.
            pass

        return cleanup

    async def close(self):
        if self.nats_connection:
            await self.nats_connection.close()
            self.nats_connection = None

        if self._session:
            await self._session.close()
            self._session = None

        self._initialized = False
