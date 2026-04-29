import json
import random
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


HISTORY_FILE = Path("quote_history.json")

QUOTES = [
    {
        "text": "The only way to do great work is to love what you do.",
        "author": "Steve Jobs",
        "topic": "Motivation",
    },
    {
        "text": "Life is what happens when you're busy making other plans.",
        "author": "John Lennon",
        "topic": "Life",
    },
    {
        "text": "It always seems impossible until it's done.",
        "author": "Nelson Mandela",
        "topic": "Persistence",
    },
    {
        "text": "Knowledge is power.",
        "author": "Francis Bacon",
        "topic": "Knowledge",
    },
    {
        "text": "Stay hungry, stay foolish.",
        "author": "Steve Jobs",
        "topic": "Motivation",
    },
    {
        "text": "To be yourself in a world that is constantly trying to make you something else is the greatest accomplishment.",
        "author": "Ralph Waldo Emerson",
        "topic": "Life",
    },
]


class QuoteGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("820x620")
        self.root.minsize(720, 560)

        self.quotes = QUOTES.copy()
        self.history = self.load_history()

        self.author_filter = tk.StringVar(value="All")
        self.topic_filter = tk.StringVar(value="All")
        self.new_text = tk.StringVar()
        self.new_author = tk.StringVar()
        self.new_topic = tk.StringVar()

        self.create_widgets()
        self.refresh_filters()
        self.refresh_history()

    def create_widgets(self):
        main = ttk.Frame(self.root, padding=16)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)

        title = ttk.Label(main, text="Random Quote Generator", font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, sticky="w")

        quote_frame = ttk.LabelFrame(main, text="Current quote", padding=12)
        quote_frame.grid(row=1, column=0, sticky="ew", pady=(14, 10))
        quote_frame.columnconfigure(0, weight=1)

        self.quote_label = ttk.Label(
            quote_frame,
            text="Click the button to generate a quote.",
            font=("Segoe UI", 13),
            wraplength=740,
            justify=tk.LEFT,
        )
        self.quote_label.grid(row=0, column=0, sticky="ew")

        self.meta_label = ttk.Label(quote_frame, text="", font=("Segoe UI", 10, "italic"))
        self.meta_label.grid(row=1, column=0, sticky="w", pady=(8, 0))

        controls = ttk.Frame(quote_frame)
        controls.grid(row=2, column=0, sticky="ew", pady=(12, 0))

        ttk.Button(controls, text="Generate quote", command=self.generate_quote).pack(side=tk.LEFT)
        ttk.Button(controls, text="Save history", command=self.save_history).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(controls, text="Clear history", command=self.clear_history).pack(side=tk.LEFT, padx=(8, 0))

        content = ttk.Frame(main)
        content.grid(row=2, column=0, sticky="nsew")
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        history_frame = ttk.LabelFrame(content, text="Generated quotes history", padding=12)
        history_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(1, weight=1)

        filters = ttk.Frame(history_frame)
        filters.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(filters, text="Author:").pack(side=tk.LEFT)
        self.author_combo = ttk.Combobox(
            filters,
            textvariable=self.author_filter,
            state="readonly",
            width=18,
        )
        self.author_combo.pack(side=tk.LEFT, padx=(6, 12))
        self.author_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_history())

        ttk.Label(filters, text="Topic:").pack(side=tk.LEFT)
        self.topic_combo = ttk.Combobox(
            filters,
            textvariable=self.topic_filter,
            state="readonly",
            width=18,
        )
        self.topic_combo.pack(side=tk.LEFT, padx=(6, 12))
        self.topic_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_history())

        ttk.Button(filters, text="Reset filters", command=self.reset_filters).pack(side=tk.LEFT)

        self.history_list = tk.Listbox(history_frame, height=14)
        self.history_list.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_list.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.history_list.configure(yscrollcommand=scrollbar.set)

        add_frame = ttk.LabelFrame(content, text="Add a new quote", padding=12)
        add_frame.grid(row=0, column=1, sticky="nsew")
        add_frame.columnconfigure(0, weight=1)

        ttk.Label(add_frame, text="Quote text").grid(row=0, column=0, sticky="w")
        ttk.Entry(add_frame, textvariable=self.new_text).grid(row=1, column=0, sticky="ew", pady=(4, 10))

        ttk.Label(add_frame, text="Author").grid(row=2, column=0, sticky="w")
        ttk.Entry(add_frame, textvariable=self.new_author).grid(row=3, column=0, sticky="ew", pady=(4, 10))

        ttk.Label(add_frame, text="Topic").grid(row=4, column=0, sticky="w")
        ttk.Entry(add_frame, textvariable=self.new_topic).grid(row=5, column=0, sticky="ew", pady=(4, 12))

        ttk.Button(add_frame, text="Add quote", command=self.add_quote).grid(row=6, column=0, sticky="ew")

        hint = (
            "New quotes are available immediately for generation and filtering. "
            "Empty fields are rejected."
        )
        ttk.Label(add_frame, text=hint, wraplength=240, foreground="#555555").grid(
            row=7, column=0, sticky="ew", pady=(12, 0)
        )

    def generate_quote(self):
        quote = random.choice(self.quotes)
        self.history.insert(0, quote.copy())
        self.show_quote(quote)
        self.refresh_history()
        self.save_history(show_message=False)

    def show_quote(self, quote):
        self.quote_label.configure(text=f'"{quote["text"]}"')
        self.meta_label.configure(text=f'{quote["author"]} - {quote["topic"]}')

    def add_quote(self):
        text = self.new_text.get().strip()
        author = self.new_author.get().strip()
        topic = self.new_topic.get().strip()

        if not text or not author or not topic:
            messagebox.showwarning("Validation error", "Please fill in quote text, author, and topic.")
            return

        self.quotes.append({"text": text, "author": author, "topic": topic})
        self.new_text.set("")
        self.new_author.set("")
        self.new_topic.set("")
        self.refresh_filters()
        messagebox.showinfo("Quote added", "The quote was added successfully.")

    def refresh_filters(self):
        authors = ["All"] + sorted({quote["author"] for quote in self.quotes + self.history})
        topics = ["All"] + sorted({quote["topic"] for quote in self.quotes + self.history})

        self.author_combo["values"] = authors
        self.topic_combo["values"] = topics

        if self.author_filter.get() not in authors:
            self.author_filter.set("All")
        if self.topic_filter.get() not in topics:
            self.topic_filter.set("All")

    def refresh_history(self):
        self.history_list.delete(0, tk.END)

        for quote in self.filtered_history():
            self.history_list.insert(
                tk.END,
                f'{quote["author"]} [{quote["topic"]}]: {quote["text"]}',
            )

    def filtered_history(self):
        author = self.author_filter.get()
        topic = self.topic_filter.get()

        result = self.history
        if author != "All":
            result = [quote for quote in result if quote["author"] == author]
        if topic != "All":
            result = [quote for quote in result if quote["topic"] == topic]
        return result

    def reset_filters(self):
        self.author_filter.set("All")
        self.topic_filter.set("All")
        self.refresh_history()

    def save_history(self, show_message=True):
        try:
            HISTORY_FILE.write_text(
                json.dumps(self.history, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            messagebox.showerror("Save error", f"Could not save history: {exc}")
            return

        if show_message:
            messagebox.showinfo("History saved", f"History saved to {HISTORY_FILE}.")

    def load_history(self):
        if not HISTORY_FILE.exists():
            return []

        try:
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            messagebox.showwarning("Load warning", "History file is damaged or unavailable.")
            return []

        valid_history = []
        for item in data:
            if all(key in item and str(item[key]).strip() for key in ("text", "author", "topic")):
                valid_history.append(
                    {
                        "text": str(item["text"]).strip(),
                        "author": str(item["author"]).strip(),
                        "topic": str(item["topic"]).strip(),
                    }
                )
        return valid_history

    def clear_history(self):
        if not self.history:
            return

        confirmed = messagebox.askyesno("Clear history", "Delete all generated quote history?")
        if not confirmed:
            return

        self.history.clear()
        self.refresh_history()
        self.save_history(show_message=False)


def main():
    root = tk.Tk()
    app = QuoteGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
