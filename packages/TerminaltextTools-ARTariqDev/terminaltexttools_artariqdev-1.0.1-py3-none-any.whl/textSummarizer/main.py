import argparse
import openai
import os
import chardet
import re
from docx import Document
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, TextArea, Input
from textual.containers import Vertical
from textual.binding import Binding
from rich.text import Text
from rich.style import Style
import asyncio
from textual.screen import Screen
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv('Key')
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)  # Use Async API Client

async def get_summary(text, detail="medium"):
    """Send text to GPT-4o for summarization asynchronously"""
    prompt = "Summarize the following text. Shorten it without losing key information."
    
    if any(keyword in text for keyword in ["def ", "import ", "class ", "function", "console.log", "#include"]):
        prompt = "Summarize the following code. Explain what it does in a concise way."

    if detail == "short":
        prompt += " Keep it very short."
    elif detail == "detailed":
        prompt += " Provide a detailed summary."

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}]
    )
    return response.choices[0].message.content  

class TextSummarizerApp(App):
    """Textual app with async summarization, word count, and search"""

    BINDINGS = [
        Binding("s", "summarize", "Summarize"),
        Binding("q", "quit", "Quit"),
        Binding("w", "word_count", "Word Count"),
        Binding("f", "search", "Find"),
        Binding("n", "next_match", "Next Match"),
    ]

    def __init__(self, file_path, detail="medium"):
        super().__init__()
        self.file_path = file_path
        self.detail = detail
        self.content = ""
        self.search_term = ""
        self.search_positions = []
        self.current_search_index = -1

    def compose(self) -> ComposeResult:
        """Render UI"""
        yield Header()
        try:
            # Added error handling for file reading with encoding detection
            if self.file_path:
                with open(self.file_path, "rb") as f:
                    raw_data = f.read()
                    encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
                
                with open(self.file_path, "r", encoding=encoding) as f:
                    self.content = f.read()
                
                self.text_display = TextArea(self.content[:300], disabled=True)
                yield Vertical(Label(f"📄 File: {self.file_path}"), self.text_display)
            else:
                yield Vertical(Label("⚠️ No file specified"))
        except Exception as e:
            yield Vertical(Label(f"⚠️ Error: {str(e)}"))
        yield Footer()

    async def action_summarize(self):
        """Handle summarization asynchronously"""
        if not self.content:
            self.notify("⚠️ No content to summarize", title="Error")
            return
            
        self.text_display.load_text("⏳ Summarizing...")

        try:
            summary = await get_summary(self.content, self.detail)  # Await async call
            self.text_display.load_text(summary)
        except Exception as e:
            self.text_display.load_text(f"⚠️ Error: {str(e)}")

    def action_word_count(self):
        """Count words in the displayed text"""
        if not self.content:
            self.notify("No content to count", title="Word Count")
            return
            
        word_count = len(self.content.split())
        char_count = len(self.content)
        lines = self.content.count('\n') + 1
        
        self.notify(f"Words: {word_count} | Characters: {char_count} | Lines: {lines}", title="Word Count")

    def action_search(self):
        """Search for a term in the text"""
        if not self.content:
            self.notify("No content to search", title="Search")
            return
            
        self.push_screen(SearchScreen(self))

    def action_next_match(self):
        """Navigate to the next search match"""
        if self.search_positions:
            self.highlight_search_term()
        elif self.search_term:
            self.notify(f"No matches found for '{self.search_term}'", title="Search")
        else:
            self.action_search()

    def highlight_search_term(self):
        """Highlight the search term in the text area"""
        if not self.search_term or not self.search_positions:
            self.notify(f"No matches found for '{self.search_term}'", title="Search")
            return

        # Cycle through occurrences
        self.current_search_index = (self.current_search_index + 1) % len(self.search_positions)
        start, end = self.search_positions[self.current_search_index]
        
        # Update footer with search info
        self.query_one(Footer).renderable = Text(
            f"Match {self.current_search_index + 1} of {len(self.search_positions)} for '{self.search_term}'"
        )

        # Create highlighted text with context
        context_range = 150  # Characters to show before and after match
        
        context_start = max(0, start - context_range)
        context_end = min(len(self.content), end + context_range)
        

        highlighted_text = (
            self.content[context_start:start] + 
            "✳️ " + self.content[start:end] + "✳️" + 
            self.content[end:context_end]
        )
        
        # Load the text with markup
        self.text_display.load_text(highlighted_text)
        

class SearchScreen(Screen):
    """Search term input screen"""

    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app

    def compose(self):
        yield Header()
        yield Label("🔍 Enter search term:")
        self.search_input = Input(value=self.parent_app.search_term)
        yield self.search_input
        yield Footer()

    def on_mount(self):
        self.search_input.focus()

    def key_enter(self):
        """Handle Enter key press for search"""
        self.submit_search()

    def on_input_submitted(self):
        """Handle input submission"""
        self.submit_search()

    def submit_search(self):
        """Process search submission"""
        search_term = self.search_input.value.strip()
        if search_term:
            self.parent_app.search_term = search_term
            self.parent_app.search_positions = [
                (m.start(), m.end()) for m in re.finditer(re.escape(search_term), self.parent_app.content, re.IGNORECASE)
            ]
            self.parent_app.current_search_index = -1  # Reset to -1 so first highlight_search_term call shows first match
            
            # Dismiss screen
            self.app.pop_screen()
            
            if self.parent_app.search_positions:
                self.parent_app.highlight_search_term()
            else:
                self.parent_app.notify(f"No matches found for '{search_term}'", title="Search")
        else:
            self.app.pop_screen()

def main():
    """Main function for CLI execution"""
    parser = argparse.ArgumentParser(description="Summarize text & code files using GPT-3.5")
    parser.add_argument("file_path", type=str, nargs="?", help="Path to the text file")
    parser.add_argument("--detail", choices=["short", "medium", "detailed"], default="medium", help="Summary length")
    
    args = parser.parse_args()

    app = TextSummarizerApp(args.file_path, args.detail)
    app.run()

if __name__ == "__main__":
    main()