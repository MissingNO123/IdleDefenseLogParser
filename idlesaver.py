import os
import time
import customtkinter
import argparse

verbose = False

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--log_directory", help="Directory of the log files", default=None, type=str)
parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
args = parser.parse_args()

class LogWatcher:
    def __init__(self, log_directory=None):
        self.vrc_is_running = False
        self.last_line = 0
        self.last_byte = 0
        self.log_file = None
        self.log_directory = log_directory
        self.save_code = "None"
        self.save_code_exists = False
        self.log_file_idx = 0 # nth most recent log file
        self.tkinter_inst = None
        self.popup: Popup_YesNo = None

        # set default path if not in log
        if not self.log_directory:
            self.log_directory = os.path.join(os.path.expanduser("~"), 'AppData', 'LocalLow', 'VRChat', 'VRChat')
        if not os.path.exists(self.log_directory):
            print("!! Log directory does not exist, set it manually as a launch option with \"-l\" plz kthx")
            return

    def get_save(self):
        start_time = time.perf_counter_ns()

        all_files = [os.path.join(self.log_directory, file) for file in os.listdir(self.log_directory)]
        files = [file for file in all_files if os.path.isfile(file)]
        textfiles = [file for file in files if file.endswith(".txt")]
        if not textfiles:
            print("!! No text files found in log directory")
            return
        # sort files by most recent to least recent
        textfiles.sort(key=os.path.getmtime, reverse=True)
        if (verbose): print(", ".join(textfiles))

        self.log_file_idx = 0
        for i in range(min( len(textfiles), 10 )): #only check the most recent 10 log files
            self.log_file_idx = i
            if (verbose): print (f"Checking file {i+1}/{len(textfiles)}")
            log_file = textfiles[self.log_file_idx]
            if not log_file:
                print("!! No log file found!")
                return
            if self.log_file != log_file:
                self.log_file = log_file
                self.last_line = 0
                self.last_byte = 0
                if (verbose): print(f"New log file found: {self.log_file}")
            self._load_log_file()
            if self.save_code == "None":
                if (verbose): print(f"No save code found in current log file: {self.log_file}")
            else:
                break
        if self.save_code == "None":
            print("!! No save code found in any log file")
            
        end_time = time.perf_counter_ns()
        if (verbose): print(f"Fetching save: {(end_time - start_time) / 1e6} ms")

    def _load_log_file(self):
        if self.log_file:
            new_last_byte = os.path.getsize(self.log_file)
            if self.last_byte < new_last_byte:
                with open(self.log_file, "rb") as file:
                    file.seek(self.last_byte)
                    lines = file.readlines()
                    if lines:
                        self._parse_log_lines(lines)
                self.last_byte = new_last_byte
            else:
                print("No new lines to read")

    def _parse_log_lines(self, lines):
        save_code: str = None
        dc_save_code: str = None
        dc_timestamp: str = None
        has_disconnected: bool = False
        last_line: str = None
        timestamp: str = None
        for line in lines:
            if line != b"" and line != b"\r\n" and line != b"\n" :
                l = line.decode('utf-8').strip()
                # check for a string that starts with "V2-" and ends with " IDLEDEFENSE"
                # then take everything up to that first space, exclusively
                if l.startswith("V2-") and l.endswith(" IDLEDEFENSE"):
                    save_code = l.split(" ")[0]
                    if (verbose): print(f'Found save code:\t{save_code[:25]}...')
                    # extract timestamp from last line
                    if last_line:
                        timestamp = " ".join(last_line.split(" ")[:2])
                        if (verbose): print(f"Timestamp: {timestamp}")
                if l.find("[Behaviour] showing disconnect reason") != -1:
                    if (verbose): print(f"Disconnect detected: {l}")
                    dc_timestamp = " ".join(l.split(" ")[:2])
                    has_disconnected = True
                    dc_save_code = save_code
            last_line = l
        if has_disconnected:
            if self.tkinter_inst:
                if (dc_save_code != self.tkinter_inst.dc_save_code):
                    self.tkinter_inst.show_disconnect_popup = True  
                    self.tkinter_inst.dc_save_code = dc_save_code
                    self.tkinter_inst.has_disconnected = True
                    self.tkinter_inst.dc_timestamp = dc_timestamp
        if timestamp:
            self.tkinter_inst.timestamp = timestamp

        if save_code:
            self.save_code = save_code
        else:
            if (verbose): print("No save code found")


