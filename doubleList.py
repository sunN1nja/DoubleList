import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyperclip

class DuplicateRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Удаление дубликатов строк")
        self.root.geometry("1200x600")
        
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
            text="📝 Ввод данных", 
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['header_bg'],
            fg=self.colors['fg']
        ).pack(side=tk.LEFT, padx=10, pady=5)

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
            text="✨ Результат", 
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['header_bg'],
            fg=self.colors['fg']
        ).pack(side=tk.LEFT, padx=10, pady=5)
        
        self.copy_button = tk.Button(
            right_header, 
            text="📋 Копировать", 
            command=self.copy_to_clipboard,
            state=tk.DISABLED,
            bg=self.colors['disabled_bg'],
            fg=self.colors['disabled_fg'],
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=2,
            cursor="hand2",
            activebackground=self.colors['success_light'],
            activeforeground=self.colors['fg']
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
            text="📊 СТАТИСТИКА", 
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['stats_bg'],
            fg=self.colors['fg']
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        stats_grid = tk.Frame(stats_frame, bg=self.colors['stats_bg'])
        stats_grid.pack(fill=tk.X, padx=15, pady=(0, 10))
        self.total_label, self.total_value = self.create_stat_label(stats_grid, "Всего строк:", "0", 0)
        self.unique_label, self.unique_value = self.create_stat_label(stats_grid, "Уникальных строк:", "0", 1)
        self.duplicates_label, self.duplicates_value = self.create_stat_label(stats_grid, "Удалено дублей:", "0", 2)
        
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, pady=5)
        
        self.process_button = tk.Button(
            button_frame, 
            text="🗑️ Удалить дубликаты", 
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
        self.process_button.pack(fill=tk.X)
        
        self.process_button.bind("<Enter>", lambda e: self.on_enter(e, self.process_button, self.colors['accent_light']))
        self.process_button.bind("<Leave>", lambda e: self.on_leave(e, self.process_button, self.colors['accent']))
        
        self.copy_button.bind("<Enter>", lambda e: self.on_enter_copy(e))
        self.copy_button.bind("<Leave>", lambda e: self.on_leave_copy(e))
        
        self.input_text.bind('<KeyRelease>', self.on_input_change)
        
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
    
    def process_duplicates(self):
        input_data = self.input_text.get(1.0, tk.END).strip()
        
        if not input_data:
            messagebox.showwarning("Предупреждение", "Введите строки для обработки!", parent=self.root)
            return
        
        lines = input_data.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        if not lines:
            messagebox.showwarning("Предупреждение", "Нет непустых строк для обработки!", parent=self.root)
            return
        
        total_lines = len(lines)
        
        unique_lines = []
        seen = set()
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)
        
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
                pyperclip.copy(result)
                original_text = self.copy_button['text']
                self.copy_button.config(text="✅ Скопировано!", bg=self.colors['success_light'])
                self.root.after(1500, lambda: self.restore_copy_button(original_text))
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось скопировать в буфер обмена: {str(e)}", parent=self.root)
        else:
            messagebox.showwarning("Предупреждение", "Нет данных для копирования!", parent=self.root)
    
    def restore_copy_button(self, original_text):
        self.copy_button.config(
            text=original_text, 
            bg=self.colors['success'],
            fg=self.colors['fg']
        )

def main():
    root = tk.Tk()
    
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass
    
    app = DuplicateRemoverApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()