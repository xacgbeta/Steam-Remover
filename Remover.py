import tkinter as tk
from tkinter import messagebox, filedialog
import os
import subprocess
import re
import time

class Remover:
    def __init__(self, master):
        master.title('Remover')
        master.geometry('260x188')
        master.resizable(False, False)
        master.configure(bg='#1E1E1E')
        
        self.master = master
        self.steam_path = self.steam_path()
        
        self.input_frame = tk.Frame(master, bg='#1E1E1E')
        self.input_frame.pack(pady=10)
        tk.Label(self.input_frame, text='AppID:', font=('Helvetica', 10, 'bold'), fg='white', bg='#1E1E1E').pack(side=tk.LEFT, padx=5)
        
        validate_cmd = master.register(lambda P: P.isdigit() or P == "")
        self.appid_entry = tk.Entry(self.input_frame, width=21, font=('Helvetica', 10), justify='center', bd=1, relief='solid', highlightbackground='#555555', highlightcolor='#FFCC00', highlightthickness=1, validate="key", validatecommand=(validate_cmd, "%P"))
        self.appid_entry.pack(side=tk.LEFT)
        
        self.steam_path_label_var = tk.StringVar()
        tk.Label(master, textvariable=self.steam_path_label_var, font=('Helvetica', 8), fg='#BBBBBB', bg='#1E1E1E', justify='center').pack(pady=(0, 5), padx=5)
        
        btn_font, btn_width, btn_style = ('Helvetica', 10, 'bold'), 25, {'bg': '#2D2D2D', 'fg': 'white', 'width': 25, 'height': 1, 'relief': 'flat'}
        self.steam_path_button = tk.Button(master, text='Steam Folder', font=btn_font, command=self.change_path, **btn_style)
        self.delete_button = tk.Button(master, text='Remove Game', font=btn_font, command=self.item_removed, **btn_style)
        self.restart_button = tk.Button(master, text='Restart Steam', font=btn_font, command=self.restart, **btn_style)

        for btn in [self.steam_path_button, self.delete_button, self.restart_button]:
            btn.pack(pady=5)
            btn.bind('<Enter>', lambda e: e.widget.config(bg='#FFCC00', fg='black'))
            btn.bind('<Leave>', lambda e: e.widget.config(bg='#2D2D2D', fg='white'))

        self.path_update()

    def steam_path(self):
        path_fragments = [('Program Files (x86)', 'Steam'), ('Program Files', 'Steam'), ('Steam',)]
        for drive in [f"{chr(d)}:\\" for d in range(ord('C'), ord('Z') + 1)]:
            for fragment in path_fragments:
                path = os.path.join(drive, *fragment)
                if os.path.exists(os.path.join(path, 'Steam.exe')):
                    return path
        return None

    def maniluabin(self, game_id):
        log_text = f"--- AppID: {game_id} ---\n\n"
        paths_to_check = {k: os.path.join(self.steam_path, *v) for k, v in {
            "p1": ("config", "stplug-in"), "p2": ("config", "depotcache"),
            "p3": ("depotcache",), "p4": ("config", "stUI"), "p5": ("config", "StatsExport")}.items()}
        pattern = re.compile(rf"^{game_id}\D+")
        
        files_deleted = 0
        for path in paths_to_check.values():
            log_text += f"Checking: {path}\n"
            if not os.path.isdir(path):
                log_text += "Directory not found.\n\n"
                continue
            
            found = False
            try:
                for filename in os.listdir(path):
                    filepath = os.path.join(path, filename)
                    if os.path.isfile(filepath) and pattern.match(filename):
                        found = True
                        try:
                            os.remove(filepath)
                            files_deleted += 1
                            log_text += f"Deleting: {filename}\n"
                        except OSError as e:
                            log_text += f"ERROR deleting {filename}: {e}\n"
            except OSError as e:
                log_text += f"ERROR accessing folder: {e}\n"
            
            if not found:
                log_text += "No matching files found.\n"
            log_text += "\n"
        return files_deleted, log_text

    def restart_steam(self):
        if not self.steam_path: return False, "Could not find Steam path."
        steam_exe = os.path.join(self.steam_path, "Steam.exe")
        if not os.path.exists(steam_exe): return False, f"Steam.exe not found at: {steam_exe}"
        try:
            if os.name == 'nt':
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.run(["taskkill", "/IM", "Steam.exe", "/F"], startupinfo=si, check=False)
                time.sleep(1)
                subprocess.Popen([steam_exe])
                return True, "Steam restarted."
            else:
                return False, "Restart only implemented for Windows."
        except Exception as e:
            return False, f"An error occurred: {e}"

    def path_update(self):
        if self.steam_path and os.path.isdir(self.steam_path):
            p = self.steam_path
            text = f"Steam Path: {p[:25] + '...' if len(p) > 28 else p}"
        else:
            text = "Steam Path: Not Found / Select Manually"
            self.steam_path = None
        self.steam_path_label_var.set(text)

    def change_path(self):
        new_path = filedialog.askdirectory(initialdir=self.steam_path or os.path.expanduser("~"))
        if new_path:
            if os.path.exists(os.path.join(new_path, "Steam.exe")):
                self.steam_path = new_path
            else:
                messagebox.showwarning("Invalid Path", f"Steam.exe not found in:\n{new_path}")
            self.path_update()

    def item_removed(self):
        game_id = self.appid_entry.get().strip()
        if not game_id:
            messagebox.showerror("Error", "Please enter an AppID.")
            return
        if not self.steam_path:
            messagebox.showerror("Error", "Steam path not found. Please set it manually.")
            return
        
        files_deleted, log_text = self.maniluabin(game_id)
        if files_deleted > 0: messagebox.showinfo("Success", log_text)
        else: messagebox.showinfo("Info", log_text)

    def restart(self):
        success, message = self.restart_steam()
        if success: messagebox.showinfo("Info", message)
        else: messagebox.showerror("Error", f"Steam restart failed: {message}")

if __name__ == '__main__':
    root = tk.Tk()
    app = Remover(root)
    root.mainloop()
