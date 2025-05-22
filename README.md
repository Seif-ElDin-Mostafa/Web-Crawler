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
streamlit run streamlit_app.py
```

The dashboard provides:
- URL input for crawling
- Real-time crawling status
- Data visualization
- Error handling and debug logs

### Command Line Usage

You can also use the crawler from the command line:
```bash
python main.py <base-url> <category-url> --max-pages 3 --output-json data.json --output-csv data.csv
```

## Project Structure

- `main.py`: Entry point for command-line usage
- `streamlit_app.py`: Streamlit dashboard interface
- `content_extractor.py`: Core content extraction logic
- `js_api_handler.py`: Dynamic content rendering with Selenium
- `robot_parser.py`: Robots.txt parsing and compliance checking

## License

MIT License 