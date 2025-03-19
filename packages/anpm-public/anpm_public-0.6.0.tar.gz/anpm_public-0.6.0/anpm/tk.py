from platform import system
from tkinter import Tk, Misc, Widget, Frame, IntVar, Label, Toplevel
from tkinter.font import Font
from tkinter.ttk import Scrollbar as TtkScrollbar, Style
from typing import Literal, Callable, Any, Type

platform = system()


class NewTk(Tk):
    def __init__(self, title: str = "tk", resize: tuple[int | float, int | float] | None = (2, 2), center: bool = True,
                 **kwargs):
        if platform == "Windows":
            from ctypes import windll

            windll.shcore.SetProcessDpiAwareness(1)

        super().__init__(**kwargs)
        self.title(title)

        if center: self.center()
        if resize: self.resize(*resize)

        self.rows = IntVar(value=0)
        self.r = self.rows.get

        def update_rows(*_):
            for row in range(self.r()):
                self.grid_rowconfigure(row, weight=0)

        self.rows.trace_add("write", update_rows)

        self.columns = IntVar(value=0)
        self.c = self.columns.get

        def update_columns(*_):
            for column in range(self.c()):
                self.grid_columnconfigure(column, weight=0)

        self.columns.trace_add("write", update_columns)

        self.style = Style()

    def center(self):
        self.update_idletasks()

        screenwidth, screenheight = self.winfo_screenwidth(), self.winfo_screenheight()
        width, height = self.winfo_width(), self.winfo_height()

        self.geometry(f"+{(screenwidth - width) // 2}+{(screenheight - height) // 2}")

    def resize(self, width_factor: int | float, height_factor: int | float):
        self.update_idletasks()

        screenwidth, screenheight = self.winfo_screenwidth(), self.winfo_screenheight()
        new_width, new_height = screenwidth // width_factor, screenheight // height_factor

        x, y = self.winfo_x(), self.winfo_y()
        width, height = self.winfo_width(), self.winfo_height()
        new_x, new_y = x + (width - new_width) // 2, y + (height - new_height) // 2

        self.geometry(f"{int(new_width)}x{int(new_height)}+{int(new_x)}+{int(new_y)}")

    def set_rows(self, *row_weights: int):
        if len(row_weights) == 1 and row_weights[0] > 1:
            row_weights = [1] * row_weights[0]

        self.rows.set(len(row_weights))
        for row, weight in enumerate(row_weights):
            self.grid_rowconfigure(row, weight=weight)

    def set_columns(self, *column_weights: int):
        if len(column_weights) == 1 and column_weights[0] > 1:
            column_weights = [1] * column_weights[0]

        self.columns.set(len(column_weights))
        for column, weight in enumerate(column_weights):
            self.grid_columnconfigure(column, weight=weight)


def clear(window: Misc): [w.destroy() for w in window.winfo_children()]


def protect_grid_size(window: Misc):
    # noinspection PyArgumentList
    [widget.configure(width=1, height=1) for widget in window.winfo_children() if
     widget.cget("width") == 0 and len(widget.grid_info().get("sticky", "")) > 1]


class Border(Frame):
    def __init__(self, master: Misc | None = None, background: str = "#000000", width: int = 1,
                 height: int = 1): super().__init__(master, background=background, width=width, height=height)