class Popup_YesNo(customtkinter.CTkToplevel):
    def __init__(self, master, window_title, window_text, button_confirm_text, button_deny_text, button_confirm_command=None, button_deny_command=None):
        super().__init__(None)
        self.geometry("400x150")
        self.grid_columnconfigure((0,1), weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure((0,2), weight=0)
        self.title(window_title)

        self.button_confirm_command = button_confirm_command
        self.button_deny_command = button_deny_command

        self.titlebar = customtkinter.CTkLabel( self, text=window_title, fg_color="gray30", corner_radius=6 )
        self.titlebar.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

        self.label = customtkinter.CTkLabel(self, text=window_text, fg_color="gray10", corner_radius=6, wraplength=360)
        self.label.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=20, pady=5)

        self.button = customtkinter.CTkButton(self, text=button_deny_text, fg_color="#A52F62", hover_color="#82254d", command=self._cancel_button_pressed)
        self.button.grid(row=2, column=0, sticky="sew", padx=(10,5), pady=(2,10))

        self.button = customtkinter.CTkButton(self, text=button_confirm_text, command=self._ok_button_pressed)
        self.button.grid(row=2, column=1, sticky="sew", padx=(5,10), pady=(2,10))

        self.protocol("WM_DELETE_WINDOW",  self.on_close)

    def _ok_button_pressed(self):
        if self.button_confirm_command:
            self.button_confirm_command()
        self.destroy()

    def _cancel_button_pressed(self):
        if self.button_deny_command:
            self.button_deny_command()
        self.destroy()
    
    def on_close(self):
        self._cancel_button_pressed()


class App(customtkinter.CTk):
    def __init__(self, log_watcher=None):
        super().__init__()

        self.title("Idle Defense Save Code Finder")
        self.geometry("640x320")
        self.grid_columnconfigure((0,1), weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.log_watcher = log_watcher

        self.timestamp : str = None
        self.has_disconnected: bool = False
        self.dc_save_code : str = None
        self.dc_timestamp : str = None
        self.show_disconnect_popup : bool = True

        self.popup: Popup_YesNo = None

        row = 0
        
        self.save_code = customtkinter.StringVar(value=log_watcher.save_code)

        self.titlebar = customtkinter.CTkLabel(
            self, text="Idle Defense Save Code Finder", fg_color="gray30", corner_radius=6)
        self.titlebar.grid(row=row, column=0, columnspan=2, padx=10, pady=(10,0), sticky="ew")
        row += 1

        self.label_savecode = customtkinter.CTkLabel(self, text="Latest Save: ", fg_color="transparent")
        self.label_savecode.grid(row=row, column=0, columnspan=2, sticky="w", pady=(4,1), padx=(10,5))
        row += 1

        self.textbox_savecode = customtkinter.CTkTextbox(self, height=190, wrap="word")
        self.textbox_savecode.insert("0.0", self.save_code.get())
        self.textbox_savecode.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=(0,10))
        row += 1

        self.button_refresh_save_code = customtkinter.CTkButton(self, text="Refresh", fg_color="#218ADE", hover_color="#1b6eb1", command=self.refresh_save_code)
        self.button_refresh_save_code.grid(row=row, column=0, sticky="ew", padx=(10,5), pady=(2,10))


        self.button_spawn_chat_box = customtkinter.CTkButton(self, text="Copy", command=self._copy_to_clipboard)
        self.button_spawn_chat_box.grid(row=row, column=1, sticky="ew", padx=(5,10), pady=(2,10))
        row += 1

        self.protocol("WM_DELETE_WINDOW",  self.on_close)

    def refresh_save_code(self):
        self.log_watcher.get_save()
        if (self.has_disconnected and self.show_disconnect_popup == True):
            print(f"Disconnected, showing popup...")
            self.popup: Popup_YesNo = Popup_YesNo( self, 
                            window_title="Disconnect detected", 
                            window_text=f"A disconnect from VRChat has been detected. Would you like to copy the last code saved before you disconnected?\nTimestamp: {self.dc_timestamp}", 
                            button_confirm_text="Copy", 
                            button_deny_text="Nope", 
                            button_confirm_command=self._copy_to_clipboard, 
                            button_deny_command=self._stop_showing_disconnect_popup )
            self.popup.after(250, self.popup.focus) # Why do I need to wait for this???
        if (self.timestamp is not None):
            self.label_savecode.configure(text=f"Latest Save: {self.timestamp}")
        self.save_code.set(self.log_watcher.save_code)
        self.textbox_savecode.delete("0.0", "end")
        self.textbox_savecode.insert("0.0", self.save_code.get())
        if (verbose): print(f"Refreshed save code: {self.save_code.get()[:25]}...")
    
    def _stop_showing_disconnect_popup(self):
        self.show_disconnect_popup = False
        pass

    def _copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.save_code.get())
        self.update()
        self.update_idletasks()
        self.after(100, self._show_copy_confirmation)
        if (verbose): print(f"Copied {len(self.log_watcher.save_code)} bytes to clipboard")
    
    def _show_copy_confirmation(self):
        self.clipboard_get()
        self.button_spawn_chat_box.configure(text="Copied!")
        self.after(1000, self._reset_copy_confirmation)

    def _reset_copy_confirmation(self):
        self.button_spawn_chat_box.configure(text="Copy")

    def on_close(self):
        self.destroy()


app: App = None


def run():
    global verbose
    global app
    if args.verbose:
        verbose = True
    log_watcher = LogWatcher(log_directory=args.log_directory)
    start_time = time.perf_counter_ns()
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("green")
    app = App(log_watcher=log_watcher)
    log_watcher.tkinter_inst = app
    app.refresh_save_code()
    end_time = time.perf_counter_ns()
    if (verbose): print(f"Init time: {(end_time - start_time) / 1e6} ms")
    app.mainloop()


if __name__ == "__main__":
    run()
    