# Wikipedia Dump Parser

A Python tool that processes Wikipedia XML dumps and cleans the content for further use without decompressing the dump file!

## Overview
This project processes Wikipedia XML dump files (.bz2) and extracts clean, readable text content. It handles the entire pipeline from parsing to cleaning without requiring manual decompression of the dump file.

## Features
- 🚀 Fast processing of Wikipedia XML dumps
- 🧹 Multi-stage content cleaning:
  - Removes wiki markup and references
  - Filters out image-related content
  - Cleans formatting and special characters
  - Removes non-article content
- 📊 Real-time processing statistics
- ⚡ Memory-efficient streaming processing
- 🔄 Handles articles of any length
- ⚙️ Configurable through config.txt
- 🗑️ Filters out redirects and non-article pages
- 💾 Outputs clean JSON format

## Requirements
- Python 3.8+
- NLTK
- mwparserfromhell

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Parkourer10/wikipedia-parser.git
cd wikipedia-parser
```


2. Install dependencies:

```bash
pip install -r requirements.txt
```


3. Configure the tool by editing the `config.txt` file: (IMPORTANT: Make sure the dump file is in the same directory as the script)
for example:
```bash
dump_path=enwiki.xml.bz2
output_path=wikipedia_processed.json
```


4. Run the tool:

```bash
python main.py
```


## Output

The tool will output a JSON file containing the processed Wikipedia content.
```json
{
    "title": "Title of the article",
    "text": "Processed content of the article"
}
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## TODO:
- [ ] Make it a package
- [ ] Add more features