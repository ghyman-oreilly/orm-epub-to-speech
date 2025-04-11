import os
import re
import time
from openai import OpenAI
import markdown
from bs4 import BeautifulSoup
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


def convert_markdown_to_speech(markdown_file, output_dir, voice='alloy'):
    """
    Convert markdown content to speech using OpenAI's Text-to-Speech API.

    Args:
        markdown_file: Path to the markdown file
        output_dir: Directory to save the audio files
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)

    Returns:
        str: Output directory path
    """
    try:
        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Read markdown file
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Split markdown into sections (chapters or major headings)
        sections = split_into_sections(markdown_content)

        # Initialize OpenAI client
        client = OpenAI()

        # Base filename from original markdown
        base_filename = os.path.splitext(os.path.basename(markdown_file))[0]

        # Process each section
        for i, (title, content) in enumerate(sections):
            # Clean the filename
            safe_title = re.sub(r'[^\w\s-]', '', title.lower())
            safe_title = re.sub(r'[\s]+', '_', safe_title)

            # Create a filename for this section
            filename = f"{i+1:02d}_{safe_title[:30]}.mp3"
            output_path = os.path.join(output_dir, filename)

            # Skip if file already exists
            if os.path.exists(output_path):
                print(f"Skipping existing file: {output_path}")
                continue

            # Limit content length
            if len(content) > 4096:
                print(
                    f"Warning: Section {i+1} is too long, truncating to 4096 characters")
                content = content[:4096]

            # Generate speech
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=content
            )

            # Save to file
            response.stream_to_file(output_path)

            print(f"Created: {output_path}")

            # Sleep to avoid hitting API rate limits
            time.sleep(1)

        return output_dir

    except Exception as e:
        return f"Error converting to speech: {str(e)}"


def split_into_sections(markdown_content, max_words=800):
    """
    Split markdown content into manageable sections based on headings.

    Args:
        markdown_content: The markdown content
        max_words: Maximum words per section

    Returns:
        list: List of tuples (section_title, section_content)
    """
    # Convert markdown to HTML
    html = markdown.markdown(markdown_content)
    soup = BeautifulSoup(html, 'html.parser')

    # Find all heading elements
    headings = soup.find_all(['h1', 'h2', 'h3'])
    sections = []

    # If no headings, return the entire content as one section
    if not headings:
        return [("Content", markdown_content)]

    # Process each heading as a section
    for i, heading in enumerate(headings):
        title = heading.get_text()
        content_parts = []

        # Add the heading text first
        content_parts.append(f"{title}\n\n")

        # Get all content until the next heading
        element = heading.next_sibling
        while element and (i == len(headings) - 1 or element != headings[i + 1]):
            if element.name and element.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                content_parts.append(element.get_text() + "\n\n")
            elif isinstance(element, str) and element.strip():
                content_parts.append(element + "\n\n")

            # Move to next element
            if hasattr(element, 'next_sibling'):
                element = element.next_sibling
            else:
                break

        content = ''.join(content_parts)

        # If content is too long, split it further
        words = content.split()
        if len(words) > max_words:
            # Split content into chunks of max_words
            chunks = [' '.join(words[i:i+max_words])
                      for i in range(0, len(words), max_words)]
            for j, chunk in enumerate(chunks):
                chunk_title = f"{title} (Part {j+1})"
                sections.append((chunk_title, chunk))
        else:
            sections.append((title, content))

    return sections