class ScrollingFrame(Frame):
    from tkinter import Event

    def __init__(self, master: Misc | None = None, *_, scrollbar: bool = True, scrollbar_border: bool = True,
                 ttk_scrollbar: bool = False, **kwargs):
        from tkinter import Canvas, Scrollbar

        self.frame = Frame(master)
        self.frame.grid_propagate(False)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        self.canvas = Canvas(self.frame, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        if ttk_scrollbar:
            self.scrollbar = TtkScrollbar(self.frame, command=self.canvas.yview)

        else:
            self.scrollbar = Scrollbar(self.frame, command=self.canvas.yview)

        self.scrollbar_border = None

        if scrollbar:
            self.scrollbar.grid(row=0, column=1, sticky="ns")
            if scrollbar_border:
                self.scrollbar_border = Border(self.frame, "#a0a0a0")
                self.scrollbar_border.grid(row=0, column=0, sticky="nse")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind("<Enter>", lambda _: self.canvas.bind_all("<MouseWheel>", self.mouse_scroll))
        self.canvas.bind("<Leave>", lambda _: self.canvas.unbind_all("<MouseWheel>"))

        super().__init__(self.canvas, **kwargs)
        self.id = self.canvas.create_window((0, 0), window=self, anchor="nw")

        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.bind("<Configure>", self.on_frame_configure)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def place(self, **kwargs):
        self.frame.place(**kwargs)

    def mouse_scroll(self, event: Event):
        from tkinter import TclError

        try:
            current_scroll = self.canvas.yview()
            move = -0.045 if event.delta > 0 else 0.045
            new_scroll = current_scroll[0] + move
            self.canvas.yview_moveto(max(0.0, min(1.0, new_scroll)))

        except TclError:
            self.canvas.unbind_all("<MouseWheel>")

    def on_canvas_configure(self, event: Event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.id, width=event.width)

    def on_frame_configure(self, event: Event):
        self.canvas.configure(background=self.cget("background"))
        self.on_canvas_configure(event)
        self.canvas.bind_all("<MouseWheel>", self.mouse_scroll)

    def tkraise(self, *args, **kwargs):
        self.frame.tkraise(*args, **kwargs)

    def super_tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)


class ToolTip(object):
    def __init__(self, widget: Widget, text: str | Callable[[], str], *_, delay: int | None = 0, x_offset: int = 30,
                 y_offset: int = 10,
                 follow: bool | Literal["once"] = False, **kwargs):
        from tkinter import Label, Toplevel, LEFT, SOLID

        self.widget = widget
        self.text = text
        self.delay = delay
        # noinspection SpellCheckingInspection
        self.kwargs = {
                          "justify": LEFT,
                          "background": "#ffffff",
                          "foreground": "#000000",
                          "font": None,
                          "relief": SOLID,
                          "borderwidth": 1,
                          "wraplength": 350
                      } | kwargs
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.follow = follow

        self.id = None
        self.tw: Toplevel | None = None
        self.positioned = False
        self.label: Label | None = None

        self.enter_id: str = ""
        self.leave_id: str = ""
        self.buttonpress_id: str = ""
        self.motion_id: str = ""
        self.label_leave_id: str = ""
        self.bind_all()

    def enter(self):
        if self.tw is None:
            self.schedule()

    def leave(self):
        widget_under_pointer = self.widget.winfo_containing(*self.widget.winfo_pointerxy())
        if self.label is not None and (widget_under_pointer == self.label or widget_under_pointer == self.widget):
            return

        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        if self.delay is not None:
            self.id = self.widget.after(self.delay, self.showtip)

    def unschedule(self):
        if self.id and self.delay is not None:
            self.widget.after_cancel(self.id)
        self.id = None

    def showtip(self):
        from tkinter import Toplevel, Label
        if not self.tw:
            self.tw = Toplevel(self.widget)
            self.tw.wm_overrideredirect(True)

        if not self.positioned:
            self.update_tooltip_position()
            self.positioned = True

        self.label = Label(self.tw, text=self.text() if callable(self.text) else self.text, **self.kwargs)
        self.label.pack(ipadx=1)
        self.label.bind("<Leave>", lambda _: self.leave())

        self.label.IAmAToolTip = True

    def update_tooltip_position(self):
        if self.follow is True or self.follow == "once":
            x = self.widget.winfo_pointerx() + self.x_offset
            y = self.widget.winfo_pointery() + self.y_offset
        else:
            widget_x = self.widget.winfo_rootx() + self.x_offset
            widget_y = self.widget.winfo_rooty() + self.y_offset
            x, y = widget_x, widget_y

        self.tw.wm_geometry(f"+{x}+{y}")

    def on_motion(self):
        if self.tw and self.follow:
            self.update_tooltip_position()

    def bind_all(self):
        self.enter_id = self.widget.bind("<Enter>", lambda _: self.enter(), add=True)
        self.leave_id = self.widget.bind("<Leave>", lambda _: self.leave(), add=True)
        self.buttonpress_id = self.widget.bind("<ButtonPress>", lambda _: self.leave(), add=True)
        if self.follow is True:
            self.motion_id = self.widget.bind("<Motion>", lambda _: self.on_motion(), add=True)

    def destroy(self):
        self.widget.unbind("<Enter>", self.enter_id)
        self.widget.unbind("<Leave>", self.leave_id)
        self.widget.unbind("<ButtonPress>", self.buttonpress_id)
        if self.follow is True or self.follow == "once":
            self.widget.unbind("<Motion>", self.motion_id)
        self.leave()

    def hidetip(self):
        if self.tw:
            self.tw.destroy()
            self.tw = None
            self.positioned = False


