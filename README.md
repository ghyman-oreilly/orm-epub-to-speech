# EPUB to Speech Converter

This tool allows you to extract content from EPUB files and convert it to speech using OpenAI's Text-to-Speech API.

## Features

- Extract content and headers from EPUB files and save as Markdown
- Convert Markdown content to speech files using OpenAI's TTS API
- Process EPUBs to speech in a single command
- Customizable voice selection
- Support for large files by splitting content into manageable sections

## Installation

### Requirements

- Python 3.7+
- OpenAI API key

### Setup

1. Clone the repository or download the source files:

```bash
git clone https://github.com/cbremseth/epub-to-speech.git
cd epub-to-speech
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory to store your OpenAI API key:

```bash
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

## Usage

The tool provides a command-line interface with three main commands:

### 1. Extract content from an EPUB file

```bash
python main.py extract path/to/book.epub --output book.md
```

Options:
- `--output`, `-o`: Output markdown filename (default: same as input with .md extension)

### 2. Convert a Markdown file to speech

```bash
python main.py speak path/to/file.md --output-dir ./audio_files --voice nova
```

Options:
- `--output-dir`, `-o`: Directory for audio output files (default: ./audio_output)
- `--voice`, `-v`: Voice to use (options: alloy, echo, fable, onyx, nova, shimmer)

### 3. Process an EPUB file to speech in one step

```bash
python main.py process path/to/book.epub --output-dir ./audio_files --voice alloy --keep-markdown
```

Options:
- `--output-dir`, `-o`: Directory for audio output files (default: ./audio_output)
- `--voice`, `-v`: Voice to use (options: alloy, echo, fable, onyx, nova, shimmer)
- `--keep-markdown`, `-k`: Keep the intermediate markdown file (default: removed after processing)

## Example

```bash
# Process "The Great Gatsby" to audio files with the "nova" voice
python main.py process books/great_gatsby.epub --output-dir ./gatsby_audio --voice nova --keep-markdown
```

## File Structure

- `main.py`: Command-line interface using Click
- `epub_processor.py`: EPUB to Markdown conversion functions
- `speech_generator.py`: Markdown to speech conversion using OpenAI API
- `requirements.txt`: List of required Python packages

## Dependencies

- click: Command-line interface creation
- ebooklib: EPUB file processing
- beautifulsoup4: HTML parsing
- markdown: Markdown processing
- openai: OpenAI API client
- python-dotenv: Environment variable management

## Limitations

- OpenAI's TTS API has a 4096 character limit per request, so long sections are split
- API rate limits may apply when processing large books
- Some EPUB formatting may not translate perfectly to Markdown
