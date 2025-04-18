# ORM EPUB to Speech Converter

Modified script based on Chris Bremseth's awesome [epub-to-speech script](https://github.com/cbremseth/epub-to-speech). 

This tool allows you to extract content from EPUB files and convert it to speech using OpenAI's Text-to-Speech API. This version has some modifications that make it suitable for the ORM/HTMLBook use case.

## Features

- Extract content and headers from EPUB files and save as Markdown
- Convert Markdown content to speech files using OpenAI's TTS API
- Process EPUBs to speech in a single command
- Customizable voice selection
- Support for large files by chunking them and then reassembling the resulting audio
- Suitable for HTMLBook specifically: Only chapter-level sections with specific data-types are retained ('chapter', 'preface', etc.)
- Headings after the first in a chapter are promoted, to keep chapter content together

## Installation

### Requirements

- Python 3.7+
- OpenAI API key
- ffmpeg or libav (used by pydub to edit/combine the MP3s)

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

4. Install [ffmpeg](https://www.ffmpeg.org) or libav on your system. On mac, you can use brew to install ffmpeg:

```bash
brew install ffmpeg
```


## Usage

The tool provides a command-line interface with three main commands:

### 1. Extract content from an EPUB file

```bash
python main.py extract path/to/book.epub --output book.md
```

Options:
- `--output`, `-o`: Output markdown filename (default: same as input with .md extension)
- `--replace-stripped-elements-with-comments', '-c'`: When stripping out unwanted elements from the EPUB HTML (e.g., images, pre blocks, etc.), insert a comment where the elements have been removed.

### 2. Convert a Markdown file to speech

```bash
python main.py speak path/to/file.md --output-dir ./audio_files --voice nova
```

Options:
- `--output-dir`, `-o`: Directory for audio output files (default: ./audio_output)
- `--voice`, `-v`: Voice to use (options: alloy, echo, fable, onyx, nova, shimmer)
- `--split-at-subheadings`, `-s`: Split audio files by subheadings (all H1 and H2) instead of the default of chapter-level audio files (H1)

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
- ffmpeg or libav (non-python dependency): Crossplatform multimedia framework

## Limitations

- OpenAI's TTS API has a 4096 character limit per request, so long sections are split
- API rate limits may apply when processing large books
- Some EPUB formatting may not translate perfectly to Markdown
