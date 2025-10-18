import flet as ft
import subprocess
from threading import Thread

def get_pacman_packages():
    try:
        output = subprocess.check_output(["pacman", "-Q"], text=True)
        return [line.split()[0] for line in output.splitlines()]
    except Exception as e:
        return [f"Error: {e}"]

def get_flatpak_packages():
    try:
        output = subprocess.check_output(["flatpak", "list"], text=True)
        packages = []
        for line in output.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            appid = next((p for p in parts if p.count(".") >= 2), None)
            if appid:
                name_index = parts.index(appid)
                friendly_name = " ".join(parts[:name_index])
                packages.append((friendly_name, appid))
        return packages
    except Exception as e:
        return [("Error", f"{e}")]


def search_pacman(query):
    try:
        output = subprocess.check_output(["pacman", "-Ss", query], text=True)
        results = []
        for line in output.splitlines():
            if not line.startswith(" "):
                repo_pkg = line.split()[0]
                pkgname = repo_pkg.split("/")[1]
                results.append(pkgname)
        return results
    except Exception as e:
        return [f"Error: {e}"]

def search_flatpak(query):
    try:
        output = subprocess.check_output(["flatpak", "search", query], text=True)
        results = []
        for line in output.splitlines()[1:]:
            parts = line.split()
            if len(parts) < 2:
                continue
            appid = next((p for p in parts if p.count(".") >= 2), None)
            if appid:
                name_index = parts.index(appid)
                friendly_name = " ".join(parts[:name_index])
                results.append((friendly_name, appid))
        return results
    except Exception as e:
        return [("Error", f"{e}")]


def run_command(cmd, password):
    cmd = ["sudo", "-S"] + cmd
    try:
        proc = subprocess.run(cmd, input=password + "\n", text=True, capture_output=True)
        return proc.returncode == 0, proc.stdout.strip() if proc.returncode == 0 else proc.stderr.strip()
    except Exception as e:
        return False, str(e)

def remove_packages(packages, is_flatpak, password):
    if not packages: return "No packages selected."
    cmd = (["flatpak", "uninstall", "-y"] + packages) if is_flatpak else (["pacman", "-Rns", "--noconfirm"] + packages)
    ok, msg = run_command(cmd, password)
    return f"Removed: {', '.join(packages)}" if ok else f"Error: {msg}"

def install_packages(packages, is_flatpak, password):
    if not packages: return "No packages selected."
    cmd = (["flatpak", "install", "-y", "flathub"] + packages) if is_flatpak else (["pacman", "-S", "--noconfirm"] + packages)
    ok, msg = run_command(cmd, password)
    return f"Installed: {', '.join(packages)}" if ok else f"Error: {msg}"

