import urllib.request
import urllib.parse
import tkinter
import json

class App(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.address = tkinter.Entry(self)
        self.address.grid()
        self.send = tkinter.Button(self)
        self.send['text'] = 'Send'
        self.send['command'] = self.retrieve
        self.send.grid(row=0, column=1)
        self.output = tkinter.Text(self)
        self.output.grid(columnspan=2)

    def retrieve(self):
        val = {'app_secret': 'FCuf65iuOUDCjlbiyyer678Coutyc64v655478VGvgh76'}
        data = urllib.parse.urlencode(val).encode('utf8')
        result = urllib.request.urlopen(self.address.get(), data)
        result = json.loads(result.read().decode('utf8'))
        result = json.dumps(result, sort_keys=True,
                            indent=4, separators=(',', ': '))
        try:
            self.output.delete('1.0', tkinter.END)
        except Exception:
            pass
        self.output.insert(tkinter.END, result)


app = App()
app.master.title('ShnergleDevClient')
app.mainloop()
