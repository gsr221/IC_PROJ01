from appConfig import AppConfig

if __name__ == '__main__':
    app = AppConfig()
    app.SetFrames()
    app.SetPots()
    app.SetUnbalance()
    app.SetBalance()
    app.master.mainloop()