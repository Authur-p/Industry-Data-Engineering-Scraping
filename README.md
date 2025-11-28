# 🏢 Finelib Business Data Scraper

A high-performance asynchronous web scraper built with Python and Playwright to extract comprehensive business information from Finelib.com. This tool efficiently collects company data across multiple categories with intelligent duplicate prevention and robust error handling.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-Async-green.svg)
![License](https://img.shields.io/badge/License-MIT-orange.svg)

## ✨ Features

- **⚡ Asynchronous Processing** - Concurrent scraping for maximum performance
- **📊 Multi-Category Support** - Scrape multiple business sectors in one run
- **🔄 Smart Deduplication** - Prevents duplicate entries in the dataset
- **🛡️ Robust Error Handling** - Continues processing even when individual requests fail
- **💾 Efficient CSV Management** - Appends new data while preserving existing records
- **🌐 Real Browser Automation** - Uses Playwright for reliable JavaScript rendering
- **📅 Timestamp Tracking** - Records when each entry was last checked

## 🗂️ Data Extracted

For each company, the scraper collects:
- **Company Name** - Official business name
- **Category** - Business sector classification
- **Contact Information** - Phone numbers, email addresses
- **Location Data** - Address, city, state
- **Online Presence** - Website URL, source page
- **Metadata** - Timestamp, error logs (if any)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- Stable internet connection

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/finelib-scraper.git
   cd finelib-scraper
   ```

2. **Create Virtual Environment**

   ```bash
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**

   Create a `requirements.txt` file:
   ```txt
   playwright>=1.40.0
   aiofiles>=23.0.0
   ```

   Then install:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright Browsers**
   ```bash
   playwright install chromium
   ```

### Configuration

Create `scraper.py` with your scraping logic and update your search categories:

```python\SEARCH_TERM = ["oil and gas", "Microfinance Banks", "Hospitals", "Clinics"]
```

### Usage

Run the scraper:
```bash
python scraper.py
```

The script will:
- Check existing data in `companies.csv`
- Skip already processed categories
- Scrape new categories with progress indicators
- Save results automatically

## 📁 Project Structure
```
finelib-scraper/
├── scraper.py              # Main scraping script
├── companies.csv           # Output data (created automatically)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🛠️ Technical Architecture

### Core Components

#### **Async Orchestration (`main()`)**
- Manages category iteration
- Implements existence checks
- Coordinates scraping workflow

#### **Browser Management (`async_scraping()`)**
- Controls Playwright instances
- Handles pagination logic
- Manages resource cleanup

#### **Data Processing (`process_company()`)**
- Extracts structured company data
- Handles CSS selectors and DOM parsing
- Implements fallback values for missing data

#### **Storage Layer (`write_csv_async()`)**
- Async file operations with aiofiles
- Duplicate detection logic
- Dynamic CSV header management

### Key Technologies
- Playwright (Browser automation)
- Asyncio (Async I/O framework)
- Aiofiles (Async file operations)
- CSV module (Data serialization)

## 📊 Output Format

### `companies.csv` Columns

| Column        | Description           | Example |
|---------------|-----------------------|---------|
| category      | Business sector       | "oil and gas" |
| company_name  | Company name          | "ABC Petroleum Ltd" |
| source_url    | Finelib link          | "https://finelib.com/companies/abc-petroleum" |
| address       | Street address        | "123 Business District" |
| city          | City location         | "Lagos" |
| state         | State/Region          | "Lagos State" |
| phone         | Contact numbers       | "+234 800 000 0000" |
| website       | Company website       | "https://abcpetroleum.com" |
| email         | Contact email         | "info@abcpetroleum.com" |
| last_checked  | UTC timestamp         | "2024-01-15T10:30:00Z" |
| error         | Error message (optional) | "Timeout waiting for selector" |

## 🔧 Advanced Configuration

### Modify Timeouts
```python
await company_page.goto(..., timeout=30000)
```

### Add New Categories
```python\SEARCH_TERM = ["Agriculture", "Technology", "Real Estate", "Education"]
```

### Customize Output
Modify the `fieldnames` list in `write_csv_async()`.

## 🐛 Troubleshooting

### Common Issues

#### **"Target closed" errors**
- Reduce concurrency
- Increase timeouts

#### **Missing data fields**
- Finelib may have updated their structure
- Update your CSS selectors

#### **Duplicate entries**
- Ensure `companies.csv` was not manually edited
- Delete the file to reset tracking

#### **Playwright installation issues**
```bash
python -m playwright install --force
```

### Performance Tips
- Use fast/stable internet
- Avoid peak hours
- Add random delays for large datasets

## 🤝 Contributing
1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Push and submit a PR

## 📄 License
Licensed under **MIT**.

## ⚠️ Disclaimer
This tool is for educational and research purposes.
- Respect website terms
- Avoid overloading servers
- Use data responsibly

## 🆕 Version Information
- **Version:** 1.0.0
- **Python:** 3.8+
- **Last Updated:** January 2024

