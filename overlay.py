import tkinter as tk
import threading


class AnswerOverlay:
    def __init__(self):
        self.root = None
        self._thread = None

    def show(self, text: str):
        if self.root:
            self.close()

        self._thread = threading.Thread(target=self._run, args=(text,), daemon=True)
        self._thread.start()

    def _run(self, text: str):
        self.root = tk.Tk()
        self.root.title("")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.92)
        self.root.overrideredirect(True)
        self.root.configure(bg="#1a1a2e")

        frame = tk.Frame(self.root, bg="#1a1a2e", padx=14, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(frame, bg="#1a1a2e")
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="Quiz Helper",
            bg="#1a1a2e",
            fg="#00FF88",
            font=("monospace", 10, "bold"),
        ).pack(side=tk.LEFT)

        tk.Button(
            header,
            text="✕",
            bg="#1a1a2e",
            fg="#888888",
            font=("monospace", 10),
            bd=0,
            activebackground="#1a1a2e",
            activeforeground="white",
            cursor="hand2",
            command=self.close,
        ).pack(side=tk.RIGHT)

        tk.Frame(frame, bg="#00FF88", height=1).pack(fill=tk.X, pady=(4, 8))

        text_widget = tk.Text(
            frame,
            bg="#1a1a2e",
            fg="white",
            font=("monospace", 11),
            wrap=tk.WORD,
            bd=0,
            highlightthickness=0,
            state=tk.NORMAL,
            width=48,
        )
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack()

        # tamanho e posição (canto inferior direito)
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = sw - w - 20
        y = sh - h - 60
        self.root.geometry(f"+{x}+{y}")

        # arrastar a janela
        self._drag = {}

        def start_drag(event):
            self._drag["x"] = event.x
            self._drag["y"] = event.y

        def do_drag(event):
            dx = event.x - self._drag["x"]
            dy = event.y - self._drag["y"]
            nx = self.root.winfo_x() + dx
            ny = self.root.winfo_y() + dy
            self.root.geometry(f"+{nx}+{ny}")

        frame.bind("<ButtonPress-1>", start_drag)
        frame.bind("<B1-Motion>", do_drag)

        self.root.mainloop()

    def show_loading(self):
        self.show("Analisando questão...")

    def close(self):
        if self.root:
            try:
                self.root.destroy()
            except Exception:
                pass
            self.root = None
