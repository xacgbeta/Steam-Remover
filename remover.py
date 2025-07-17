import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import re
from tkinter import filedialog
import time

def find_steam_path():

    possible_drives = [f"{chr(d)}:\\" for d in range(ord('C'), ord('Z') + 1)]
    for drive in possible_drives:

        potential_path_64 = os.path.join(drive, 'Program Files (x86)', 'Steam')
        if os.path.exists(os.path.join(potential_path_64, 'Steam.exe')):
            return potential_path_64

        potential_path_32 = os.path.join(drive, 'Program Files', 'Steam')
        if os.path.exists(os.path.join(potential_path_32, 'Steam.exe')):
            return potential_path_32

        potential_path_root = os.path.join(drive, 'Steam')
        if os.path.exists(os.path.join(potential_path_root, 'Steam.exe')):
            return potential_path_root
    return None

def delete_game_files(steam_path, game_id):
    files_deleted = 0
    log_text = f"--- AppID: {game_id} ---\n\n"

    if not game_id or not game_id.isdigit():
        return -1, "AppID must be a number."
    
    steam_paths_to_check = {
        "stplugin": os.path.join(steam_path, "config", "stplug-in"),
        "config_depotcache": os.path.join(steam_path, "config", "depotcache"),
        "depotcache": os.path.join(steam_path, "depotcache"),
        "stui": os.path.join(steam_path, "config", "stUI"),
        "stats": os.path.join(steam_path, "config", "StatsExport"),
    }

    if len(game_id) > 1:
        pattern_str = rf"^{game_id}"
    else:
        pattern_str = rf"^{game_id}"
    pattern = re.compile(pattern_str)

    for path_key, path in steam_paths_to_check.items():
        log_text += f"Checking: {path}\n"
        if not os.path.isdir(path):
            log_text += "  Directory not found.\n\n"
            continue

        found_in_folder = False
        try:
            for filename in os.listdir(path):
                filepath = os.path.join(path, filename)
                if os.path.isfile(filepath) and pattern.match(filename):
                    found_in_folder = True
                    try:
                        log_text += f"  Deleting: {filename}\n"
                        os.remove(filepath)
                        files_deleted += 1
                    except OSError as e:
                        log_text += f"  ERROR deleting {filename}: {e}\n"
        except OSError as e:
            log_text += f"  ERROR accessing folder contents: {e}\n\n"
            continue

        if not found_in_folder:
            log_text += "  No matching files found.\n"
        log_text += "\n"

    return files_deleted, log_text

def restart_steam():
    steam_path = find_steam_path()
    if not steam_path:
        return False, "Could not find Steam path."

    steam_exe_path = os.path.join(steam_path, "Steam.exe")
    if not os.path.exists(steam_exe_path):
        return False, f"Steam.exe not found at: {steam_exe_path}"

    try:
        if os.name == 'nt':
            kill_command = ["taskkill", "/IM", "Steam.exe", "/F"]
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(kill_command, shell=False, startupinfo=startupinfo, check=False)
            time.sleep(1)
            
            subprocess.Popen([steam_exe_path])
            return True, "Steam restarted."
        else:
            return False,
    except Exception as e:
        return False, f"An error occurred: {e}"

