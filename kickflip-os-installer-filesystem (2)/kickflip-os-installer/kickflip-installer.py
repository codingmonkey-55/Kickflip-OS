#!/usr/bin/env python3
import os, subprocess, threading
from pathlib import Path
import gi
gi.require_version("Gtk","3.0")
from gi.repository import Gtk, Gdk, GLib
from installer import drives, size, install

BASE=Path(__file__).resolve().parent

class App(Gtk.Window):
    def __init__(self):
        super().__init__(title="Kickflip OS Installer")
        self.set_default_size(1100,700)
        self.cfg={"hostname":"kickflip","locale":"en_US.UTF-8","keyboard":"us"}
        self.stack=Gtk.Stack()
        self.add(self.stack)
        self.css()
        self.build()
        self.show_all()

    def css(self):
        css=Gtk.CssProvider()
        css.load_from_data(b"""
        window{background:#050509;color:#fff}
        label{color:#eee}
        entry{background:#090b12;color:#fff;border:2px solid #08bff5;border-radius:8px;padding:8px}
        button{background:#101525;color:#fff;border:2px solid #08bff5;border-radius:9px;padding:10px 20px}
        button:hover{background:#f000a8;border-color:#f000a8}
        .title{font-size:30px;font-weight:800}.accent{color:#ff00aa}
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def page(self,key,title,desc):
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=14)
        box.set_margin_top(30);box.set_margin_bottom(25);box.set_margin_start(40);box.set_margin_end(40)
        t=Gtk.Label();t.set_markup(f'<span class="title">{title}</span>');t.set_xalign(0);box.pack_start(t,False,False,0)
        d=Gtk.Label(label=desc);d.set_xalign(0);box.pack_start(d,False,False,0)
        c=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=12);box.pack_start(c,True,True,0)
        nav=Gtk.Box(spacing=12);b=Gtk.Button(label="‹ Back");n=Gtk.Button(label="Next ›")
        nav.pack_start(b,False,False,0);nav.pack_end(n,False,False,0);box.pack_end(nav,False,False,0)
        self.stack.add_named(box,key);return c,b,n

    def build(self):
        c,b,n=self.page("welcome","Welcome to Kickflip OS","Same vibes. New system.")
        c.pack_start(Gtk.Label(label="Let's get your system ready to roll."),False,False,0)
        b.set_sensitive(False);n.connect("clicked",lambda *_:self.go("account"))

        c,b,n=self.page("account","Create Your Account","Your space. Your rules.")
        self.full=self.ent("Full name");self.user=self.ent("Username")
        self.pw=self.ent("Password",True);self.pw2=self.ent("Confirm password",True)
        for e in (self.full,self.user,self.pw,self.pw2):c.pack_start(e,False,False,0)
        b.connect("clicked",lambda *_:self.go("welcome"));n.connect("clicked",self.account)

        c,b,n=self.page("wifi","Connect to Wi-Fi","Stay connected. Stay rolling.")
        self.wifi=Gtk.ComboBoxText();self.refresh_wifi();c.pack_start(self.wifi,False,False,0)
        self.wpass=self.ent("Wi-Fi password",True);c.pack_start(self.wpass,False,False,0)
        self.skip=Gtk.CheckButton(label="Skip Wi-Fi setup for now");c.pack_start(self.skip,False,False,0)
        b.connect("clicked",lambda *_:self.go("account"));n.connect("clicked",lambda *_:self.go("drive"))

        c,b,n=self.page("drive","Install to Drive","Pick a drive. Make it yours.")
        self.disks=Gtk.ComboBoxText();self.refresh_disks();c.pack_start(self.disks,False,False,0)
        c.pack_start(Gtk.Label(label="⚠ Everything on the selected drive will be erased."),False,False,0)
        b.connect("clicked",lambda *_:self.go("wifi"));n.connect("clicked",self.drive)

        c,b,n=self.page("confirm","Confirm and Install","Review your choices before installation.")
        self.summary=Gtk.Label();self.summary.set_xalign(0);self.summary.set_line_wrap(True);c.pack_start(self.summary,True,True,0)
        b.connect("clicked",lambda *_:self.go("drive"));n.set_label("Install Now ›");n.connect("clicked",self.confirm)

        self.go("welcome")

    def ent(self,p,secret=False):
        e=Gtk.Entry();e.set_placeholder_text(p);e.set_visibility(not secret);return e

    def refresh_wifi(self):
        self.wifi.remove_all();self.wifi.append_text("No Wi-Fi selected")
        try:
            out=subprocess.check_output(["nmcli","-t","-f","SSID","dev","wifi"],text=True)
            for x in sorted(set(v for v in out.splitlines() if v.strip())):self.wifi.append_text(x)
        except Exception:pass
        self.wifi.set_active(0)

    def refresh_disks(self):
        self.disk_data=drives();self.disks.remove_all()
        for d in self.disk_data:self.disks.append_text(f'{d["path"]} — {size(d["size"])} — {d.get("model") or "Drive"}')
        if self.disk_data:self.disks.set_active(0)

    def account(self,*_):
        self.cfg.update(full_name=self.full.get_text().strip(),username=self.user.get_text().strip().lower(),
                        password=self.pw.get_text(),password2=self.pw2.get_text())
        if not self.cfg["full_name"] or not self.cfg["username"]:
            return self.err("Enter your name and username.")
        if self.cfg["password"]!=self.cfg["password2"]:return self.err("Passwords do not match.")
        self.go("wifi")

    def drive(self,*_):
        i=self.disks.get_active()
        if i<0:return self.err("Select an installation drive.")
        self.cfg["drive"]=self.disk_data[i]
        if self.skip.get_active():self.cfg["wifi_ssid"]="";self.cfg["wifi_password"]=""
        else:self.cfg["wifi_ssid"]=self.wifi.get_active_text() or "";self.cfg["wifi_password"]=self.wpass.get_text()
        d=self.cfg["drive"]
        self.summary.set_text(
            f'USER\n{self.cfg["full_name"]} ({self.cfg["username"]})\n\n'
            f'DRIVE\n{d["path"]} — {size(d["size"])}\n\n'
            f'WI-FI\n{self.cfg["wifi_ssid"] or "Skipped"}\n\n'
            f'INSTALL\nKickflip OS system, kernel, GRUB and desktop\n\n'
            f'WARNING\nAll data on {d["path"]} will be erased.')
        self.go("confirm")

    def confirm(self,*_):
        q=Gtk.MessageDialog(transient_for=self,flags=0,message_type=Gtk.MessageType.WARNING,
                            buttons=Gtk.ButtonsType.OK_CANCEL,text="Erase the selected drive?")
        q.format_secondary_text("This cannot be undone. Verify the drive before continuing.")
        r=q.run();q.destroy()
        if r!=Gtk.ResponseType.OK:return
        dlg=Gtk.Dialog(title="Installing Kickflip OS",transient_for=self)
        bar=Gtk.ProgressBar();lab=Gtk.Label(label="Starting…");box=dlg.get_content_area()
        box.pack_start(lab,False,False,18);box.pack_start(bar,False,False,18);dlg.show_all()
        def progress(msg):GLib.idle_add(lab.set_text,msg);GLib.idle_add(bar.pulse)
        def worker():
            try:
                install(self.cfg,progress);GLib.idle_add(done)
            except Exception as e:GLib.idle_add(fail,str(e))
        def done():
            dlg.destroy();self.err("Kickflip OS is installed! Remove the USB and reboot.");return False
        def fail(msg):
            dlg.destroy();self.err("Installation failed:\n\n"+msg);return False
        threading.Thread(target=worker,daemon=True).start()

    def go(self,k):self.stack.set_visible_child_name(k)
    def err(self,msg):
        d=Gtk.MessageDialog(transient_for=self,flags=0,message_type=Gtk.MessageType.ERROR,
                            buttons=Gtk.ButtonsType.OK,text=msg);d.run();d.destroy()

if __name__=="__main__":
    if os.geteuid()!=0:raise SystemExit("Run with pkexec or sudo.")
    a=App();a.connect("destroy",Gtk.main_quit);Gtk.main()
