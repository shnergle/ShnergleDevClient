import json
import threading
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import urllib.error
import urllib.parse
import urllib.request


class JSONText(tk.Text):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag_configure('number', foreground='#009999')
        self.tag_configure('boolean', font='bold')
        self.tag_configure('string', foreground='#dd1144')
        self.tag_configure('keystring', foreground='#000080')
        
    def highlight(self):
        self.set_tags('(0|[1-9])[0-9]*(\.[0-9]*)?', 'number')
        self.set_tags('(true|false|null)', 'boolean')
        self.set_tags('"[^":]*"', 'string')
        self.set_tags('"[^":]*"(?=\:)', 'keystring')
        
    def set_tags(self, pattern, tag):
        start = self.index('1.0')
        self.mark_set('matchStart', start)
        self.mark_set('matchEnd', start)
        self.mark_set('searchLimit', self.index('end'))
        count = tk.IntVar()
        while True:
            index = self.search(pattern, 'matchEnd', 'searchLimit',
                                count=count, regexp=True)
            if not index:
                break
            self.mark_set('matchStart', index)
            self.mark_set('matchEnd', '{}+{}c'.format(index, count.get()))
            self.tag_add(tag, 'matchStart', 'matchEnd')


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
        self.url_protocol.set('https')
        menu_protocol.add_radiobutton(label='HTTP', variable=self.url_protocol,
                                      value='http')
        menu_protocol.add_radiobutton(label='HTTPS',
                                      variable=self.url_protocol,
                                      value='https')

        menu_server = tk.Menu(menu)
        self.url_server = tk.StringVar()
        self.url_server.set('shnergle-api.azurewebsites.net')
        menu_server.add_radiobutton(label='shnergle-api.azurewebsites.net',
                                    variable=self.url_server,
                                    value='shnergle-api.azurewebsites.net')
        menu_server.add_radiobutton(label='localhost',
                                    variable=self.url_server,
                                    value='localhost')

        menu_port = tk.Menu(menu)
        self.url_port = tk.StringVar()
        self.url_port.set('default')
        menu_port.add_radiobutton(label='Default', variable=self.url_port,
                                  value='default')
        menu_port.add_separator()
        menu_port.add_radiobutton(label='80', variable=self.url_port,
                                  value='80')
        menu_port.add_radiobutton(label='443', variable=self.url_port,
                                  value='443')
        menu_port.add_radiobutton(label='8080', variable=self.url_port,
                                  value='8080')
                                  
        menu_version = tk.Menu(menu)
        self.url_version = tk.StringVar()
        self.url_version.set('latest')
        menu_version.add_radiobutton(label='Latest', variable=self.url_version,
                                     value='latest')
        menu_version.add_separator()
        menu_version.add_radiobutton(label='1', variable=self.url_version,
                                     value='v1')
                                  
        menu_wrap = tk.Menu(menu)
        self.wrap_mode = tk.StringVar()
        self.wrap_mode.set('none')
        menu_wrap.add_radiobutton(label='None', variable=self.wrap_mode,
                                  value='none', command=self.set_wrap)
        menu_wrap.add_radiobutton(label='Character', variable=self.wrap_mode,
                                  value='char', command=self.set_wrap)
        menu_wrap.add_radiobutton(label='Word', variable=self.wrap_mode,
                                  value='word', command=self.set_wrap)

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
        menu.add_cascade(menu=menu_version, label='API Version')
        menu.add_cascade(menu=menu_wrap, label='Editor Wrap')
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

        editor = ttk.Frame(self)

        self.output = JSONText(editor, state='disabled')
        self.output.grid(sticky='nswe')
        output_scroll_y = ttk.Scrollbar(editor, orient=tk.VERTICAL,
                                        command=self.output.yview)
        output_scroll_y.grid(row=0, column=1, sticky='ns')
        output_scroll_x = ttk.Scrollbar(editor, orient=tk.HORIZONTAL,
                                        command=self.output.xview)
        output_scroll_x.grid(sticky='we')
        self.output.configure(xscrollcommand=output_scroll_x.set,
                              yscrollcommand=output_scroll_y.set,
                              wrap=self.wrap_mode.get())

        ttk.Sizegrip(editor).grid(row=1, column=1, sticky='se')

        editor.rowconfigure(0, weight=1)
        editor.columnconfigure(0, weight=1)
        editor.grid(columnspan=4, sticky='nswe')

        self.winfo_toplevel().rowconfigure(0, weight=1)
        self.winfo_toplevel().columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)
        self.columnconfigure(1, weight=1)

        return self

    def retrieve(self):
        self.dialog = tk.Toplevel(self)
        self.dialog.resizable(tk.FALSE, tk.FALSE)
        self.dialog.title('Loading...')
        progress = ttk.Progressbar(self.dialog, orient=tk.HORIZONTAL,
                                   length=250, mode='indeterminate')
        progress.pack()
        progress.start()
        RetrievalThread(self).start()

    @property
    def address(self):
        port = ''
        if self.url_port.get() != 'default':
            port = ':' + self.url_port.get()
        version = ''
        if self.url_version.get() != 'latest':
            version = '/v' + self.url_version.get()
        return (self.url_protocol.get() + '://' + self.url_server.get() +
                port + version + '/' + self.url_method.get() + '/' +
                self.url_action.get())

    @property
    def data(self):
        res = dict(i.split('=') for i in self.post_params.get().split('&'))
        res['app_secret'] = 'FCuf65iuOUDCjlbiyyer678Coutyc64v655478VGvgh76'
        if self.post_facebook.get():
            res['facebook_token'] = self.post_facebook.get()
        if self.post_image.get():
            res['image'] = open(self.post_image.get())
        return urllib.parse.urlencode(res).encode('utf8')

    def escape(self, jsonstr):
        jsonstr = jsonstr.replace('\\n', '\n')
        jsonstr = jsonstr.replace('\\"', "'")
        jsonstr = jsonstr.replace('\\\\', '\\')
        return jsonstr
        
    def pretty_print(self, jsonstr):
        try:
            return self.escape(json.dumps(json.loads(jsonstr), sort_keys=True,
                                          indent=4, separators=(',', ': ')))
        except Exception:
            return jsonstr

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
        
    def set_wrap(self):
        self.output['wrap'] = self.wrap_mode.get()


class RetrievalThread(threading.Thread):

    def __init__(self, main):
        super().__init__()
        self.main = main

    def run(self):
        self.main.output['state'] = 'normal'

        for combo in (self.main.combo_facebook, self.main.combo_params,
                      self.main.combo_image):
            combo_params = []
            combo_params.append(combo.get())
            for item in combo['values']:
                if item and item != combo.get():
                    combo_params.append(item)
            combo['values'] = combo_params

        try:
            self.main.output.delete('1.0', tk.END)
        except Exception:
            pass

        result = ''
        try:
            result = urllib.request.urlopen(self.main.address, self.main.data)
            result = self.main.pretty_print(result.read().decode('utf8'))
        except urllib.error.URLError as e:
            if hasattr(e, 'read'):
                result = self.main.pretty_print(e.read().decode('utf8'))
            else:
                result = e
        except Exception as e:
            result = e
        self.main.output.insert(tk.END, result)
        self.main.output.highlight()

        self.main.output['state'] = 'disabled'
        self.main.dialog.destroy()


if __name__ == '__main__':
    App().init().mainloop()
