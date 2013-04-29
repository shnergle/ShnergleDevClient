import json
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import urllib.error
import urllib.parse
import urllib.request


class App(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.grid(sticky='nswe')

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
        menu_port.add_radiobutton(label='Default', variable=self.url_port,
                                  value='')
        menu_port.add_separator()
        menu_port.add_radiobutton(label='80', variable=self.url_port,
                                  value='80')
        menu_port.add_radiobutton(label='443', variable=self.url_port,
                                  value='443')
        menu_port.add_radiobutton(label='8080', variable=self.url_port,
                                  value='8080')
        menu_clear_history = tk.Menu(menu)
        menu_clear_history.add_command(label='Facebook Token',
                                       command=self.clear_history_facebook)
        menu_clear_history.add_command(label='Other Parameters',
                                      command=self.clear_history_params)
        menu_clear_history.add_command(label='Image',
                                       command=self.clear_history_image)
        menu_clear_history.add_separator()
        menu_clear_history.add_command(label='All',
                                       command=self.clear_history)
        menu.add_cascade(menu=menu_protocol, label='Protocol')
        menu.add_cascade(menu=menu_server, label='Server')
        menu.add_cascade(menu=menu_port, label='Port')
        menu.add_cascade(menu=menu_clear_history, label='Clear History')
        self.master['menu'] = menu

        main_bar = ttk.Frame(self)

        self.url_method = tk.StringVar()
        ttk.Combobox(main_bar, textvariable=self.url_method,
                     values=['users', 'user_searches']).grid(sticky='nswe')

        self.url_action = tk.StringVar()
        self.url_action.set('get')
        ttk.Radiobutton(main_bar, text='get', variable=self.url_action,
                        value='get').grid(row=0, column=1)
        ttk.Radiobutton(main_bar, text='set', variable=self.url_action,
                        value='set').grid(row=0, column=2)

        ttk.Button(main_bar, text='Send', command=self.retrieve).grid(row=0,
                                                                      column=3)

        main_bar.grid(columnspan=4, sticky='nswe')
        main_bar.columnconfigure(0, weight=1)

        ttk.Label(self, text='Facebook Token:').grid()
        self.post_facebook = tk.StringVar()
        self.post_facebook.set('test')
        self.combo_facebook = ttk.Combobox(self,
                                           textvariable=self.post_facebook)
        self.combo_facebook.grid(row=1, column=1, columnspan=2, sticky='we')
        ttk.Button(self, text='Clear', command=self.clear_facebook).grid(
            row=1, column=3)

        ttk.Label(self, text='Other Parameters:').grid()
        self.post_params = tk.StringVar()
        self.post_params.set('key=value&variable=content')
        self.combo_params = ttk.Combobox(self, textvariable=self.post_params)
        self.combo_params.grid(row=2, column=1, columnspan=2, sticky='we')
        ttk.Button(self, text='Clear', command=self.clear_params).grid(
            row=2, column=3)

        ttk.Label(self, text='Image:').grid()
        self.post_image = tk.StringVar()
        self.combo_image = ttk.Combobox(self, textvariable=self.post_image)
        self.combo_image.grid(row=3, column=1, sticky='we')
        ttk.Button(self, text='Browse', command=self.browse_image).grid(
            row=3, column=2)
        ttk.Button(self, text='Clear', command=self.clear_image).grid(
            row=3, column=3)

        self.output = tk.Text(self, state='disabled')
        self.output.grid(columnspan=4, sticky='nswe')
        output_scroll_y = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                        command=self.output.yview)
        output_scroll_y.grid(row=4, column=4, sticky='ns')
        output_scroll_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL,
                                        command=self.output.xview)
        output_scroll_x.grid(columnspan=4, sticky='we')
        self.output.configure(xscrollcommand=output_scroll_x.set,
                              yscrollcommand=output_scroll_y.set)

        ttk.Sizegrip(self).grid(row=5, column=4, sticky='se')

        self.winfo_toplevel().rowconfigure(0, weight=1)
        self.winfo_toplevel().columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)
        self.columnconfigure(1, weight=1)

        return self

    def retrieve(self):
        self.output['state'] = 'normal'

        for combo in (self.combo_facebook, self.combo_params,
                      self.combo_image):
            combo_params = []
            combo_params.append(combo.get())
            for item in combo['values']:
                if item and item != combo.get():
                    combo_params.append(item)
            combo['values'] = combo_params

        try:
            self.output.delete('1.0', tk.END)
        except Exception:
            pass

        result = ''
        try:
            result = urllib.request.urlopen(self.address, self.data)
            result = self.pretty_print(result.read().decode('utf8'))
        except urllib.error.URLError as e:
            if hasattr(e, 'read'):
                result = self.pretty_print(e.read().decode('utf8'))
            else:
                result = e
        except Exception as e:
            result = e
        self.output.insert(tk.END, result)

        self.output['state'] = 'disabled'

    @property
    def address(self):
        return (self.url_protocol.get() + '://' + self.url_server.get() +
                (':' + self.url_port.get() if self.url_port.get() else '') +
                '/' + self.url_method.get() + '/' + self.url_action.get())

    @property
    def data(self):
        res = dict(i.split('=') for i in self.post_params.get().split('&'))
        res['app_secret'] = 'FCuf65iuOUDCjlbiyyer678Coutyc64v655478VGvgh76'
        if self.post_facebook.get():
            res['facebook_token'] = self.post_facebook.get()
        if self.post_image.get():
            pass
            #TODO: send image to server
        return urllib.parse.urlencode(res).encode('utf8')

    def pretty_print(self, jsonstr):
        return json.dumps(json.loads(jsonstr), sort_keys=True,
                          indent=4, separators=(',', ': '))

    def clear_facebook(self):
        self.post_facebook.set('')

    def clear_params(self):
        self.post_params.set('')

    def clear_image(self):
        self.post_image.set('')

    def clear_history(self):
        self.clear_history_facebook()
        self.clear_history_params()
        self.clear_history_image()

    def clear_history_facebook(self):
        self.combo_facebook['values'] = ()

    def clear_history_params(self):
        self.combo_params['values'] = ()

    def clear_history_image(self):
        self.combo_image['values'] = ()

    def browse_image(self):
        self.post_image.set(filedialog.askopenfilename())


if __name__ == '__main__':
    App().init().mainloop()
