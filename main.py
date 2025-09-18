from pathlib import Path
import os, sys
from hashlib import sha256
import requests
import stat
import time
from psutil import process_iter
import urllib.request
from tkinter import Tk, Canvas, Button, Label, PhotoImage, messagebox
from PIL import Image, ImageTk
from platform import system as sysoschk
from shutil import copyfile
from subprocess import run as runproc
from subprocess import Popen, TimeoutExpired
from subprocess import PIPE as sPIPE
import threading
if sysoschk() == "Windows":
    import ctypes

# theres a shit ton of repeating code, weird formatting, pointless if statements and all that stuff
# i wanted this to be organized but i went insane and lazy in the middle of doing that
# will fix that later tho

def run_as_admin_and_wait(cmd_str):
    if sysoschk() == "Windows":
        try:
            if ctypes.windll.shell32.IsUserAnAdmin():
                result = runproc(cmd_str, shell=True, stdout=sPIPE, stderr=sPIPE)
                return result.returncode == 0
            else:
                params = f'/c {cmd_str}'
                ret = ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", "cmd.exe", params, None, 1
                )
                return ret > 32
        except Exception as e:
            print("Failed to run admin command:", e)
            return False

class LauncherWindow:
    def __init__(self):
        self.dotstate = 1
        self.base_string = "Verifying"

        self.xwin = 0
        self.ywin = 0
        self.window = Tk()
        self.setup_window()
        self.create_widgets()
        self.bind_events()
        self.window.iconphoto(False, PhotoImage(file=self.relative_to_assets("icon.png")))

        self.window.after(1, self.dot_anim)
        self.window.attributes('-alpha', 0.0)
        self.window.after(1, self.fade_in)

        self.disabled_chk = PhotoImage(file=self.relative_to_assets("check_n.png"))
        self.enabled_chk = PhotoImage(file=self.relative_to_assets("check_y.png"))
        self.chkstate = False
        self.chkstate2 = False
        self.isdotanim = False
        self.isplayon = True
        self.isaware = False
        self.hollup = False
        
        self.setup_settings()

        self.window.resizable(False, False)
        self.window.mainloop()

    def get_pos(self, event):
        self.xwin = event.x_root - self.window.winfo_x()
        self.ywin = event.y_root - self.window.winfo_y()

    def bootstrap(self, event):
        if self.chkstate and self.chkstate2 and self.isplayon:
            self.isplayon = False
            self.isdotanim = True
            self.base_string = "Launching"
            self.text.configure(bg="#2B1F2E")

            def task():
                if sysoschk() == 'Linux':
                    url = "https://github.com/ppy/osu/releases/latest/download/osu.AppImage"
                    local_path = os.path.expanduser("~/.local/share/m1pplazer/osu.AppImage")
                    todl = False
                    try:
                        proc = Popen([local_path])
                        proc.wait(timeout=1)
                        if proc.returncode != 0:
                            todl = True
                            try:
                                os.remove(local_path)
                            except:
                                pass
                    except TimeoutExpired:
                        self.window.after(0, self.close_window)
                    except Exception:
                        todl = True
                        try:
                            os.remove(local_path)
                        except:
                            pass
                    try:
                        if not os.path.exists(local_path) or todl:
                            self.window.after(0, lambda: setattr(self, 'base_string', "Download"))
                            urllib.request.urlretrieve(url, local_path)
                            st = os.stat(local_path)
                            os.chmod(local_path, st.st_mode | stat.S_IEXEC)
                            proc = Popen([local_path])
                            self.window.after(0, self.close_window)
                    except Exception as e:
                        def show_error():
                            self.window.withdraw()
                            messagebox.showerror(title="Error!", message="Unable to download file. Check your disk space and try again\n\n" + str(e))
                            self.window.destroy()
                            self.close_window()
                        self.window.after(0, show_error)
                elif sysoschk() == 'Windows':
                    url = "https://github.com/ppy/osu/releases/latest/download/install.exe"
                    local_path = os.path.join(os.getenv("LOCALAPPDATA"), "osulazer", "current", "osu!.exe")
                    install_path = os.path.join(os.getenv("APPDATA"), "m1pplazer", "install.exe")
                    todl = False
                    try:
                        proc = Popen([local_path])
                        proc.wait(timeout=1)
                        if proc.returncode != 0:
                            todl = True
                    except TimeoutExpired:
                        self.hollup = True
                        self.window.after(0, self.close_window)
                    except Exception:
                        todl = True
                    try:
                        if todl:
                            self.window.after(0, lambda: setattr(self, 'base_string', "Download"))
                            urllib.request.urlretrieve(url, install_path)
                            proc2 = Popen([install_path]).wait(timeout=120)
                            if proc2.returncode != 0:
                                self.hollup = True
                                proc2 = Popen([local_path])
                                self.window.after(0, self.close_window)
                            else:
                                raise Exception("Unknown error")
                    except Exception as ex:
                        def show_error():
                            self.window.withdraw()
                            messagebox.showerror(title="Error!", message="Unable to download file. Check your disk space and try again\n\n" + str(ex))
                            self.window.destroy()
                            self.close_window()
                        self.window.after(0, show_error)
            threading.Thread(target=task, daemon=True).start()

    def setup_settings(self):
        found = False
        if sysoschk() == 'Linux':
            pathdir = os.path.isfile(os.getenv("HOME") + "/.local/share/osu/rulesets/osu.Game.Rulesets.AuthlibInjection.dll")
            with open("/etc/hosts", "r") as f:
                for line in f:
                    if "ppy.sh" in line:
                        found = True
                        break
        elif sysoschk() == 'Windows':
            appdata_path = os.getenv("APPDATA")
            if appdata_path:
                pathdir = os.path.isfile(os.path.join(appdata_path, "osu", "rulesets", "osu.Game.Rulesets.AuthlibInjection.dll"))

            hosts_path = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts")
            try:
                with open(hosts_path, "r") as f:
                    for line in f:
                        if "ppy.sh" in line:
                            found = True
                            break
            except Exception as e:
                print(f"Error reading hosts file: {e}")
        if found:
            self.button_check.configure(image=self.enabled_chk)
            self.chkstate = True
        if pathdir:
            self.button_check2.configure(image=self.enabled_chk)
            self.chkstate2 = True
        self.checkstatusedit()

    def checkstatusedit(self):
        if self.chkstate and self.chkstate2:
            self.warntext.configure(text="All good", fg="#53FD61")
        else:
            self.warntext.configure(text="Please check all the boxes to continue", fg="#FD5353")
    def unload_injector(self):
        try:
            if sysoschk() == 'Linux': 
                os.remove(os.getenv("HOME") + "/.local/share/osu/rulesets/osu.Game.Rulesets.AuthlibInjection.dll")
            elif sysoschk() == 'Windows':
                os.remove(os.path.join(os.getenv("APPDATA"), "osu", "rulesets", "osu.Game.Rulesets.AuthlibInjection.dll"))
        except Exception as e:
            self.window.withdraw()
            messagebox.showerror(title="Error!", message="Unable to delete file. Close osu!lazer and try again\n\n" + str(e))
            self.window.destroy()
    def load_injector(self):
        if sysoschk() == 'Linux':
            topath = os.getenv("HOME") + "/.local/share/m1pplazer"
        if sysoschk() == 'Windows':
            topath = os.getenv("APPDATA") + "\\m1pplazer"
            
        url = "https://github.com/MingxuanGame/LazerAuthlibInjection/releases/latest/download/osu.Game.Rulesets.AuthlibInjection.dll"
        filename = "osu.Game.Rulesets.AuthlibInjection.dll"
        try:
            h = sha256()
            with open(os.path.join(topath, filename), "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            calculated_sha256 = h.hexdigest() 
        except:
            calculated_sha256 = 0
        if not os.path.isfile(os.path.join(topath, filename)) or not requests.get("https://assets.m1pposu.dev/lazer/injector_sha.txt").text == calculated_sha256:
            try:
                os.remove(os.path.join(topath, filename))
            except Exception as e:
                print(str(e))
            self.isdotanim = True
            self.isplayon = False
            self.text.configure(bg="#2B1F2E")
            self.base_string = "Download"
            try:
                os.makedirs(topath, exist_ok=True)
                dest_file = os.path.join(topath, filename)
                response = requests.get(url)
                response.raise_for_status()
                with open(dest_file, "wb") as f:
                    f.write(response.content)
            except Exception as e:
                self.window.withdraw()
                messagebox.showerror(title="Error!", message="Unable to download file. Check your internet connection and try again\n\n" + str(e))
                self.window.destroy()
        try:
            try:
                if sysoschk() == "Linux":
                    os.remove(os.getenv("HOME") + "/.local/share/osu/rulesets/" + filename)
                elif sysoschk() == 'Windows':
                    os.remove(os.path.join(os.getenv("APPDATA"), "osu", "rulesets", "osu.Game.Rulesets.AuthlibInjection.dll"))
            except:
                pass
            if sysoschk() == "Linux":
                os.makedirs(os.getenv("HOME") + "/.local/share/osu/rulesets/", exist_ok=True)
                copyfile(os.path.join(topath, filename), os.getenv("HOME") + "/.local/share/osu/rulesets/" + filename)
                with open(os.getenv("HOME") + "/.local/share/osu/authlib_local_config.json", "w") as f:
                    f.write('{"ApiUrl":"https://lazer-api.m1pposu.dev","WebsiteUrl":"https://lazer.m1pposu.dev","ClientId":"","ClientSecret":"","SpectatorUrl":"","MultiplayerUrl":"","MetadataUrl":"","BeatmapSubmissionServiceUrl":""}')
            if sysoschk() == "Windows":
                os.makedirs(os.path.join(os.getenv("APPDATA"), r"osu\rulesets"), exist_ok=True)
                copyfile(os.path.join(topath, filename), os.path.join(os.getenv("APPDATA"), r"osu\rulesets", filename))
                with open(os.getenv("APPDATA") + "/osu/authlib_local_config.json", "w") as f:
                    f.write('{"ApiUrl":"https://lazer-api.m1pposu.dev","WebsiteUrl":"https://lazer.m1pposu.dev","ClientId":"","ClientSecret":"","SpectatorUrl":"","MultiplayerUrl":"","MetadataUrl":"","BeatmapSubmissionServiceUrl":""}')
            self.isdotanim = False
            self.isplayon = True
            self.text.configure(bg="#603D69", text="  Launch  ")
        except Exception as e:
            self.window.withdraw()
            messagebox.showerror(title="Error!", message="Unable to copy file. Check your disk space and try again\n\n" + str(e))
            self.window.destroy()
            
            

    def move_window(self, event):
        if 0 <= self.xwin <= 403 and 0 <= self.ywin <= 36:
            new_x = event.x_root - self.xwin
            new_y = event.y_root - self.ywin
            self.window.geometry(f'+{new_x}+{new_y}')

    def relative_to_assets(self, path: str) -> Path:
        try:
            base_path = Path(sys._MEIPASS)
        except Exception:
            if getattr(sys, "frozen", False):
                base_path = Path(sys.executable).parent
            else:
                base_path = Path(__file__).parent

        ASSETS_PATH = base_path / "assets"
        return ASSETS_PATH / path

    def close_window(self, trns=1.0):
        if trns > 0:
            trns -= 0.05
            self.window.attributes('-alpha', trns)
            self.window.after(20, self.close_window, trns)
        else:
            self.window.withdraw()
            start = time.time()
            while time.time() - start < 10.0:
                processes = [p for p in process_iter(['name']) if p.info['name'] == "osu!.exe"]
                if processes or not self.hollup:
                    if self.hollup:
                        proc = processes[0]
                        proc.wait()
                    try:
                        if sysoschk() == 'Windows':
                            os.remove(os.path.join(os.getenv("APPDATA"), "osu", "rulesets", "osu.Game.Rulesets.AuthlibInjection.dll"))
                    except:
                        pass
                    try:
                        self.deactiveset(self.button_check)
                    except:
                        pass
                    sys.exit(0)
                time.sleep(1)
            sys.exit(1)

    def fade_in(self, trns=0.0):
        if not self.isaware:
            messagebox.showinfo(title="IMPORTANT, PLEASE READ", message="IMPORTANT: This is a program that configures access to M1Lazer, HOWEVER settings changed in this program affect your osu!lazer install and also disable access to ppy.sh\n\nIN ORDER TO REGAIN ACCESS TO PPY.SH AFTER A LAUNCHER CRASH YOU WILL NEED TO RUN THIS PROGRAM AGAIN AND UNCHECK ALL OF THE CHECKBOXES!!!")
            self.isaware = True
        if trns < 1.0:
            trns += 0.05
            self.window.attributes('-alpha', trns)
            self.window.after(20, self.fade_in, trns)

    def dot_anim(self):
        if self.isdotanim:
            self.dotstate += 1
            if self.dotstate > 3:
                self.dotstate = 0
            towrite = self.base_string + ("." * self.dotstate)
            self.text.configure(text=towrite)

        self.window.after(600, self.dot_anim)

    def hlbtn(self, button):
        button.configure(background='#7d0101', activeforeground='#7d0101', activebackground='#7d0101')
        self.button_2.configure(background='#7d0101', activeforeground='#7d0101', activebackground='#7d0101')

    def uhlbtn(self, button):
        button.configure(background='#3a0c0c', activeforeground='#3a0c0c', activebackground='#3a0c0c')
        self.button_2.configure(background='#3a0c0c', activeforeground='#3a0c0c', activebackground='#3a0c0c')

    def activeset(self, button):
        if sysoschk() == "Linux":
            result = runproc(["pkexec", "bash", "-c", "echo -e '127.0.0.1 ppy.sh\n127.0.0.1 osu.ppy.sh\n127.0.0.1 auth.ppy.sh\n127.0.0.1 blog.ppy.sh\n127.0.0.1 c.ppy.sh\n127.0.0.1 data.ppy.sh\n127.0.0.1 dev.ppy.sh\n127.0.0.1 docs.ppy.sh\n127.0.0.1 grafana.ppy.sh\n127.0.0.1 i.ppy.sh\n127.0.0.1 old.ppy.sh\n127.0.0.1 stmp.ppy.sh\n127.0.0.1 s.ppy.sh\n127.0.0.1 status.ppy.sh\n127.0.0.1 store.ppy.sh' >> /etc/hosts"], capture_output=True)
            if result.returncode == 0:
                button.configure(image=self.enabled_chk)
                self.chkstate = True
        elif sysoschk() == 'Windows':
            hosts_file = r"C:\Windows\System32\drivers\etc\hosts"
            lines = [ "127.0.0.1 ppy.sh", "127.0.0.1 osu.ppy.sh", "127.0.0.1 auth.ppy.sh", "127.0.0.1 blog.ppy.sh", "127.0.0.1 c.ppy.sh", "127.0.0.1 data.ppy.sh", "127.0.0.1 dev.ppy.sh", "127.0.0.1 docs.ppy.sh", "127.0.0.1 grafana.ppy.sh", "127.0.0.1 i.ppy.sh", "127.0.0.1 old.ppy.sh", "127.0.0.1 stmp.ppy.sh", "127.0.0.1 s.ppy.sh", "127.0.0.1 status.ppy.sh", "127.0.0.1 store.ppy.sh" ]
            temp_file = os.path.join(os.environ["TEMP"], "hosts_add.txt")
            with open(temp_file, "w") as f:
                with open(hosts_file, "r") as fx:
                    f.write(fx.read())
                f.write("\n".join(lines) + "\n")
            
            if run_as_admin_and_wait(f'copy "{temp_file}" "{hosts_file}" /Y'):
                button.configure(image=self.enabled_chk)
                self.chkstate = True

    def deactiveset(self, button):
        if sysoschk() == 'Linux':
            result = runproc(["pkexec", "bash", "-c", "sed -i '/ppy\\.sh/d' /etc/hosts"], capture_output=True)
            if result.returncode == 0:
                button.configure(image=self.disabled_chk)
                self.chkstate = False
        elif sysoschk() == 'Windows':
            hosts_file = r"C:\Windows\System32\drivers\etc\hosts"
            temp_file = os.path.join(os.environ["TEMP"], "hosts_clean.txt")
            with open(hosts_file, "r") as f:
                filtered = [line for line in f if "ppy.sh" not in line]
            with open(temp_file, "w") as f:
                f.writelines(filtered)
            if run_as_admin_and_wait(f'copy "{temp_file}" "{hosts_file}" /Y'):
                button.configure(image=self.disabled_chk)
                self.chkstate = False
            

    def activeset2(self, button):
        self.load_injector()
        button.configure(image=self.enabled_chk)
        self.chkstate2 = True

    def deactiveset2(self, button):
        self.unload_injector()
        button.configure(image=self.disabled_chk)
        self.chkstate2 = False

    def toggle_active(self, button, index):
        if not self.isdotanim:
            if index == 1:
                if self.chkstate:
                    self.deactiveset(button)
                else:
                    self.activeset(button)
            if index == 2:
                if self.chkstate2:
                    self.deactiveset2(button)
                else:
                    self.activeset2(button)
            self.checkstatusedit()
    def setup_window(self):
        self.window.configure(bg="#2B1F2E")
        self.window.overrideredirect(True)

        self.window.update_idletasks()
        width = 465
        height = 255
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        self.canvas = Canvas(self.window, bg="#2B1F2E", height=255, width=465, bd=0, highlightthickness=0, relief="ridge")
        self.canvas.place(x=0, y=0)
        self.canvas.create_rectangle(0.0, 0.0, 465.0, 36.0, fill="#1A121C", outline="")
        self.warntext = Label(self.window, text="Please check all the boxes to continue", fg="#FD5353", bg="#2B1F2E", font=("Nunito", 8)) 
        self.warntext.place(x=6, y=235)
        self.title_bar = Canvas(self.window, width=465, height=36)
        self.button_1 = Button(
            background='#3a0c0c', activeforeground='#3a0c0c', activebackground='#3a0c0c',
            borderwidth=0, highlightthickness=0, command=lambda: self.close_window(), relief="flat"
        )
        self.button_1.place(x=403.0, y=0.0, width=62.0, height=36.0)

        self.canvas.create_text(8.0, 8.0, anchor="nw", text="M1PP Lazer", fill="#7F538A", font=("Nunito", 15 * -1))

        self.text = Label(self.window, text="  Launch  ", fg="#D97FF0", bg="#603D69", font=("Nunito", 12)) 
        self.text.place(x=360, y=194)
        self.canvas.create_rectangle(403.0, 0.0, 465.0, 36.0, fill="#7D0000", outline="")
        
        self.button_image_2 = PhotoImage(file=self.relative_to_assets("button_2.png"))
        self.button_2 = Button(
            image=self.button_image_2, borderwidth=0, background='#3a0c0c',
            activeforeground='#3a0c0c', activebackground='#3a0c0c', highlightthickness=0,
            command=lambda: self.close_window(), relief='sunken'
        )
        self.button_2.place(x=427.0, y=9.0, width=13.0, height=20.0)

        self.image_image_1 = PhotoImage(file=self.relative_to_assets("image_1.png"))
        self.canvas.create_image(232.0, 112.0, image=self.image_image_1)

        self.canvas.place(x = 0, y = 0)
        self.canvas.create_text(
            39.0,
            181.0,
            anchor="nw",
            text="Block official servers (ppy.sh)",
            fill="#D97FF0",
            font=("Nunito Regular", 13 * -1)
        )

        self.button_check_o_img = PhotoImage(file=self.relative_to_assets("chkb.png"))
        self.button_check_o = Button(
            image=self.button_check_o_img,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.toggle_active(self.button_check, 1),
            relief="sunken",
            activeforeground="#2B1F2E",
            activebackground="#2B1F2E",
            bg = "#2B1F2E"
        )
        self.button_check_o.place(
            x=10.0,
            y=177.0,
            width=25.0,
            height=25.0
        )

        self.button_check_img = PhotoImage(
            file=self.relative_to_assets("check_n.png"))
        self.button_check = Button(
            image=self.button_check_img,
            borderwidth=0,
            highlightthickness=0,
            bg="#7F538B",
            command=lambda: self.toggle_active(self.button_check, 1),
            relief='sunken',
            activeforeground="#7F538B",
            activebackground="#7F538B"
        )
        self.button_check.place(
            x=13.0,
            y=180.0,
            width=19.0,
            height=19.0
        )



        self.canvas.create_text(
            39.0,
            213.0,
            anchor="nw",
            text="Connect to M1PP (lazer)",
            fill="#D97FF0",
            font=("Nunito Regular", 13 * -1)
        )

        self.button_check_o2 = Button(
            image=self.button_check_o_img,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.toggle_active(self.button_check2, 2),
            relief="sunken",
            activeforeground="#2B1F2E",
            activebackground="#2B1F2E",
            bg = "#2B1F2E"
        )
        self.button_check_o2.place(
            x=10.0,
            y=209.0,
            width=25.0,
            height=25.0
        )

        self.button_check2 = Button(
            image=self.button_check_img,
            borderwidth=0,
            highlightthickness=0,
            bg="#7F538B",
            command=lambda: self.toggle_active(self.button_check2, 2),
            relief='sunken',
            activeforeground="#7F538B",
            activebackground="#7F538B"
        )
        self.button_check2.place(
            x=13.0,
            y=212.0,
            width=19.0,
            height=19.0
        )

    def bind_events(self):
        self.button_1.bind("<Enter>", lambda e: self.hlbtn(self.button_1))
        self.button_1.bind("<Leave>", lambda e: self.uhlbtn(self.button_1))
        self.button_2.bind("<Enter>", lambda e: self.hlbtn(self.button_1))
        self.button_2.bind("<Leave>", lambda e: self.uhlbtn(self.button_1))
        self.window.bind("<B1-Motion>", self.move_window)
        self.window.bind("<Button-1>", self.get_pos)
        self.text.bind("<Button-1>", self.bootstrap)

if __name__ == "__main__":
    try:
        if sys.argv[1] == "cleanup":
            if sysoschk() == 'Windows':
                try:
                    for user in os.listdir(r"C:\Users"):
                        user_path = os.path.join(r"C:\Users", user)
                        appdata_path = os.path.join(user_path, "AppData", "Roaming", "osu", "rulesets", "osu.Game.Rulesets.AuthlibInjection.dll")
                        
                        if os.path.isfile(appdata_path):
                            try:
                                os.remove(appdata_path)
                            except:
                                pass
                except:
                    pass
                hosts_file = r"C:\Windows\System32\drivers\etc\hosts"
                temp_file = os.path.join(os.environ["TEMP"], "hosts_clean.txt")
                with open(hosts_file, "r") as f:
                    filtered = [line for line in f if "ppy.sh" not in line]
                with open(temp_file, "w") as f:
                    f.writelines(filtered)
                if run_as_admin_and_wait(f'copy "{temp_file}" "{hosts_file}" /Y'):
                    sys.exit(0)
                sys.exit(1)
    except IndexError:
        pass
    LauncherWindow()
