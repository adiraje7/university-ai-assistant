import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import PyPDF2

import os
import subprocess
import shutil
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from component import PDFProcessor, PDFDelete, WebScraping, WebDelete, MyDatabase

load_dotenv()

qdrant_host = os.getenv('QDRANT_HOST')
qdrant_api_key = os.getenv('QDRANT_API_KEY')

UPLOAD_FOLDER = '../Project_AI_assistant/pdf' 
collection_name = 'university_collection'
# Create the main window


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Assistant Database management")
        self.root.geometry("900x450")
        # Create a side menu frame
        self.side_menu = tk.Frame(root, width=200, bg='#3D3B40', relief='raised')
        self.side_menu.pack(side='left', fill='y')

        # Add buttons to the side menu
        self.add_side_menu_button("Home", self.homepage_button)
        self.add_side_menu_button("Database", self.mydatabase_button)
        self.add_side_menu_button("Management", self.management_button)
        self.add_side_menu_button("Help", self.help_button)
        self.add_side_menu_button("Exit", root.quit)

        # Create a simple label in the main area
        self.main_area = tk.Frame(root, bg='#F8EDFF')
        self.main_area.pack(side='right', fill='both', expand=True)
        self.label = tk.Label(self.main_area, text="Welcome to AI Assistant Database Management!", font=('Times New Roman', 25, 'bold'))
        self.label.place(relx = 0.2, rely = 0.2)

    def add_side_menu_button(self, text, command):
        button = tk.Button(self.side_menu, text=text, command=command, relief='flat',bg='#525CEB',fg="white", activebackground='#F8EDFF', activeforeground="black", pady=5, padx=5)
        button.pack(fill='x', pady=20,padx=5)

    def reset(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        
    def homepage_button(self):
        self.reset()
        Homepage(self.main_area)
    
    def mydatabase_button(self):
        self.reset()
        Databasepage(self.main_area)
    
    def management_button(self):
        self.reset()
        Managementpage(self.main_area)
    
    def help_button(self):
        messagebox.showinfo("About", "This is a simple Tkinter app with a side menu bar")

class Homepage:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg='#F8EDFF')
        self.frame.pack(fill='both', expand=True)

        self.label = tk.Label(self.frame, text="Welcome to AI Assistant Database Management!", font=('Times New Roman', 25, 'bold'))
        self.label.place(relx = 0.2, rely = 0.2)

class Databasepage:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg='#F8EDFF')
        self.frame.pack(fill='both', expand=True)

        list_items = tk.Variable(value=['collection1','collection2'])
        listbox = tk.Listbox(
            self.frame,
            height=5,
            listvariable=list_items
        )
        listbox.place(x=50,y=50)



