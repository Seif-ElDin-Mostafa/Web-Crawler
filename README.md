# Web Crawler with Dynamic Content Support

A Python-based web crawler specifically designed to handle both static and JavaScript-rendered content. Features a Streamlit dashboard for easy visualization and control.

## Features

- Static and dynamic content crawling
- Automatic detection of JavaScript-heavy pages
- Selenium support for rendering dynamic content
- Beautiful Soup parsing for efficient data extraction
- Streamlit dashboard for visualization
- Robots.txt compliance checking
- RSS feed detection
- Configurable crawling parameters
- Automatic output file management

## Requirements

- Python 3.7+
- Chrome/Chromium browser
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd web-crawler
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Streamlit Dashboard

Run the Streamlit dashboard:
```bash
streamlit run src/streamlit_app.py
```

The dashboard provides:
- URL input for crawling
- Real-time crawling status
- Data visualization
- Error handling and debug logs
- One-click data saving to output directory

### Command Line Usage

You can also use the crawler from the command line:
```bash
python src/main.py <base-url> <category-url> --max-pages 3
```

By default, output files are saved to the `output/` directory:
- JSON output: `output/data.json`
- CSV output: `output/data.csv`

You can specify custom output paths:
```bash
python src/main.py <base-url> <category-url> --output-json custom.json --output-csv custom.csv
```

## Project Structure

```
web-crawler/
├── src/
│   ├── main.py              # Command-line entry point
│   ├── streamlit_app.py     # Streamlit dashboard interface
│   └── modules/
│       ├── __init__.py
│       ├── content_extractor.py  # Core content extraction logic
│       ├── js_api_handler.py     # Dynamic content rendering with Selenium
│       └── robot_parser.py       # Robots.txt parsing and compliance
├── output/                  # Default directory for crawled data
│   └── .gitkeep            # Placeholder to maintain directory
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## License

MIT License 