"""Import all packages"""

import tkinter as tk
from tkinter import filedialog
import threading
import re  # Regular expression module for splitting text into words
import fitz  # PyMuPDF, for reading PDF files
import docx  # python-docx, for reading DOCX files

class ReadingAssistant:
    """The entire reading assistant app in one class"""
    def __init__(self, master):
        # Initialize the main window
        self.master = master
        self.master.title("Speed Reading Assistant")

        # Set background color of the main window
        self.master.configure(bg='black')

        # Center the window on the screen
        window_width = 1400
        window_height = 700
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.master.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        # Top frame for completed label and upload button
        self.top_frame = tk.Frame(master, bg='black')
        self.top_frame.pack(fill=tk.X, padx=20, pady=20)

        # Percentage completed label, in the upper left side
        self.total_word_count = 0
        self.percentage_completed_label = tk.Label(self.top_frame, text="Completed:   0 %",
        fg="white", font=("Georgia Pro Semibold",12, "bold"), bg='black', )
        self.percentage_completed_label.pack(side=tk.LEFT)

        # Button to upload a document, in the upper right side
        self.load_text_button = tk.Button(self.top_frame, bg="lightgrey",
        text="Upload Document", command=self.load_text,)
        self.load_text_button.pack(side=tk.RIGHT, padx=(10, 10))  # Adjust padding as needed

        # Button to load text from clipboard, next to the upload document button
        self.load_clipboard_button = tk.Button(self.top_frame, bg="lightgrey", text="Clipboard",
        command=self.load_clipboard)
        self.load_clipboard_button.pack(side=tk.RIGHT, padx=(0, 0))  # Adjust padding as needed

        # Display label for showing words, centered
        self.label = tk.Label(master, text="", fg="white",
                              font=("Georgia", 40, "bold"), bg='black', width = 20, height = 2)
        self.label.config(text="Upload to Begin")
        self.label.pack(expand=True, padx = 10, pady = 10)  # This will center the label in the available space

        # Initialize variables for word display logic
        self.words = []  # List of words to display
        self.running = False  # Flag to control reading state
        self.current_word_index = 0  # Index of the current word being displayed
        self.word_delay = 0.42857  # Delay between words, adjustable by user

        # Calculate words per minute
        self.words_per_minute = int(60 / self.word_delay)

        # Binding buttons events to start and stop reading
        self.master.bind("<Right>", self.start_reading)
        self.master.bind("<KeyRelease-Right>", self.stop_reading)

        self.master.bind("<Return>", self.start_reading)
        self.master.bind("<Shift_R>", self.stop_reading)

        self.master.bind("<ButtonPress-3>", self.start_reading)
        self.master.bind("<ButtonRelease-3>", self.stop_reading)

        # Bottom frame for words per minute controls and rewind button
        self.bottom_frame = tk.Frame(master, bg='black')
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)

        # Frame for words per minute controls to keep them on the left side
        self.wpm_frame = tk.Frame(self.bottom_frame, bg='black')
        self.wpm_frame.pack(side=tk.LEFT, padx=(20, 10))

        # Buttons to adjust the words per minute, within the wpm frame
        self.increase_wpm_button = tk.Button(self.wpm_frame, text="Faster",
        bg="lightgrey", command=self.increase_wpm)
        self.increase_wpm_button.pack(side=tk.LEFT, padx=(0, 10))  # Pack within the frame
        self.decrease_wpm_button = tk.Button(self.wpm_frame, text="Slower",
        bg="lightgrey", command=self.decrease_wpm)
        self.decrease_wpm_button.pack(side=tk.LEFT, padx=(0, 0))  # Pack within the frame

        # Label to display the current words per minute, packed in the wpm frame
        self.wpm_value_label = tk.Label(self.wpm_frame, fg="white",
        text=f"Words per minute: {self.words_per_minute}", \
                                        font=("Georgia Pro Semibold", 12, "bold"), bg='black')
        self.wpm_value_label.pack(side=tk.LEFT, padx=(10, 10))

        # Rewind button on the right side of the bottom frame
        self.rewind_button = tk.Button(self.bottom_frame, text="Go Back",
        bg="lightgrey", command=self.rewind_one_word)
        self.master.bind("<Left>", lambda event: self.rewind_one_word())
        self.rewind_button.pack(side=tk.RIGHT, padx=(10, 20))  # Adjust padding as needed

    def clean_words(self, split_on_space=True):
        """Removes any unwanted characters from the imported files"""
        # Define a regular expression pattern that allows only specific special characters
        allowed_special_chars = r"[^a-zA-Z0-9,.\''!;\"“”\s]"
        cleaned_words = []
        for word in self.words:
            if split_on_space:
                # Replace disallowed special characters with space and split on space
                parts = re.sub(allowed_special_chars, ' ', word).split()
                cleaned_words.extend(parts)  # Extend the list by adding all parts as separate words
            else:
                # Replace disallowed special characters with space without splitting the word
                cleaned_word = re.sub(allowed_special_chars, ' ', word)
                cleaned_word = ' '.join(cleaned_word.split())  # Normalize spaces
                if cleaned_word:  # Add the word to the list if it's not empty after cleaning
                    cleaned_words.append(cleaned_word)
        self.words = cleaned_words

    def load_text(self):
        """Imports any file or documents to be read"""
        # Open a file dialog to select a document
        file_path = filedialog.askopenfilename()
        if file_path:
            # Load the document based on its file extension
            if file_path.endswith('.pdf'):
                self.words = self.read_pdf(file_path)
            elif file_path.endswith('.docx'):
                self.words = self.read_docx(file_path)
            else:  # Treat as a plain text file
                with open(file_path, "r", encoding="utf-8", errors='ignore') as file:
                    text = file.read()
                    self.words = text.split()
            self.clean_words()  # Clean the words list to remove special characters
        # Update the total word count after loading the document
        self.total_word_count = len(self.words)
        self.update_percentage_completed(0)  # Reset the percentage completed to 0
        # Display the first word as confirmation of successful upload
        if self.words:  # Check if the list of words is not empty
            self.label.config(text="Press Enter to start")
            self.current_word_index = 0  # Ensure to start from the beginning when reading starts
        else:
            self.label.config(text="File is Blank!")

    def load_clipboard(self):
        """Imports material to be read from the clipboard"""
        try:
            # Load text from the clipboard using Tkinter's clipboard_get()
            clipboard_text = self.master.clipboard_get()
            if clipboard_text:
                self.words = clipboard_text.split()
                self.clean_words()  # Clean the words list to remove special characters
                # Update the total word count after loading the text
                self.total_word_count = len(self.words)
                self.update_percentage_completed(0)  # Reset the percentage completed to 0
                if self.words:  # Check if the list of words is not empty
                    self.label.config(text="Press Enter to start")
                    self.current_word_index = 0  # Starts from the beginning when reading starts
                else:
                    self.label.config(text="Clipboard is Empty..")
            else:
                self.label.config(text="Clipboard is Empty...")
        except ImportError:
        # Handle any error that occurred while trying to access the clipboard
            self.label.config(text="Clipboard is Empty!")

    def read_docx(self, file_path):
        """Read DOCX file and return a list of words"""
        text = ""
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + " "
        return text.split()

    def read_pdf(self, file_path):
        """Read PDF file and return a list of words"""
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text.split()

    def increase_wpm(self):
        """Function to increase words per minute to read faster"""
        # Assuming a decrease in delay increases words per minute
        self.words_per_minute += 10  # Adjust the increment as needed
        self.word_delay = 60 / self.words_per_minute
        self.wpm_value_label.config(text=f"Words per minute: {self.words_per_minute}")

    def decrease_wpm(self):
        """Function to decrease words per minute to read slower"""
        # Assuming an increase in delay decreases words per minute
        self.words_per_minute -= 10  # Adjust the decrement as needed
        if self.words_per_minute < 10:  # Prevent words per minute from being too low
            self.words_per_minute = 10
        self.word_delay = 60 / self.words_per_minute
        self.wpm_value_label.config(text=f"Words per minute: {self.words_per_minute}")

    def display_words(self):
        """Function to display reading material in the GUI"""
        # Display words one at a time with adjustable delay
        if self.running and self.current_word_index < len(self.words):
            word = self.words[self.current_word_index]
            self.label.config(text=word)
            self.current_word_index += 1
            # Schedule the next call on the main thread
            self.master.after(int(self.word_delay * 1000), self.display_words)
        else:
            self.running = False

        # Update the percentage completed after displaying each word
        if self.total_word_count > 0:
            percentage_completed = (self.current_word_index / self.total_word_count) * 100
            self.update_percentage_completed(percentage_completed)

    def update_percentage_completed(self, percentage):
        """FUnction to update the 'Completed' label on the GUI"""
        # Update the percentage completed label
        self.percentage_completed_label.config()
        # Round the percentage to the nearest whole number
        rounded_percentage = round(percentage)
        # Update the percentage completed label with the rounded value
        self.percentage_completed_label.config(text=f"Completed: {rounded_percentage} %")

    def start_reading(self, event = None):
        """Function to change the displayed word in the GUI"""
        # Start displaying words
        if not self.running:
            self.running = True
            if self.current_word_index < len(self.words):
                threading.Thread(target=self.display_words).start()
            else:
                self.current_word_index = 0  # Reset to start if at the end

    def stop_reading(self, event): # DO NOT REMOVE! "event" is declared on line 99.
        """Function to stop changing the displayed word in the GUI"""
        # Stop displaying words
        self.running = False

    def rewind_one_word(self):
        """Function to go back by one word in the list of words"""
        # Check if we can rewind (current_word_index must be greater than 1 to rewind)
        if self.current_word_index > 1:
            self.current_word_index -= 2  # Go back by one word
            # Update the display immediately with the previous word
            self.label.config(text=self.words[self.current_word_index])
            self.current_word_index += 1  # Adjust index for the next display
        elif self.current_word_index == 1:  # If at the second word, go back to the first word
            self.current_word_index = 0
            self.label.config(text=self.words[self.current_word_index])
            self.current_word_index += 1  # Adjust index for the next display

def main():
    """Main function of the app"""
    # Create the main window and start the application
    root = tk.Tk()
    ReadingAssistant(root)
    root.mainloop()

if __name__ == "__main__":
    main()