def main(page: ft.Page):
    page.title = "Package Manager"
    page.window_maximized = True
    page.padding = 10
    page.vertical_alignment = ft.MainAxisAlignment.START

    status_text = ft.Text("", color="green")
    sudo_field = ft.TextField(label="Sudo Password", password=True, can_reveal_password=True, expand=True)

    pacman_checks_un, flatpak_checks_un = [], []
    pacman_list_un, flatpak_list_un = ft.ListView(expand=True), ft.ListView(expand=True)

    pacman_checks_in, flatpak_checks_in = [], []
    pacman_list_in, flatpak_list_in = ft.ListView(expand=True), ft.ListView(expand=True)

    def make_section(title, listview):
        return ft.Column(
            [ft.Text(title, weight=ft.FontWeight.BOLD),
             ft.Container(content=listview, expand=True, border=ft.border.all(1,"grey"))],
            expand=True)

    uninstall_frame = ft.Row([make_section("Pacman Packages", pacman_list_un),
                              make_section("Flatpak Packages", flatpak_list_un)], expand=True)
    install_frame = ft.Row([make_section("Pacman Search Results", pacman_list_in),
                            make_section("Flatpak Search Results", flatpak_list_in)], expand=True)

    all_pacman, all_flatpak = [], []

    def load_installed():
        nonlocal all_pacman, all_flatpak
        all_pacman, all_flatpak = get_pacman_packages(), get_flatpak_packages()
        filter_uninstall()

    def filter_uninstall(e=None):
        q = (search_box_un.value or "").lower()
        pacman_list_un.controls, flatpak_list_un.controls = [], []
        pacman_checks_un.clear(); flatpak_checks_un.clear()
        for pkg in all_pacman:
            if q in pkg.lower():
                cb = ft.Checkbox(label=pkg, data=pkg)
                pacman_checks_un.append(cb)
                pacman_list_un.controls.append(cb)
        for name, appid in all_flatpak:
            if q in name.lower() or q in appid.lower():
                cb = ft.Checkbox(label=f"{name} ({appid})", data=appid)
                flatpak_checks_un.append(cb)
                flatpak_list_un.controls.append(cb)
        page.update()

    def do_uninstall(password):
        pac_sel = [cb.data for cb in pacman_checks_un if cb.value]
        flat_sel = [cb.data for cb in flatpak_checks_un if cb.value]
        results = []
        if pac_sel: results.append(remove_packages(pac_sel, False, password))
        if flat_sel: results.append(remove_packages(flat_sel, True, password))
        load_installed()
        status_text.value = " | ".join(results); page.update()

    def uninstall_selected(e):
        pwd = sudo_field.value
        if not pwd:
            status_text.value="Please enter your sudo password."; page.update(); return
        status_text.value="Removing packages..."; page.update()
        Thread(target=do_uninstall, args=(pwd,)).start()

    def search_repos(e=None):
        q = (search_box_in.value or "").strip()
        if not q: return
        pacman_list_in.controls, flatpak_list_in.controls = [], []
        pacman_checks_in.clear(); flatpak_checks_in.clear()
        for pkg in search_pacman(q):
            cb = ft.Checkbox(label=pkg, data=pkg)
            pacman_checks_in.append(cb)
            pacman_list_in.controls.append(cb)
        for name, appid in search_flatpak(q):
            cb = ft.Checkbox(label=f"{name} ({appid})", data=appid)
            flatpak_checks_in.append(cb)
            flatpak_list_in.controls.append(cb)
        page.update()

    def do_install(password):
        pac_sel = [cb.data for cb in pacman_checks_in if cb.value]
        flat_sel = [cb.data for cb in flatpak_checks_in if cb.value]
        results = []
        if pac_sel:
            results.append(install_packages(pac_sel, False, password))
        if flat_sel:
            results.append(install_packages(flat_sel, True, password))
        load_installed()
        status_text.value = " | ".join(results); page.update()

    def install_selected(e):
        pwd = sudo_field.value
        if not pwd:
            status_text.value="Please enter your sudo password."; page.update(); return
        status_text.value="Installing packages..."; page.update()
        Thread(target=do_install, args=(pwd,)).start()

    search_box_un = ft.TextField(label="Search installed packages", on_change=filter_uninstall)
    search_box_in = ft.TextField(label="Search repositories", on_submit=search_repos)

    uninstall_tab = ft.Tab(
        text="Uninstall",
        content=ft.Column([
            ft.Container(height=10),
            search_box_un,
            ft.Container(content=uninstall_frame, expand=True),
            ft.Divider(),
            ft.Row([sudo_field, ft.ElevatedButton("Remove Selected", on_click=uninstall_selected)]),
        ], expand=True, spacing=10)
    )

    install_tab = ft.Tab(
        text="Install",
        content=ft.Column([
            ft.Container(height=10),
            search_box_in,
            ft.Container(content=install_frame, expand=True),
            ft.Divider(),
            ft.Row([sudo_field, ft.ElevatedButton("Install Selected", on_click=install_selected)]),
        ], expand=True, spacing=10)
    )

    tabs = ft.Tabs(selected_index=0, tabs=[uninstall_tab, install_tab], expand=True)
    page.add(tabs)
    page.add(status_text)


    Thread(target=load_installed).start()

ft.app(target=main)
