# dalle-generator

An image generator that focuses on prompt adherence and unique aesthetics.

## Installation

```bash
pip install dalle-generator
```

## Key Features

- 🎨 **Image Generation**
  - Text-to-Image Generation
  - Multiple Image Output
  - Smart Prompt Handling
- 🔄 **Flexible Integration**
  - Interactive Web UI
  - REST API Server
  - Python Library
- 💾 **Output Management**
  - Multiple Output Formats
  - Date-based Organization
  - Automatic File Naming

## Usage

### Python Library

```python
from dalle_generator import DalleGenerator

# Initialize
client = DalleGenerator(
    mode="default",       # Mode (default/webui/api)
    log_on=True,          # Enable logging
    log_to=None,          # Log directory
    save_to="outputs",    # Output directory
    save_as="webp"        # Output format (webp/jpg/pil)
)

# Generate images
results = client.image_generate(
    prompt="a beautiful landscape"
)

# Returns list of file paths or PIL Images if save_as='pil'
```

### Web UI

Start the Gradio web interface:

```python
client = DalleGenerator(mode="webui")
# OR
client.start_webui(
    host="0.0.0.0",    # Server host
    port=5735,         # Server port
    browser=True,      # Launch browser
    upload_size="4MB", # Max upload size
    public=False,      # Enable public URL
    limit=10           # Max concurrent requests
)
```

### REST API

Start the Flask API server:

```python
client = DalleGenerator(mode="api")
# OR
client.start_api(
    host="0.0.0.0",    # Server host
    port=5734,         # Server port
    debug=False        # Enable debug mode
)
```

#### API Endpoints

- `POST /v1/api/image/generate`

## Configuration

### Output Formats
- `webp` - High quality, small size
- `jpg` - Standard compressed
- `pil` - PIL Image object

### Output Structure
```
outputs/
└── YYYY-MM-DD/
    ├── YYYYMMDD_HHMMSS_UUID8_1.webp
    ├── YYYYMMDD_HHMMSS_UUID8_2.webp
    └── ...
```

## License

See [LICENSE](LICENSE) for details.
