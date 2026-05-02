import tkinter as tk
import tkinter.font as tkfont
from tkinter import scrolledtext, messagebox
import ctypes
import sys


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


def remove_duplicates(lines, strip_lines=True, ignore_case=False, keep_empty=False, sort_result=False):
    processed_lines = []

    for line in lines:
        value = line.strip() if strip_lines else line
        if not keep_empty and not value:
            continue
        processed_lines.append(value)

    unique_lines = []
    seen = set()

    for line in processed_lines:
        key = line.casefold() if ignore_case else line
        if key not in seen:
            seen.add(key)
            unique_lines.append(line)

    if sort_result:
        unique_lines.sort(key=lambda item: item.casefold() if ignore_case else item)

    return processed_lines, unique_lines


def enable_high_dpi_mode():
    if sys.platform != "win32":
        return

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def configure_fonts(root):
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(family="Segoe UI", size=10)

    text_font = tkfont.nametofont("TkTextFont")
    text_font.configure(family="Segoe UI", size=10)

    menu_font = tkfont.nametofont("TkMenuFont")
    menu_font.configure(family="Segoe UI", size=10)

    fixed_font = tkfont.nametofont("TkFixedFont")
    fixed_font.configure(family="Consolas", size=10)

    root.option_add("*Font", default_font)


def get_work_area(root):
    if sys.platform == "win32":
        rect = RECT()
        try:
            ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
            return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top
        except Exception:
            pass

    return 0, 0, root.winfo_screenwidth(), root.winfo_screenheight()

class DuplicateRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Удаление дубликатов строк")
        self.set_start_window_size()
        self.auto_update_job = None
        
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#0078d4',
            'accent_light': '#4cc2ff',
            'success': '#107c10',
            'success_light': '#14a114',
            'input_bg': '#2d2d2d',
            'input_fg': '#ffffff',
            'border': '#3d3d3d',
            'stats_bg': '#252525',
            'header_bg': '#2a2a2a',
            'disabled_bg': '#404040',
            'disabled_fg': '#808080'
        }

        self.strip_lines_var = tk.BooleanVar(value=True)
        self.ignore_case_var = tk.BooleanVar(value=False)
        self.keep_empty_var = tk.BooleanVar(value=False)
        self.sort_result_var = tk.BooleanVar(value=False)
        
        self.root.configure(bg=self.colors['bg'])
        main_frame = tk.Frame(root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        top_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        top_frame.pack(fill=tk.BOTH, expand=True)
        left_frame = tk.Frame(top_frame, bg=self.colors['bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 7))
        left_header = tk.Frame(left_frame, bg=self.colors['header_bg'], height=30)
        left_header.pack(fill=tk.X, pady=(0, 5))
        left_header.pack_propagate(False)
        
        tk.Label(
            left_header, 
            text="Ввод данных",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['header_bg'],
            fg=self.colors['fg']
        ).pack(side=tk.LEFT, padx=10, pady=5)

        self.paste_button = self.create_header_button(
            left_header,
            "Вставить",
            self.paste_from_clipboard,
            self.colors['accent'],
            self.colors['accent_light']
        )
        self.paste_button.pack(side=tk.RIGHT, padx=(0, 10))

        input_frame = tk.Frame(left_frame, bg=self.colors['input_bg'], relief=tk.FLAT, bd=1, highlightbackground=self.colors['border'], highlightthickness=1)
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 10),
            bg=self.colors['input_bg'],
            fg=self.colors['input_fg'],
            insertbackground=self.colors['fg'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['fg'],
            relief=tk.FLAT,
            bd=0,
            padx=5,
            pady=5
        )

        self.input_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        right_frame = tk.Frame(top_frame, bg=self.colors['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(7, 0))
        right_header = tk.Frame(right_frame, bg=self.colors['header_bg'], height=30)
        right_header.pack(fill=tk.X, pady=(0, 5))
        right_header.pack_propagate(False)
        
        tk.Label(
            right_header, 
            text="Результат",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['header_bg'],
            fg=self.colors['fg']
        ).pack(side=tk.LEFT, padx=10, pady=5)
        
        self.copy_button = self.create_header_button(
            right_header,
            "Копировать",
            self.copy_to_clipboard,
            self.colors['disabled_bg'],
            self.colors['success_light'],
            state=tk.DISABLED,
            fg=self.colors['disabled_fg']
        )
        self.copy_button.pack(side=tk.RIGHT, padx=10)
        result_frame = tk.Frame(right_frame, bg=self.colors['input_bg'], relief=tk.FLAT, bd=1, highlightbackground=self.colors['border'], highlightthickness=1)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = scrolledtext.ScrolledText(
            result_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 10),
            bg=self.colors['input_bg'],
            fg=self.colors['input_fg'],
            insertbackground=self.colors['fg'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['fg'],
            relief=tk.FLAT,
            bd=0,
            state=tk.DISABLED,
            padx=5,
            pady=5
        )

        self.result_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        stats_frame = tk.Frame(main_frame, bg=self.colors['stats_bg'], relief=tk.FLAT, bd=1, highlightbackground=self.colors['border'], highlightthickness=1)
        stats_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            stats_frame, 
            text="СТАТИСТИКА",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['stats_bg'],
            fg=self.colors['fg']
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        stats_grid = tk.Frame(stats_frame, bg=self.colors['stats_bg'])
        stats_grid.pack(fill=tk.X, padx=15, pady=(0, 10))
        self.total_label, self.total_value = self.create_stat_label(stats_grid, "Всего строк:", "0", 0)
        self.unique_label, self.unique_value = self.create_stat_label(stats_grid, "Уникальных строк:", "0", 1)
        self.duplicates_label, self.duplicates_value = self.create_stat_label(stats_grid, "Удалено дублей:", "0", 2)

        options_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        options_frame.pack(fill=tk.X, pady=(0, 10))

        self.create_option(options_frame, "Обрезать пробелы", self.strip_lines_var)
        self.create_option(options_frame, "Не учитывать регистр", self.ignore_case_var)
        self.create_option(options_frame, "Оставлять пустые строки", self.keep_empty_var)
        self.create_option(options_frame, "Сортировать результат", self.sort_result_var)

        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, pady=5)

        self.process_button = tk.Button(
            button_frame,
            text="Удалить дубликаты",
            command=self.process_duplicates,
            bg=self.colors['accent'],
            fg=self.colors['fg'],
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            height=2,
            cursor="hand2",
            activebackground=self.colors['accent_light'],
            activeforeground=self.colors['fg']
        )
        self.process_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 7))

        self.clear_button = tk.Button(
            button_frame,
            text="Очистить",
            command=self.clear_all,
            bg=self.colors['header_bg'],
            fg=self.colors['fg'],
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            height=2,
            cursor="hand2",
            activebackground=self.colors['border'],
            activeforeground=self.colors['fg']
        )
        self.clear_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(7, 0))
        
        self.process_button.bind("<Enter>", lambda e: self.on_enter(e, self.process_button, self.colors['accent_light']))
        self.process_button.bind("<Leave>", lambda e: self.on_leave(e, self.process_button, self.colors['accent']))
        self.clear_button.bind("<Enter>", lambda e: self.on_enter(e, self.clear_button, self.colors['border']))
        self.clear_button.bind("<Leave>", lambda e: self.on_leave(e, self.clear_button, self.colors['header_bg']))
        
        self.copy_button.bind("<Enter>", lambda e: self.on_enter_copy(e))
        self.copy_button.bind("<Leave>", lambda e: self.on_leave_copy(e))
        
        self.input_text.bind('<KeyRelease>', self.on_input_change)
        self.root.bind_all("<Control-KeyPress>", self.handle_control_shortcuts)

    def set_start_window_size(self):
        work_x, work_y, work_width, work_height = get_work_area(self.root)

        width = min(1200, max(760, int(work_width * 0.9)))
        height = min(900, max(650, int(work_height * 0.95)))
        width = min(width, work_width)
        height = min(height, work_height)
        x = work_x + max(0, (work_width - width) // 2)
        y = work_y + max(0, (work_height - height) // 2)

        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(min(760, work_width), min(620, work_height))
        
    def create_header_button(self, parent, text, command, bg, active_bg, state=tk.NORMAL, fg=None):
        return tk.Button(
            parent,
            text=text,
            command=command,
            state=state,
            bg=bg,
            fg=fg or self.colors['fg'],
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=2,
            cursor="hand2",
            activebackground=active_bg,
            activeforeground=self.colors['fg']
        )

    def create_stat_label(self, parent, label_text, value_text, column):
        frame = tk.Frame(parent, bg=self.colors['stats_bg'])
        frame.grid(row=0, column=column, padx=20, sticky=tk.W)
        
        label = tk.Label(
            frame, 
            text=label_text,
            font=("Segoe UI", 10),
            bg=self.colors['stats_bg'],
            fg='#cccccc'
        )
        label.pack(anchor=tk.W)
        
        value = tk.Label(
            frame, 
            text=value_text,
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['stats_bg'],
            fg=self.colors['accent_light']
        )
        value.pack(anchor=tk.W)
        
        return label, value

    def create_option(self, parent, text, variable):
        checkbox = tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            command=self.on_input_change,
            font=("Segoe UI", 10),
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            selectcolor=self.colors['input_bg'],
            activebackground=self.colors['bg'],
            activeforeground=self.colors['fg'],
            cursor="hand2"
        )
        checkbox.pack(side=tk.LEFT, padx=(0, 18))
        return checkbox
    
    def on_enter(self, event, button, color):
        if button['state'] != tk.DISABLED:
            button.configure(bg=color)
    
    def on_leave(self, event, button, color):
        if button['state'] != tk.DISABLED:
            button.configure(bg=color)
    
    def on_enter_copy(self, event):
        if self.copy_button['state'] != tk.DISABLED:
            self.copy_button.configure(bg=self.colors['success_light'])
    
    def on_leave_copy(self, event):
        if self.copy_button['state'] != tk.DISABLED:
            self.copy_button.configure(bg=self.colors['success'])
    
    def on_input_change(self, event=None):
        if self.auto_update_job:
            self.root.after_cancel(self.auto_update_job)
        self.auto_update_job = self.root.after(300, self.process_auto_update)

        self.copy_button.config(
            state=tk.DISABLED, 
            bg=self.colors['disabled_bg'],
            fg=self.colors['disabled_fg']
        )
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.total_value.config(text="0")
        self.unique_value.config(text="0")
        self.duplicates_value.config(text="0")

    def process_auto_update(self):
        self.auto_update_job = None
        self.process_duplicates(show_warnings=False)

    def handle_control_shortcuts(self, event):
        if event.keycode == 86:
            self.paste_from_clipboard(insert_at_cursor=True)
            return "break"

        if event.keycode == 67:
            self.copy_cleaned_data()
            return "break"

        if event.keysym == "Return":
            self.process_duplicates()
            return "break"

        if event.keycode == 76:
            self.clear_all()
            return "break"

        return None
    
    def process_duplicates(self, show_warnings=True):
        input_data = self.input_text.get(1.0, tk.END)
        
        if not input_data.strip():
            if show_warnings:
                messagebox.showwarning("Предупреждение", "Введите строки для обработки!", parent=self.root)
            return
        
        lines = input_data.splitlines()
        processed_lines, unique_lines = remove_duplicates(
            lines,
            strip_lines=self.strip_lines_var.get(),
            ignore_case=self.ignore_case_var.get(),
            keep_empty=self.keep_empty_var.get(),
            sort_result=self.sort_result_var.get()
        )
        
        if not processed_lines:
            if show_warnings:
                messagebox.showwarning("Предупреждение", "Нет строк для обработки!", parent=self.root)
            return
        
        total_lines = len(processed_lines)
        unique_count = len(unique_lines)
        duplicates_count = total_lines - unique_count
        self.total_value.config(text=str(total_lines))
        self.unique_value.config(text=str(unique_count))
        self.duplicates_value.config(text=str(duplicates_count))
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, '\n'.join(unique_lines))
        self.result_text.config(state=tk.DISABLED)
        
        self.copy_button.config(
            state=tk.NORMAL, 
            bg=self.colors['success'],
            fg=self.colors['fg']
        )
    
    def copy_to_clipboard(self):
        result = self.result_text.get(1.0, tk.END).strip()
        
        if result:
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(result)
                original_text = self.copy_button['text']
                self.copy_button.config(text="Скопировано!", bg=self.colors['success_light'])
                self.root.after(1500, lambda: self.restore_copy_button(original_text))
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось скопировать в буфер обмена: {str(e)}", parent=self.root)
        else:
            messagebox.showwarning("Предупреждение", "Нет данных для копирования!", parent=self.root)

    def copy_cleaned_data(self):
        result = self.result_text.get(1.0, tk.END).strip()

        if not result:
            self.process_duplicates(show_warnings=False)
            result = self.result_text.get(1.0, tk.END).strip()

        if result:
            self.copy_to_clipboard()
    
    def restore_copy_button(self, original_text):
        self.copy_button.config(
            text=original_text, 
            bg=self.colors['success'],
            fg=self.colors['fg']
        )

    def paste_from_clipboard(self, insert_at_cursor=False):
        try:
            text = self.root.clipboard_get()
        except tk.TclError:
            messagebox.showwarning("Предупреждение", "Буфер обмена пуст или содержит не текст.", parent=self.root)
            return

        self.input_text.focus_set()

        if insert_at_cursor:
            try:
                self.input_text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                pass
            self.input_text.insert(tk.INSERT, text)
        else:
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(1.0, text)

        self.on_input_change()

    def clear_all(self):
        if self.auto_update_job:
            self.root.after_cancel(self.auto_update_job)
            self.auto_update_job = None

        self.input_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.total_value.config(text="0")
        self.unique_value.config(text="0")
        self.duplicates_value.config(text="0")
        self.copy_button.config(
            state=tk.DISABLED,
            bg=self.colors['disabled_bg'],
            fg=self.colors['disabled_fg'],
            text="Копировать"
        )

def main():
    enable_high_dpi_mode()
    root = tk.Tk()
    root.tk.call("tk", "scaling", root.winfo_fpixels("1i") / 72)
    configure_fonts(root)
    
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass
    
    app = DuplicateRemoverApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