class Remover:
    def __init__(self, master):
        self.master = master
        master.title('Game Remover')
        master.geometry('260x188')
        master.resizable(False, False)
        master.configure(bg='#1E1E1E')

        self.steam_path = find_steam_path()

        # --- UI Elements ---
        self.input_frame = tk.Frame(master, bg='#1E1E1E')
        self.input_frame.pack(pady=10)

        self.label = tk.Label(self.input_frame, text='AppID:', font=('Helvetica', 10, 'bold'), fg='white', bg='#1E1E1E')
        self.label.pack(side=tk.LEFT, padx=5)

        validate_cmd = master.register(self.validate_input)
        self.appid_entry = tk.Entry(self.input_frame, width=21, font=('Helvetica', 10), justify='center', bd=1, relief='solid', highlightbackground='#555555', highlightcolor='#FFCC00', highlightthickness=1,
                               validate="key", validatecommand=(validate_cmd, "%P"))
        self.appid_entry.pack(side=tk.LEFT)

        self.steam_path_label_var = tk.StringVar()
        self.steam_path_label = tk.Label(master, textvariable=self.steam_path_label_var, font=('Helvetica', 8), fg='#BBBBBB', bg='#1E1E1E', justify='center')
        self.steam_path_label.pack(pady=(0, 5), padx=5)
        self.update_steam_path_display()

        button_font = ('Helvetica', 10, 'bold')
        button_width = 25
        button_style = {'bg': '#2D2D2D', 'fg': 'white', 'width': button_width, 'height': 1, 'relief': 'flat'}

        self.steam_path_button = tk.Button(master, text='Steam Folder', font=button_font, command=self.change_steam_path, **button_style)
        self.steam_path_button.pack(pady=5)
        self.steam_path_button.bind('<Enter>', self.on_hover)
        self.steam_path_button.bind('<Leave>', self.on_leave)

        self.delete_button = tk.Button(master, text='Remove Game', font=button_font, command=self.delete_game_gui, **button_style)
        self.delete_button.pack(pady=5)
        self.delete_button.bind('<Enter>', self.on_hover)
        self.delete_button.bind('<Leave>', self.on_leave)

        self.restart_button = tk.Button(master, text='Restart Steam', font=button_font, command=self.restart_steam_gui, **button_style)
        self.restart_button.pack(pady=5)
        self.restart_button.bind('<Enter>', self.on_hover)
        self.restart_button.bind('<Leave>', self.on_leave)

    def update_steam_path_display(self):
        if self.steam_path and os.path.isdir(self.steam_path):
            max_len = 28
            display_path = self.steam_path
            if len(display_path) > max_len:
                display_path = display_path[:max_len-3] + "..."
            display_text = f"Steam Path: {display_path}"
        else:
            display_text = "Steam Path: Not Found / Select Manually"
            self.steam_path = None
        self.steam_path_label_var.set(display_text)

    def change_steam_path(self):
        initial_dir = self.steam_path if self.steam_path else os.path.expanduser("~")
        new_path = filedialog.askdirectory(title="Select Steam Installation Directory", initialdir=initial_dir)
        if new_path:
            if os.path.exists(os.path.join(new_path, "Steam.exe")):
                self.steam_path = new_path
                self.update_steam_path_display()
            else:
                messagebox.showwarning("Invalid Path", f"Steam.exe not found in:\n{new_path}\nPlease select the correct Steam installation folder.")
                if not self.steam_path:
                    self.steam_path = None
                self.update_steam_path_display()

    def delete_game_gui(self):
        game_id = self.appid_entry.get().strip()
        if not game_id:
            messagebox.showerror("Error", "Please enter an AppID.")
            return
        if not self.validate_input(game_id):
            messagebox.showerror("Error", "AppID must contain only numbers.")
            return

        if not self.steam_path:
            messagebox.showerror("Error", "Could not find Steam path.\nPlease use the 'Steam Folder' button to set it manually.")
            return
            
        files_deleted, log_text = delete_game_files(self.steam_path, game_id)

        if files_deleted > 0:
            messagebox.showinfo("Success", log_text)
        elif files_deleted == 0:
            messagebox.showinfo("Info", log_text)
        else:
            messagebox.showerror("Error", log_text)

    def restart_steam_gui(self):
        success, message = restart_steam()
        if success:
            messagebox.showinfo("Info", message)
        else:
            messagebox.showerror("Error", f"Steam restart failed: {message}")

    def validate_input(self, new_text):
        return new_text.isdigit() or new_text == ""

    def on_hover(self, event):
        event.widget.configure(bg='#FFCC00', fg='black')

    def on_leave(self, event):
        event.widget.configure(bg='#2D2D2D', fg='white')

if __name__ == '__main__':
    root = tk.Tk()
    game_remover = Remover(root)
    root.mainloop()