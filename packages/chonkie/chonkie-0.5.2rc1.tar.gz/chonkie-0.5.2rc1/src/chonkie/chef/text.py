"""A Chef for handling text files."""

import re

from chonkie.chef.base import BaseChef
from chonkie.chef.patterns import ABBREVIATIONS, UnicodeReplacements


class TextChef(BaseChef):

    """A chef that handles basic text processing.

    This chef handles basic text files and performs common text cleaning operations
    like removing extra whitespace, normalizing line endings, etc.
    """

    def __init__(
        self,
        whitespace: bool = True,
        newlines: bool = True,
        abbreviations: bool = True,
        ellipsis: bool = True,
        mid_sentence_newlines: bool = False,
        decimals: bool = True,
        email: bool = True,
        url: bool = True,
        sentence_endings: str = ".!?;:",
    ) -> None:
        """Initialize the TextChef with common text file extensions."""
        extensions = [".txt", ".md", ".rst", ".text"]
        super().__init__(extensions=extensions)

        # Initialize the flags
        self._enable_whitespace = whitespace
        self._enable_newlines = newlines
        self._enable_mid_sentence_newlines = mid_sentence_newlines
        self._enable_abbreviations = abbreviations
        self._enable_ellipsis = ellipsis
        self._enable_decimal_points = decimals
        self._enable_email = email
        self._enable_url = url

        # Initialize the sentence endings
        self._sentence_endings = sentence_endings

        # Initialize the patterns
        self._dot = "."
        self._abbreviations = ABBREVIATIONS if abbreviations else set()
        self._unicode_replacements = UnicodeReplacements()

        # Compiling the regex patterns
        self._ellipsis_pattern = re.compile(r"\.{3,}")
        self._paragraph_pattern = re.compile(r"\n{2,}")
        self._decimal_pattern = re.compile(r'(?<=\d)\.(?=\d)')  # matches only the dot between any two digits
        self._email_pattern = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
        self._url_pattern = re.compile(r'\b(?:https?://|www\.)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\S*\b')

    def _handle_abbreviations(self, text: str) -> str:
        """Replace the fullstop in abbreviations with a dot leader."""
        sorted_abbreviations = sorted(self._abbreviations, key=len, reverse=True)   # processing the abbreviation based on their length
        for abbreviation in sorted_abbreviations:
            # Only match the abbreviations that are surrounded by word boundary at beginning and a non-word character at end
            pattern = re.compile(r"\b" + re.escape(abbreviation) + r"(?=\W)")
            new_abbreviation = abbreviation.replace(
                ".", self._unicode_replacements.DOT_LEADER
            )
            text = pattern.sub(new_abbreviation, text)
        return text

    def _replace_ellipsis(self, text: str) -> str:
        """Replace ellipsis with Unicode ellipsis character.

        Args:
            text: Input text

        Returns:
            Text with ellipsis replaced

        """
        # Replace any sequence of 3 or more dots with ellipsis character
        return self._ellipsis_pattern.sub(self._unicode_replacements.ELLIPSIS, text)
    
    def _replace_decimal_points(self, text: str) -> str:
        """Replace the DOT with the DOT LEADER at places where there is a decimal point.
        
        Args:
            text: Input text
            
        Returns:
            Text with replaced decimal points
            
        """
        # Replace any decimal point between two digits with a dot leader
        return self._decimal_pattern.sub(self._unicode_replacements.DOT_LEADER, text)
    
    def _replace_emails(self, text: str) -> str:
        """Replace the DOT in an email with the DOT LEADER.
        
        Args:
            text: Input text
            
        Returns:
            Text with replaced DOTs in emails
        
        """
        # Match all the emails
        email_matches = self._email_pattern.findall(text)
        for email_match in email_matches:
            # Replace the dots with the dot leaders
            modified = email_match.replace(self._dot, self._unicode_replacements.DOT_LEADER)
            text = text.replace(email_match, modified)  # change the occurrences
        
        return text
    
    def _replace_urls(self, text: str) -> str:
        """Replace the DOT in an URL with the DOT LEADER.
        
        Args:
            text: Input text
            
        Returns:
            Text with replaced DOTs in URLs
        
        """
        # Match all the URLs in the given text
        url_matches = self._url_pattern.findall(text)
        for url_match in url_matches:
            # Replace the dots with the dot leaders
            modified = url_match.replace(self._dot, self._unicode_replacements.DOT_LEADER)
            text = text.replace(url_match, modified)    # change the occurrences
            
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text.

        Args:
            text: Input text

        Returns:
            Text with normalized whitespace

        """
        # Replace multiple spaces with single space
        text = " ".join([s for s in text.split(" ") if s])
        return text

    def _normalize_newlines(self, text: str) -> str:
        """Normalize newlines in text.

        Args:
            text: Input text

        Returns:
            Text with normalized newlines

        """
        # Normalize newlines
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Normalize more than one newline as double newlines
        text = self._paragraph_pattern.sub("\n\n", text)

        return text

    def _handle_mid_sentence_newlines(self, text: str) -> str:
        """Handle mid-sentence newlines while preserving paragraph breaks.

        This function distinguishes between line wrapping and paragraph breaks:
        - Multiple newlines (2+) indicate paragraph breaks and are preserved
        - Single newlines within sentences are converted to spaces
        - Newlines after sentence endings start new lines

        Args:
            text: Input text

        Returns:
            Text with line wrapping handled but paragraph breaks preserved

        """
        # Split into paragraphs (2+ newlines)
        paragraphs = text.split("\n\n")
        processed_paragraphs = []

        for paragraph in paragraphs:
            if not paragraph.strip():
                continue

            # Split paragraph into lines
            lines = paragraph.split("\n")
            result = []
            current_line = ""

            for line in lines:
                stripped_line = line.strip()
                if not stripped_line:
                    continue

                # If we have a current line and it doesn't end with sentence ending punctuation
                # and the current line isn't starting with dialog markers or special punctuation
                if (
                    current_line
                    and not any(
                        current_line.rstrip().endswith(end)
                        for end in self._sentence_endings
                    )
                    and not any(
                        stripped_line.startswith(p)
                        for p in ['"', '"', """, """, "-", "—"]
                    )
                ):
                    current_line = f"{current_line} {stripped_line}"
                else:
                    if current_line:
                        result.append(current_line)
                    current_line = stripped_line

            if current_line:
                result.append(current_line)

            # Join the lines in this paragraph
            processed_paragraphs.append("\n".join(result))

        # Join paragraphs with double newlines
        return "\n\n".join(processed_paragraphs)

    def clean(self, text: str) -> str:
        """Clean the text by performing basic text processing operations.

        A common function where one can enable/disable the operations supported by the chef.

        Args:
            text: The text to clean.

        Returns:
            The cleaned text.

        """
        if not text:
            return text

        # Normalize whitespace
        if self._enable_whitespace:
            text = self._normalize_whitespace(text)

        # Handle mid-sentence newlines
        if self._enable_mid_sentence_newlines:
            text = self._handle_mid_sentence_newlines(text)

        # Normalize newlines
        if self._enable_newlines:
            text = self._normalize_newlines(text)

        # Replace ellipsis
        if self._enable_ellipsis:
            text = self._replace_ellipsis(text)

        # Replace abbreviations
        if self._enable_abbreviations:
            text = self._handle_abbreviations(text)
            
        # Replace decimal points
        if self._enable_decimal_points:
            text = self._replace_decimal_points(text)

        # Replace the dots in emails
        if self._enable_email:
            text = self._replace_emails(text)
            
        # Replace the dots in URLs
        if self._enable_url:
            text = self._replace_urls(text)

        return text
    
    def revert(self, text: str) -> str:
        """Revert back the DOT LEADERS and ELLIPSIS replacing DOTs.
        
        Args:
            text: The text to revert.

        Returns:
            The reverted text.
        
        """
        return text.replace(self._unicode_replacements.ELLIPSIS, "...").replace(self._unicode_replacements.DOT_LEADER, ".")