class NewFrame(Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.rows = IntVar(value=0)
        self.r = self.rows.get

        def update_rows(*_):
            for row in range(self.r()):
                self.grid_rowconfigure(row, weight=0)

        self.rows.trace_add("write", update_rows)

        self.columns = IntVar(value=0)
        self.c = self.columns.get

        def update_columns(*_):
            for column in range(self.c()):
                self.grid_columnconfigure(column, weight=0)

        self.columns.trace_add("write", update_columns)

    def set_rows(self, *row_weights: int):
        if len(row_weights) == 1 and row_weights[0] > 1:
            row_weights = [1] * row_weights[0]

        self.rows.set(len(row_weights))
        for row, weight in enumerate(row_weights):
            self.grid_rowconfigure(row, weight=weight)

    def set_columns(self, *column_weights: int):
        if len(column_weights) == 1 and column_weights[0] > 1:
            column_weights = [1] * column_weights[0]

        self.columns.set(len(column_weights))
        for column, weight in enumerate(column_weights):
            self.grid_columnconfigure(column, weight=weight)


def get_default_font():
    from tkinter.font import Font
    return Font(family="Segoe UI", size=9, weight="normal", slant="roman", underline=False, overstrike=False)


def is_hovered(widget: Widget):
    return widget.master.winfo_containing(*widget.master.winfo_pointerxy()) == widget


def validate_input(new_value: str, rule: Callable[[str], bool]) -> bool:
    return rule(new_value)


class NewFont(Font):
    def __init__(self):
        self.default = dict(family="Segoe UI", size=9, weight="normal", slant="roman", underline=False,
                            overstrike=False)
        super().__init__(**self.default)

    def reset(self):
        super().__init__(**self.default)
        return self


class NewLabel(Label):
    def __init__(self, master: Misc | None = None, cnf: dict[str, Any] | None = None, **kwargs):
        if cnf is None: cnf = {}

        self.frame = Frame(master)
        self.frame.pack_propagate(False)
        self.frame.grid_propagate(False)

        super().__init__(self.frame, cnf, **kwargs)
        super().pack(fill="both", expand=True)

    def pack(self, **kwargs): self.frame.pack(**kwargs)

    def grid(self, **kwargs): self.frame.grid(**kwargs)

    def destroy(self):
        super().destroy()
        self.frame.destroy()

    def pack_forget(self): self.frame.pack_forget()

    def place_forget(self): self.frame.place_forget()

    def grid_forget(self): self.frame.grid_forget()

    def super_pack(self, **kwargs): super().pack(**kwargs)

    def super_grid(self, **kwargs): super().grid(**kwargs)


class NewWidget(Widget):
    # def __init__(self, widget_type: Type[Widget], master: Misc | None = None, cnf: dict[str, Any] | None = None, *args, **kwargs):
    #     if cnf is None: cnf = {}

    # noinspection PyMissingConstructor
    def __init__(self, widget_type: Type[Widget], master: Misc | None = None, *args, **kwargs):
        self.frame = Frame(master)
        self.frame.pack_propagate(False)
        self.frame.grid_propagate(False)

        # self.widget = widget_type(self.frame, cnf, *args, **kwargs)
        self.widget = widget_type(self.frame, *args, **kwargs)
        self.widget.pack(fill="both", expand=True)

        self.widgetType = widget_type

    def pack(self, **kwargs): self.frame.pack(**kwargs)

    def grid(self, **kwargs): self.frame.grid(**kwargs)

    def destroy(self):
        self.widget.destroy()
        self.frame.destroy()

    def pack_forget(self): self.frame.pack_forget()

    def place_forget(self): self.frame.place_forget()

    def grid_forget(self): self.frame.grid_forget()

    def __getattr__(self, name):
        if hasattr(self.widget, name): return getattr(self.widget, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def super_pack(self, **kwargs): super().pack(**kwargs)

    def super_grid(self, **kwargs): super().grid(**kwargs)


def hovered_widget(widget: Widget) -> Widget | Tk | Misc:
    if isinstance(widget, Tk):
        return widget.winfo_containing(*widget.winfo_pointerxy())
    else:
        return widget.master.winfo_containing(*widget.master.winfo_pointerxy())


def generate_validate_command(window: Misc, rule: Callable[[str], bool]) -> tuple[str, str]:
    return window.register(lambda k: validate_input(k, rule)), "%P"


class LockedFrame(Frame):
    def __init__(
            self,
            master: Misc | None = None,
            ratio: tuple[int, int] | None = None,
            min_size: tuple[int, int] | None = None,
            max_size: tuple[int, int] | None = None,
            *args, **kwargs
    ):
        self.ratio = ratio
        self.min_width, self.min_height = min_size if min_size else (None, None)
        self.max_width, self.max_height = max_size if max_size else (None, None)

        self.frame = Frame(master)
        self.frame.pack_propagate(False)

        self.pack = self.frame.pack
        self.grid = self.frame.grid
        self.pack_forget = self.frame.pack_forget
        self.place_forget = self.frame.place_forget
        self.grid_forget = self.frame.grid_forget

        self.super_pack = super().pack
        self.super_grid = super().grid

        super().__init__(self.frame, *args, **kwargs)

        if any(i is not None for i in [ratio, min_size, max_size]):
            self.pack_propagate(False)
            self.grid_propagate(False)

        self.super_pack(expand=True)
        self.frame.bind("<Configure>", self._resize)

    def _resize(self, event):
        width, height = event.width, event.height

        if self.min_width and width < self.min_width:
            width = self.min_width

        if self.min_height and height < self.min_height:
            height = self.min_height

        if self.max_width and width > self.max_width:
            width = self.max_width

        if self.max_height and height > self.max_height:
            height = self.max_height

        if self.ratio:
            ratio_x, ratio_y = self.ratio

            if width / height > ratio_x / ratio_y:
                width = int(height * (ratio_x / ratio_y))

            else:
                height = int(width * (ratio_y / ratio_x))

        self.configure(width=width, height=height)

    def destroy(self):
        super().destroy()
        self.frame.destroy()


def make_window_draggable(window: Tk | Toplevel, dragged_function: Callable[[int, int], None] = lambda *_: None):
    window.drag_start = (None, None)

    def on_drag_start(event):
        window.drag_start = event.x, event.y

    def on_drag_motion(event):
        delta_x = event.x - window.drag_start[0]
        delta_y = event.y - window.drag_start[1]

        new_x = window.winfo_x() + delta_x
        new_y = window.winfo_y() + delta_y

        width, height = window.winfo_width(), window.winfo_height()
        s_width, s_height = window.winfo_screenwidth(), window.winfo_screenheight()

        new_x = min(max(-width // 2, new_x), s_width - width // 2)
        new_y = min(max(-height // 2, new_y), s_height - height // 2)

        window.geometry(f"+{new_x}+{new_y}")

        dragged_function(delta_x, delta_y)

    window.bind("<ButtonPress-1>", on_drag_start)
    window.bind("<B1-Motion>", on_drag_motion)


def after(func, window: Misc):
    """Wrapper"""

    def do(*args, **kwargs):
        window.after_idle(lambda: func(*args, **kwargs))

    return do


def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
    """
    By SneakyTurtle on StackOverflow: https://stackoverflow.com/users/7202599/sneakyturtle
    """

    points = [x1 + radius, y1,
              x1 + radius, y1,
              x2 - radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1 + radius,
              x1, y1]

    return self.create_polygon(points, **kwargs, smooth=True)


# Compatibility
NewTK = NewTk

__all__ = ["NewTk", "clear", "protect_grid_size", "Border", "ScrollingFrame", "ToolTip", "NewFrame", "get_default_font",
           "is_hovered", "validate_input", "NewFont", "NewLabel", "NewWidget", "hovered_widget",
           "generate_validate_command", "LockedFrame", "make_window_draggable", "NewTK", "after", "round_rectangle"]
