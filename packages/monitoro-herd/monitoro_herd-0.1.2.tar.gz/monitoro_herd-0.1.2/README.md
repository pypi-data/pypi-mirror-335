# Herd Python SDK

A powerful SDK for controlling your own browser and other devices through the [Herd](https://herd.garden) platform. Similar to Puppeteer but with support for multiple devices and real-time events, and no infrastructure to setup.

Learn more about Herd at [https://herd.garden](https://herd.garden).

## Features

- 🌐 Control multiple browsers and devices from a single client
- ⛏️ Extract data from web pages
- 🔍 Run automations and interact with webpages
- 🤖 Build AI web tools that can use your own browser and accounts
- 🚀 Familiar automation API similar to Puppeteer
- 🧩 Python type hints for better IDE support

## Installation

```bash
pip install monitoro-herd
```

## Usage

Here's a basic example of how to use the SDK:

```python
import asyncio
from monitoro_herd import HerdClient

async def example():
    # Create a client
    client = HerdClient(
        token='your-auth-token'
    )

    # Initialize the client (required before using)
    await client.initialize()

    try:
        # List available devices
        devices = await client.list_devices()
        print('Available devices:', devices)

        # Get a specific device
        device = await client.get_device('device-id')

        # Create a new page
        page = await device.new_page()

        # Navigate to a URL
        await page.goto('https://example.com')

        # Click an element
        await page.click('#submit-button')

        # Fill a form field
        await page.fill('#username', 'testuser')

        # Extract data
        data = await page.extract({
            'title': 'h1',
            'description': '.description',
            'items': {
                'price': '.item-price',
                'name': '.item-name'
            }
        })
        print('Extracted data:', data)

        # Subscribe to device events
        def handle_event(event):
            print('Device event:', event)

        unsubscribe = device.on_event(handle_event)

        # Cleanup
        unsubscribe()
        await page.close()
        await device.close()
    finally:
        # Always close the client when done
        await client.close()

# Run the example
asyncio.run(example())
```

## Features

- Asynchronous API using `asyncio`
- Device management
- Browser automation
- Event subscription
- Data extraction
- Automatic reconnection handling
- Type hints for better IDE support

## API Reference

Complete API reference is available at [https://herd.garden/docs/reference](https://herd.garden/docs/reference).

### HerdClient

The main client class for interacting with the Herd platform.

```python
client = HerdClient(token: str)
```

Methods:
- `initialize()` - Initialize the client and connect to NATS
- `list_devices()` - Get a list of available devices
- `get_device(device_id: str)` - Get a specific device
- `register_device(device_id: str, device_type: str, name: str = None)` - Register a new device
- `close()` - Close the client and cleanup resources

### Device

Represents a device in the Herd platform.

Methods:
- `new_page()` - Create a new page
- `list_pages()` - List all pages
- `get_page(page_id: int)` - Get a specific page
- `on_event(callback)` - Subscribe to device events
- `close()` - Close the device and cleanup resources

### Page

Represents a browser page/tab.

Methods:
- `goto(url: str)` - Navigate to a URL
- `click(selector: str, options: Dict = None)` - Click an element
- `fill(selector: str, value: str, options: Dict = None)` - Fill a form field
- `extract(selectors: Dict)` - Extract data from the page
- `close()` - Close the page

## Error Handling

The SDK uses exceptions to handle errors. Make sure to handle these appropriately in your code:

```python
try:
    await client.initialize()
except Exception as e:
    print(f"Failed to initialize client: {e}")
```

## Best Practices

1. Always use `async/await` with the SDK functions
2. Initialize the client before using it
3. Close resources when done using them
4. Handle exceptions appropriately
5. Use type hints for better code completion
6. Subscribe to events when needed for real-time updates

## Contact us

If you have any questions or feedback, please contact us at [pypi@herd.garden](mailto:pypi@herd.garden).

## License

EULA - see [LICENSE](LICENSE)