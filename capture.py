import tkinter as tk
import mss
import mss.tools


def capture_region() -> tuple:
    """Opens fullscreen overlay for region selection. Returns (x, y, width, height) or None."""
    result = {}

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.25)
    root.attributes("-topmost", True)
    root.configure(bg="black")
    root.config(cursor="crosshair")

    canvas = tk.Canvas(root, bg="black", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    label = tk.Label(
        root,
        text="Arraste para selecionar a questão  |  ESC para cancelar",
        bg="#222222",
        fg="white",
        font=("monospace", 13),
    )
    label.place(relx=0.5, rely=0.02, anchor="n")

    state = {"start_x": None, "start_y": None, "rect": None}

    def on_press(event):
        state["start_x"] = event.x
        state["start_y"] = event.y
        if state["rect"]:
            canvas.delete(state["rect"])

    def on_drag(event):
        if state["rect"]:
            canvas.delete(state["rect"])
        state["rect"] = canvas.create_rectangle(
            state["start_x"],
            state["start_y"],
            event.x,
            event.y,
            outline="#00FF88",
            width=2,
        )

    def on_release(event):
        x1 = min(state["start_x"], event.x)
        y1 = min(state["start_y"], event.y)
        x2 = max(state["start_x"], event.x)
        y2 = max(state["start_y"], event.y)

        if (x2 - x1) > 10 and (y2 - y1) > 10:
            result["region"] = (x1, y1, x2 - x1, y2 - y1)

        root.destroy()

    def on_escape(event):
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Escape>", on_escape)

    root.mainloop()

    return result.get("region", None)


def take_screenshot(region: tuple):
    """Captures the screen region. region = (x, y, width, height)"""
    x, y, w, h = region
    with mss.mss() as sct:
        monitor = {"top": y, "left": x, "width": w, "height": h}
        screenshot = sct.grab(monitor)
        from PIL import Image
        return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
