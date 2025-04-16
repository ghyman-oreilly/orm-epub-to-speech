import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from markdownify import markdownify as md


def extract_epub_to_markdown(epub_path, output_file):
    """
    Process an EPUB file, extract content and headers, and save as markdown.
    Removes formatting elements like bold, italics, code blocks, figures, and tables.

    Args:
        epub_path: Path to the EPUB file
        output_file: Path to save the markdown output

    Returns:
        str: Path to the created markdown file
    """
    try:
        # Read the EPUB file
        book = epub.read_epub(epub_path, {"ignore_ncx": True})

        # Get book metadata
        title = book.get_metadata('DC', 'title')
        creator = book.get_metadata('DC', 'creator')

        # Start building markdown content
        markdown_content = []

        # Add book title and author if available
        if title:
            markdown_content.append(f"# {title[0][0]}\n")
        if creator:
            markdown_content.append(f"By {creator[0][0]}\n")

        # Process each document in the EPUB
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Get content as bytes and decode to string
                html_content = item.get_content().decode('utf-8')

                # Parse HTML with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                # section classes to retain
                chapter_level_section_classes = ['afterword', 'appendix', 'chapter', 'colophon','conclusion', 'foreword', 'introduction', 'preface', 'titlepage']

                # skip any chapter-level sections that we don't want to keep
                try:
                    if not soup.find("section").get('data-type') in chapter_level_section_classes:
                        continue
                except:
                    continue

                first_h1_found = False

                # promote all headings but the first (chapter title)
                for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    level = int(tag.name[1])

                    if tag.name == "h1" and not first_h1_found:
                        first_h1_found = True
                        continue  # Leave the first h1 untouched

                    if level < 6:
                        tag.name = f"h{level + 1}"  # Promote to the next level

                # Remove unwanted elements
                for element in soup(['script', 'style', 'table', 'figure', 'figcaption', 'pre']):
                    element.decompose()

                # Remove footnote paragraphs
                for element in soup.select('p[data-type="footnote"]'):
                    element.decompose()

                # Remove formatting tags but keep their content
                for tag in soup.find_all(['strong', 'b', 'em', 'i', 'code']):
                    tag.replace_with(tag.get_text())

                # Extract chapter title if available before converting to markdown
                chapter_title = soup.find(['h1', 'h2'])
                if chapter_title:
                    markdown_content.append(
                        f"\n## {chapter_title.get_text().strip()}\n")

                # Convert the HTML to markdown using markdownify library
                # Configure markdownify to skip certain conversions
                markdown_section = md(
                    str(soup),
                    heading_style="ATX",
                    strip=['a', 'img', 'code', 'pre',
                           'table', 'tr', 'td', 'th', 'blockquote']
                )

                # Ensure proper spacing between sections
                markdown_content.append(f"\n{markdown_section}\n\n")

        # Clean up excessive newlines and spaces
        final_content = re.sub(r'\n{3,}', '\n\n', ''.join(markdown_content))

        # Remove any remaining markdown formatting for bold and italic
        final_content = re.sub(r'\*\*|\*|__|\^|_', '', final_content)

        # Remove any remaining code blocks
        final_content = re.sub(
            r'```.*?```', '', final_content, flags=re.DOTALL)

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)

        return output_file

    except Exception as e:
        return f"Error processing EPUB: {str(e)}"