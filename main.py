from appConfig import AppConfig as ac

if __name__ == '__main__':
    app = ac()
    app.SetFrames()
    app.SetPots()
    app.SetUnbalance()
    app.master.mainloop()