import tkinter as tk
from tkinter import ttk

cinza_claro = '#c9c9c9'

#CLASSE PARA CONFIGURAÇÃO DO APP
class AppConfig():
    def __init__(self):
        #==Config da janela==#
        self.master = tk.Tk()
        self.master.title("app IC")
        self.master.geometry("1280x720")
        
    def SetFrames(self):
        self.topFrame = tk.Frame(self.master)
        self.topFrame.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.2)
        
        self.midFrame = tk.Frame(self.master)
        self.midFrame.place(relx=0.02, rely=0.2, relwidth=0.96, relheight=0.38)
        
        self.bottonFrame = tk.Frame(self.master)
        self.bottonFrame.place(relx=0.02, rely=0.58, relwidth=0.96, relheight=0.38)
        
        self.styleBtn = ttk.Style()
        self.styleBtn.map("btn1.TButton", 
                          foreground=[("disabled", "black"), 
                                      ("pressed", "white"), 
                                      ("active", "#878787")]) 
        
    def SetPots(self):
        self.textPotsLabel = tk.Label(self.topFrame, text="Insira os valores absolutos de potência máximos para cada fase do dispositivo", fg="#000000")
        self.textPotsLabel.grid(row=0, column=0, columnspan=5)
        
        self.potMALabel = tk.Label(self.topFrame, text="Pma =", fg="#000000")
        self.potMALabel.grid(row=1, column=0)
        
        self.potMAEntry = tk.Entry(self.topFrame)
        self.potMAEntry.grid(row=1, column=1)
        
        self.potMBLabel = tk.Label(self.topFrame, text="Pmb =", fg="#000000")
        self.potMBLabel.grid(row=1, column=2)
        
        self.potMBEntry = tk.Entry(self.topFrame)
        self.potMBEntry.grid(row=1, column=3)
        
        self.potMCLabel = tk.Label(self.topFrame, text="Pmc =", fg="#000000")
        self.potMCLabel.grid(row=1, column=4)
        
        self.potMCEntry = tk.Entry(self.topFrame)
        self.potMCEntry.grid(row=1, column=5)
        
    def SetUnbalance(self):
        self.calcDesesqButton = ttk.Button(self.midFrame,
                         text = 'Calcular Desequilíbrio',
                         style= "btn1.TButton",
                         command = ...)
        self.calcDesesqButton.grid(row=0, column=0)
        
        