class Managementpage:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg='#F8EDFF')
        self.frame.pack(fill='both', expand=True)
        self.pdf_upload_button = tk.Button(self.frame, text='Upload File', command=self.upload_file, width=10,height=2)
        self.pdf_delete_button = tk.Button(self.frame, text='Delete File', command= self.delete_file, width=10,height=2)
        self.web_upload_button = tk.Button(self.frame, text='Upload Web', command=self.scrap_web)
        self.web_delete_button = tk.Button(self.frame, text='Delete Web', command= self.delete_web)
        self.web_input = tk.Entry(self.frame, bg="lightblue", width=50)
        self.pdf_label = tk.Label(self.frame, text='PDF Management', bg= '#F8EDFF',font=('Times New Roman', 18, 'bold'))
        self.web_label = tk.Label(self.frame, text='WEB Management', bg= '#F8EDFF',font=('Times New Roman', 18, 'bold'))
        self.status_label = tk.Label(self.frame, text='',bg='black',fg='white',width=30,height=10)

        self.pdf_label.place(x=20,y=20)
        self.pdf_upload_button.place(x=20,y=80)
        self.pdf_delete_button.place(x=150,y=80)

        self.web_label.place(x=20,y=210)
        self.web_upload_button.place(x=20,y=300)
        self.web_delete_button.place(x=100,y=300)
        self.web_input.place(x=20,y=270)
        self.status_label.place(x=450,y=150)

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            filename = os.path.basename(file_path)
            if filename.lower().endswith('.pdf'):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                destination = os.path.join(UPLOAD_FOLDER, filename)
                shutil.copy(file_path, destination)
                #directory = '../Project_AI_assistant/pdf'
                processor = PDFProcessor(collection_name=collection_name)
                processor.process_file(file_path,filename)
                self.status_label.config(text=f'File {filename} uploaded successfully!')
            else:
                self.status_label.config(text='Selected file is not a PDF!')

    def delete_file(self):
        file_path = filedialog.askopenfilename(initialdir=UPLOAD_FOLDER,filetypes=[("PDF files", "*.pdf")])
        if os.path.exists(file_path):
            
            filename = os.path.basename(file_path)
            directory = os.path.dirname(file_path)
            if(filename in os.listdir(directory)): #change this code
                os.remove(file_path)
                file_deleted = PDFDelete(collection_name=collection_name)
                file_deleted.delete_pdf(filename)
                self.status_label.config(text=f'File {filename} deleted successfully!')
            else:
                self.status_label.config(text=f'File {filename} is not in a valid path')

    def scrap_web(self):
        url = self.web_input.get()
        try:
            response = requests.get(url)
            print(response)
            if response.status_code == 200:
                # Parse the content of the page with Beautiful Soup
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract all text from the page
                all_text = soup.get_text()
                scrapingweb = WebScraping(collection_name=collection_name)
                print(scrapingweb.search_data(collection_name,"web",url)[0])
                if(scrapingweb.search_data(collection_name,"web",url)[0]!=[]):
                    self.status_label.config(text=f"Web already scraped and in the database")
                else:
                    scrapingweb.scrape_text_from_page(all_text,url)
                    self.status_label.config(text=f"Succesful to retrieve the page. Scrap: {response.status_code}")
            else:
                self.status_label.config(text=f"Failed to retrieve the page. Status code: {response.status_code}")
        except:
            self.status_label.config(text=f"Invalid URL")
        # Check if the request was successful

    def delete_web(self):
        url = self.web_input.get()
        deleteWeb = WebDelete(collection_name=collection_name, url=url)

        try:
            print(deleteWeb.search_data(collection_name,"web",url)[0])
            if(deleteWeb.search_data(collection_name,"web",url)[0]==[]):
                self.status_label.config(text=f"No such weblink in the database")
            else:
                deleteWeb.delete_web()
                self.status_label.config(text=f"Succesful to delete web database with url: {url}")
        except:
            self.status_label.config(text=f"Cannot detect weblink in database or url invalid")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
# root = tk.Tk()
# root.title('AI Assistant Database Management')

# root.geometry("800x450")
# # Create and place a button for file upload
# tk.Label(text="Data Management For AI Assistant (Qdrant)",font=('Times New Roman', 25, 'bold')).grid(column=0,row=0,columnspan=10)
# #file_entry = tk.Entry(root, width = 50, bg='lightblue')
# #file_entry.grid(row=2, column=0,columnspan = 3,pady=20,padx=20)

# statusbar = tk.Frame(root, background="#e3e3e3",width=800, height=50)

# statusbar.grid(row=10,column=0,columnspan=10)


# pdf_frame = tk.Frame(root, background="#99ceff",width=350, height=150).grid(row=1,column=0,rowspan=3,columnspan=3)
# web_frame = tk.Frame(root, background="#ffe6cd",width=350, height=150).grid(row=4,column=0,rowspan=3,columnspan=3)
# terminal_frame = tk.Frame(root, background="black",width=450, height=300).grid(row=1,column=4,rowspan=6)
# upload_button = tk.Button(pdf_frame, text='Upload PDF File', command=upload_file)
# delete_button = tk.Button(pdf_frame, text='Delete File', command= delete_file)

# tk.Label(pdf_frame,text="Pdf Manager").grid(row=1,column=0,columnspan=3)
# upload_button.grid(row=2,column=0,columnspan=3)
# delete_button.grid(row=3,column=0,columnspan=3)


# web_input = tk.Entry(web_frame, bg="lightblue", width=50)
# scrap_button = tk.Button(web_frame, text='Scrap Web', command=scrap_web)
# delweb_button = tk.Button(web_frame, text='Delete Web Data', command=delete_web)

# tk.Label(web_frame,text="Web Scraping Manager").grid(row=4,column=0)
# web_input.grid(row = 5, column=0,columnspan=3)
# scrap_button.grid(row = 6, column=0)
# delweb_button.grid(row = 6, column=1)


# # # Create and place a label for status messages
# status_label = tk.Label(root, text='',bg='black',fg='white',width=60,height=10)
# #tk.Label(terminal_frame, text="Terminal").grid(row=1,column=4,pady=10,padx=10)
# status_label.grid(row=1, column=4, columnspan=10, rowspan=6, pady=10, padx=10)


# # Run the application
# root.mainloop()