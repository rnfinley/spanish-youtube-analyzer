# Spanish YouTube Word Analyzer 🇪🇸

A web application that extracts Spanish transcripts from YouTube videos and analyzes word frequency to help Spanish learners identify the most common vocabulary.

## Features

- Extract Spanish transcripts from any YouTube video with Spanish captions
- Count and display word frequency
- Show top 100 most frequent words
- Support for Spanish special characters (á, é, í, ó, ú, ñ, ü)
- Clean, responsive web interface
- Helpful error messages when Spanish captions aren't available

## Installation

1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/spanish-youtube-analyzer.git
cd spanish-youtube-analyzer
```

2. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:

```bash
python app.py
```

2. Open your browser to `http://127.0.0.1:5000`

3. Paste a YouTube URL with Spanish content

4. Click "Analyze Video" to see word frequencies

## Requirements

- Python 3.7+
- Flask
- youtube-transcript-api

## Project Structure

```
├── app.py              # Flask backend
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Frontend interface
└── static/
    └── style.css      # Styling
```

## Future Features

- [ ] Export word lists to CSV/Anki format
- [ ] Filter common words (articles, prepositions)
- [ ] Show words in context
- [ ] Support for analyzing multiple videos
- [ ] Add translations and pronunciation guides

## Contributing

Feel free to open issues or submit pull requests!

## License

MIT License
