import urllib.request
import urllib.parse
import tkinter as tk
import tkinter.ttk as ttk
import json

class App(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.grid()
        
    def init(self):        
        self.master.title('ShnergleDevClient')
        
        self.master.option_add('*tearOff', tk.FALSE)    
        menu = tk.Menu(self.master)
        menu_protocol = tk.Menu(menu)
        self.url_protocol = tk.StringVar()
        self.url_protocol.set('http')
        menu_protocol.add_radiobutton(label='HTTP', variable=self.url_protocol,
                                      value='http')
        menu_protocol.add_radiobutton(label='HTTPS',
                                      variable=self.url_protocol,
                                      value='https')
        menu_server = tk.Menu(menu)
        self.url_server = tk.StringVar()
        self.url_server.set('localhost')
        menu_server.add_radiobutton(label='shnergle-server.appspot.com',
                                    variable=self.url_server,
                                    value='shnergle-server.appspot.com')
        menu_server.add_radiobutton(label='localhost',variable=self.url_server,
                                    value='localhost')
        menu_port = tk.Menu(menu)
        self.url_port = tk.StringVar()
        self.url_port.set('8080')
        menu_port.add_radiobutton(label='80', variable=self.url_port,
                                  value='80')
        menu_port.add_radiobutton(label='443', variable=self.url_port,
                                  value='443')
        menu_port.add_radiobutton(label='8080', variable=self.url_port,
                                  value='8080')
        menu.add_cascade(menu=menu_protocol, label='Protocol')
        menu.add_cascade(menu=menu_server, label='Server')
        menu.add_cascade(menu=menu_port, label='Port')
        self.master['menu'] = menu
        
        self.url_method = tk.StringVar()
        ttk.Combobox(self, textvariable=self.url_method,
                     values=['users', 'user_searches']).grid()
        
        self.url_action = tk.StringVar()
        self.url_action.set('get')
        ttk.Radiobutton(self, text='get', variable=self.url_action,
                        value='get').grid(row=0, column=1)
        ttk.Radiobutton(self, text='set', variable=self.url_action,
                        value='set').grid(row=0, column=2)
        
        ttk.Button(self, text='Send', command=self.retrieve).grid(row=0,
                                                                  column=3)
        
        self.url_params = tk.StringVar()
        self.url_params.set('facebook_token=test')
        self.combo_params = ttk.Combobox(self, values=(),
                                         textvariable=self.url_params)
        self.combo_params.grid(columnspan=5, sticky='we')
                
        self.output = tk.Text(self, state='disabled')
        self.output.grid(columnspan=4, sticky='nswe')
        output_scroll_y = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                        command=self.output.yview)
        output_scroll_y.grid(row=2, column=4, sticky='ns')
        output_scroll_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL,
                                        command=self.output.xview)
        output_scroll_x.grid(columnspan=4, sticky='we')
        self.output.configure(xscrollcommand=output_scroll_x.set,
                              yscrollcommand=output_scroll_y.set)
        
        ttk.Sizegrip(self).grid(row=3, column=4, sticky='se')
        
        return self

    def retrieve(self):
        self.output['state'] = 'normal'
        if self.url_params.get() not in self.combo_params['values']:
            self.combo_params['values'] += (self.url_params.get(),)
        try:
            self.output.delete('1.0', tk.END)
        except Exception:
            pass
        
        result = urllib.request.urlopen(self.address, self.data)
        result = json.loads(result.read().decode('utf8'))
        result = json.dumps(result, sort_keys=True,
                            indent=4, separators=(',', ': '))
        
        self.output.insert(tk.END, result)
        self.output['state'] = 'disabled'
        
    @property
    def address(self):
        return (self.url_protocol.get() + '://' + self.url_server.get() + ':' +
                self.url_port.get() + '/' + self.url_method.get() + '/' +
                self.url_action.get())

    @property
    def data(self):
        defs = {'app_secret': 'FCuf65iuOUDCjlbiyyer678Coutyc64v655478VGvgh76'}
        res = {}
        for pair in self.url_params.get().split('&'):
            item = pair.split('=')
            res[item[0]] = item[1]
        res.update(defs)
        return urllib.parse.urlencode(res).encode('utf8')


if __name__ == '__main__':
    App().init().mainloop()
