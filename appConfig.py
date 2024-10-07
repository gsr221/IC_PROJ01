import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from appFunctions import AppFunctions as f

#CLASSE PARA CONFIGURAÇÃO DO APP
class AppConfig():
    def __init__(self):
        #==Config da janela==#
        self.master = tk.Tk()
        self.master.title("app IC")
        self.master.geometry("1280x720")
        self.styleBtn = ttk.Style()
        #==Config do estilo dos botões==#
        self.styleBtn.map("btn1.TButton", 
                          foreground=[("disabled", "black"), 
                                      ("pressed", "white"), 
                                      ("active", "#878787")])
        #==Objeto da classe AppFunctions==#
        self.f = f()
        
    def SetFrames(self):
        #==Frames==#
        self.topFrame = tk.LabelFrame(self.master, text="Insira os valores absolutos de potência máximos para cada fase do dispositivo")
        self.topFrame.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.07)
        
        self.midFrame = tk.LabelFrame(self.master)
        self.midFrame.place(relx=0.02, rely=0.09, relwidth=0.96, relheight=0.445)
        
        self.bottonFrame = tk.LabelFrame(self.master)
        self.bottonFrame.place(relx=0.02, rely=0.535, relwidth=0.96, relheight=0.445)
             
        
    def SetPots(self):
        #==Entradas de valores de potência máxima==#
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
        #==Visor das barras desequilibradas==#
        self.tvBarrasDeseq = ttk.Treeview(self.midFrame)
        self.tvBarrasDeseq.place(relx=0.01, rely=0.13, relwidth=0.98, relheight=0.82)
        
        #==Configurando o scroll no visor==#
        self.treescrolly1 = tk.Scrollbar(self.midFrame, orient="vertical", command=self.tvBarrasDeseq.yview)
        self.treescrollx1 = tk.Scrollbar(self.midFrame, orient="horizontal", command=self.tvBarrasDeseq.xview)
        self.tvBarrasDeseq.configure(xscrollcommand=self.treescrollx1.set, yscrollcommand=self.treescrolly1.set)
        self.treescrollx1.pack(side="bottom", fill='x')
        self.treescrolly1.pack(side="right", fill='y')
        
        #==Botão para visualizar barras desequilibradas==#
        self.calcDesesqButton = ttk.Button(self.midFrame,
                         text = 'Calcular Desequilíbrio',
                         style= "btn1.TButton",
                         command = lambda: self.f.calcDesqButtFun(self.tvBarrasDeseq))
        self.calcDesesqButton.place(relx=0.01, rely=0.02, height=25, width=150)
        
    def SetBalance(self):        
        #==Visor das barras possíveis de alocar dispositivo==#
        self.tvResultadoAg = ttk.Treeview(self.bottonFrame)
        self.tvResultadoAg.place(relx=0.01, rely=0.13, relwidth=0.49, relheight=0.82)
        
        #==Configurando o scroll no visor==#
        self.treescrolly2 = tk.Scrollbar(self.bottonFrame, orient="vertical", command=self.tvResultadoAg.yview)
        self.treescrollx2 = tk.Scrollbar(self.bottonFrame, orient="horizontal", command=self.tvResultadoAg.xview)
        self.tvResultadoAg.configure(xscrollcommand=self.treescrollx2.set, yscrollcommand=self.treescrolly2.set)
        self.treescrolly2.place(relx=0.49, rely=0.13, relwidth=0.01, relheight=0.81)
        self.treescrollx2.place(relx=0.01, rely=0.94, relwidth=0.49, relheight=0.06)
        
        #==Botão para executar o ag para equilibrar o sistema==#
        self.execAgButton = ttk.Button(self.bottonFrame,
                         text = 'Equilibrar',
                         style= "btn1.TButton",
                         command = lambda: self.f.equilButtFun(self.tvResultadoAg, self.potMAEntry, self.potMBEntry, self.potMCEntry))
        self.execAgButton.place(relx=0.01, rely=0.02, height=25, width=150)

        #==Visor dos dados de sequencia do sistema==#
        self.tvAloca = ttk.Treeview(self.bottonFrame)
        self.tvAloca.place(relx=0.51, rely=0.13, relwidth=0.49, relheight=0.82)

        #==Configurando o scroll no visor==#
        self.treescrolly3 = tk.Scrollbar(self.bottonFrame, orient="vertical", command=self.tvAloca.yview)
        self.treescrollx3 = tk.Scrollbar(self.bottonFrame, orient="horizontal", command=self.tvAloca.xview)
        self.tvAloca.configure(xscrollcommand=self.treescrollx3.set, yscrollcommand=self.treescrolly3.set)
        self.treescrolly3.place(relx=0.99, rely=0.13, relwidth=0.01, relheight=0.81)
        self.treescrollx3.place(relx=0.51, rely=0.94, relwidth=0.49, relheight=0.06)

        #==Campos para prencher potencias que serão alocadas e o barramento
        self.potALabel = tk.Label(self.bottonFrame, text='Pot A=', fg="#000000")
        self.potALabel.place(relx=0.64, rely=0.02, heigh=25, relwidth=0.03)
        self.potAEntry = tk.Entry(self.bottonFrame)
        self.potAEntry.place(relx=0.67, rely=0.02, heigh=20, relwidth=0.05)

        self.potBLabel = tk.Label(self.bottonFrame, text='Pot B=', fg="#000000")
        self.potBLabel.place(relx=0.72, rely=0.02, heigh=25, relwidth=0.03)
        self.potBEntry = tk.Entry(self.bottonFrame)
        self.potBEntry.place(relx=0.75, rely=0.02, heigh=20, relwidth=0.05)

        self.potCLabel = tk.Label(self.bottonFrame, text='Pot C=', fg="#000000")
        self.potCLabel.place(relx=0.80, rely=0.02, heigh=25, relwidth=0.03)
        self.potCEntry = tk.Entry(self.bottonFrame)
        self.potCEntry.place(relx=0.83, rely=0.02, heigh=20, relwidth=0.05)

        self.barraLabel = tk.Label(self.bottonFrame, text='Barra=', fg="#000000")
        self.barraLabel.place(relx=0.88, rely=0.02, heigh=25, relwidth=0.03)
        self.barraEntry = tk.Entry(self.bottonFrame)
        self.barraEntry.place(relx=0.91, rely=0.02, heigh=20, relwidth=0.05)

        #==Botão para alocar as potencias na barra desejada==#
        self.alocaButton = ttk.Button(self.bottonFrame,
                         text = 'Alocar',
                         style = 'btn1.TButton',
                         command = lambda: self.f.alocaButtFun(self.tvAloca, self.potAEntry, self.potBEntry, self.potCEntry, self.barraEntry))
        self.alocaButton.place(relx = 0.51, rely=0.02, heigh=25, width=150)