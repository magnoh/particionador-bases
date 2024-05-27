import os
import time
import pandas as pd
import customtkinter 
import tkinter as tk

from tkinter import filedialog
from tkinter import messagebox
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(BASE_DIR, 'atualizar-pares-de-setas-em-circulo.png')

class Window:

    def __init__(self) -> None:
        self.app = customtkinter.CTk()
        self.app.geometry('560x480')
        self.app.title('Separador de Bases')
        self.app.resizable(0, 0)

        self.app.columnconfigure(0, weight=1)
        self.app.rowconfigure(3, weight=1)

        self.first_frame = customtkinter.CTkFrame(self.app)
        self.first_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='nsew')

        refresh_logo = customtkinter.CTkImage(
            light_image=Image.open(image_path),
            size=(30,30)
        )
        
        self.button_refresh = customtkinter.CTkButton(
            self.first_frame,
            command=self.reset_window,  
            width=60, 
            height=40,
            text='',
            image=refresh_logo,
        )
        self.button_refresh.grid(row=0, column=1, sticky='e')

        self.textbox = customtkinter.CTkTextbox(
            self.first_frame, 
            width=370, 
            height=0, 
            fg_color='white', 
            text_color='black'
        )
        self.textbox.grid(row=1, column=0, pady=20, padx=10)

        self.button = customtkinter.CTkButton(
            self.first_frame, 
            text="Selecionar arquivo", 
            command=self.select_file 
        ).grid(row=1, column=1, pady=20)
 
        self.textbox2 = customtkinter.CTkTextbox(
            self.first_frame, width=370, 
            height=0, 
            fg_color='white', 
            text_color='black'
        )
        self.textbox2.grid(row=2, column=0, pady=20, padx=10)

        self.output_path = None

        self.select_output_button = customtkinter.CTkButton(
            self.first_frame, 
            text="Salvar em", 
            command=self.select_output_directory
        ).grid(row=2, column=1, pady=20)

        self.chunksize_label = customtkinter.CTkLabel(
            self.first_frame, 
            text='Quantidade de Partes:'
        ).grid(row=3, column=0, padx=10, stick='e')

        self.chunksize_entry = customtkinter.CTkEntry(
            self.first_frame
        )
        self.chunksize_entry.grid(row=3, column=1, pady=20, stick='s')
        self.chunksize_entry.bind('<KeyRelease>', self.calculate_rows_per_base)

        self.total_rows = customtkinter.StringVar()
        self.total_rows_label = customtkinter.CTkLabel(
            self.first_frame, 
            textvariable=self.total_rows, 
            text_color='green',
            font=('Arial', 18)
        ).grid(row=4, column=0)

        self.total_rows_por_base = customtkinter.StringVar(self.first_frame)
        self.total_rows_por_base_label = customtkinter.CTkLabel(
            self.first_frame, 
            textvariable=self.total_rows_por_base, 
            text_color='green', 
            font=('Arial', 18)
        ).grid(row=5, column=0)

        self.second_frame = customtkinter.CTkFrame(self.app)
        self.second_frame.grid(row=1, column=0, padx=10, pady=(0, 10), rowspan=4,sticky="nsew")
        
        self.button_separar_base = customtkinter.CTkButton(
            self.second_frame, text="Separar base", 
            command=self.separate_base
        ).grid(row=0, column=0, pady=50, padx=85)

        self.button_sair = customtkinter.CTkButton(
            self.second_frame, 
            command=self.app.destroy, 
            text="Sair"
        ).grid(row=0, column=1, padx=30)

        self.app.mainloop()
    
    def reset_window(self):
        self.output_path = None  
        self.chunksize_entry.delete(0, customtkinter.END)
        self.textbox.configure(state='normal')
        self.textbox.delete(0.0, customtkinter.END)
        if self.textbox2:
            self.textbox2.configure(state='normal')
            self.textbox2.delete('0.0', customtkinter.END)
        self.total_rows.set('')
        self.total_rows_por_base.set('')

    def select_output_directory(self):
        self.output_path = filedialog.askdirectory()
        if self.textbox2:
            self.textbox2.insert('0.0', self.output_path)
            self.textbox2.configure(state='disabled')

    def select_file(self):
        self.textbox.delete('0.0', customtkinter.END)

        self.filename = filedialog.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=(
                ("CSV Files","*.csv"),
                ('text files', '*.txt')
            )
        )
        self.textbox.insert('0.0', self.filename)
        self.textbox.configure(state='disable')

        self.df = pd.read_csv(self.filename, encoding='latin1')

        self.total_rows.set(f'Total de linhas encontradas: {self.df.shape[0]:,}')
    
    def calculate_rows_per_base(self, event):
        try:
            self.total_rows_por_base.set('')

            chunksize = self.chunksize_entry.get()
            total_rows = self.total_rows.get()

            self.total_rows_int = int(''.join(filter(str.isdigit, total_rows)))

            if int(chunksize) > 0 and self.total_rows_int > 0:
                result = self.total_rows_int / int(chunksize)
                self.total_rows_por_base.set(f'Quantidade de linhas por base: {int(result):,}')
        except:
            pass
        
    def separate_base(self):
        if self.output_path is None:
            self.show_error_message("Por favor, selecione a pasta de destino.")
            return
        try:
            num_parts = int(self.chunksize_entry.get())
        except ValueError:
            self.show_error_message("Número de partes inválido. Por favor, insira um número inteiro válido.")
            return
        
        chunksize = self.total_rows_int // num_parts

        progressbar = customtkinter.CTkProgressBar(
            self.second_frame, 
            mode='determinate', 
            width=400, 
            height=20
        )
        progressbar.grid(row=1, columnspan=3)

        output_name = os.path.splitext(os.path.basename(self.filename))[0]

        index = 1

        delimiter = self.getDelimitador(self.filename)

        for chunk in pd.read_csv(self.filename, delimiter=delimiter, encoding='latin1', chunksize=chunksize):
            output = f'{self.output_path}/{output_name}{index}.csv'
            chunk.to_csv(output, sep=';' ,encoding='latin1' ,index=False)
            index += 1

            progress = min((index / num_parts) * 100, 100)
            progressbar['value'] = progress
            self.app.update_idletasks()

        self.reset_window()      
        progressbar.destroy()
        self.show_info_message("Processo concluído com sucesso.")
        

    def show_error_message(self, message):
        messagebox.showerror("Erro", message)

    def show_info_message(self, message):
        messagebox.showinfo("Informação", message)

    def getDelimitador(self, diretorio):

        with open(diretorio, 'r') as file:

            header = file.readline()

            if header.find(";") != -1:
                separador = ";"
                
            elif header.find("\t") != -1:
                separador = "\t"

            elif header.find(",") != -1:
                separador = ","

        return separador


Window()