import os
import re
import time
from openai import OpenAI
import markdown
from bs4 import BeautifulSoup
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


def convert_markdown_to_speech(markdown_file, output_dir, voice='alloy', split_at_subheadings=False):
    """
    Convert markdown content to speech using OpenAI's Text-to-Speech API.

    Args:
        markdown_file: Path to the markdown file
        output_dir: Directory to save the audio files
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)

    Returns:
        List of lists of tuples:
        - Each nested list represents a section
        - Each tuple is as: (chunk_index, file_basename, output_filename)
    """
    try:
        # Read markdown file
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Split markdown into sections (chapters or major headings)
        sections = split_into_sections(markdown_content, split_at_subheadings)

        # Initialize OpenAI client
        client = OpenAI()

        # Instructions for model
        instructions = """
            Do not read aloud any of the following characters: #, *, _

            Do not read aloud a backslash if it immediately precedes any of the following characters: #, *, _

            Do not read aloud any HTML comments (wrapped in <!-- and -->).
            """

        output = []

        # Process each section
        for section_ix, (title, content) in enumerate(sections):

            section_audio = []
            
            # Clean the filename
            safe_title = re.sub(r'[^\w\s-]', '', title.lower())
            safe_title = re.sub(r'[\s]+', '_', safe_title)

            file_basename = f"{section_ix+1:02d}_{safe_title[:30]}"
            
            # chunk the content, to stay below char limit
            chunked_content = split_content_into_chunks(content)

            for chunk_ix, chunk in enumerate(chunked_content):
                print(f"Processing section {section_ix + 1} of {len(sections)} (chunk {chunk_ix + 1} of {len(chunked_content)})...")

                # Generate speech
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=chunk,
                    instructions=instructions
                )

                # Create a filename for this chunk
                filename = f"{(
                    f'{file_basename}.mp3' if len(chunked_content) == 1 
                    else f'{file_basename}_pt{chunk_ix:02}.mp3'
                )}"
                output_path = os.path.join(output_dir, filename)

                # Skip if file already exists
                if os.path.exists(output_path):
                    print(f"Skipping existing file: {output_path}")
                    continue

                # Save to file
                response.stream_to_file(output_path)

                section_audio.append((chunk_ix, file_basename, output_path))

                # Sleep to avoid hitting API rate limits
                time.sleep(1)
            
            output.append(section_audio)

        return output

    except Exception as e:
        return f"Error converting to speech: {str(e)}"


def split_into_sections(markdown_content, split_at_subheadings=False):
    """
    Split markdown content into sections based on headings.

    Args:
        markdown_content: The markdown content

    Returns:
        list: List of tuples (section_title, section_content)
    """
    # Convert markdown to HTML
    html = markdown.markdown(markdown_content)
    soup = BeautifulSoup(html, 'html.parser')

    # Find heading elements
    if split_at_subheadings:
        headings = soup.find_all(['h1', 'h2'])
    else:
        headings = soup.find_all(['h1'])
    
    sections = []

    # If no headings, return the entire content as one section
    if not headings:
        return [("Content", markdown_content)]

    # Add content before the first heading as "Intro"
    intro_parts = []
    for element in soup.contents:
        if element == headings[0]:
            break
        if getattr(element, 'name', None) or isinstance(element, str):
            text = element.get_text() if hasattr(element, 'get_text') else str(element)
            if text.strip():
                intro_parts.append(text.strip() + "\n\n")
    if intro_parts:
        sections.append(("Intro", ''.join(intro_parts)))

    # Process each heading as a section
    for i, heading in enumerate(headings):
        title = heading.get_text()
        content_parts = []

        # Add the heading text first
        content_parts.append(f"{title}\n\n")

        # Get all content until the next heading
        element = heading.next_sibling
        while element and (i == len(headings) - 1 or element != headings[i + 1]):
            content_parts.append(element.get_text() + "\n\n")

            # Move to next element
            if hasattr(element, 'next_sibling'):
                element = element.next_sibling
            else:
                break

        content = ''.join(content_parts)
        sections.append((title, content))

    return sections


def split_content_into_chunks(content, max_chars=4096):
    """
    Chunk string of content to ensure we
    remain below character limit but retain all content.
    """
    sentences = content.split('. ')
    chunks = []
    current_chunk = ""

    for i, sentence in enumerate(sentences):
        # Reattach the ". " (unless it's the very last sentence)
        if i < len(sentences) - 1:
            sentence += ". "

        if len(current_chunk) + len(sentence) > max_chars:
            # Save the current chunk and start a new one
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks