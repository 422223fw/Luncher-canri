import json
import shutil
import threading
import zipfile
from pathlib import Path

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput

DEFAULT_SETTINGS = {
    "github_owner": "422223fw",
    "github_repo": "canri_ai",
    "asset_name_contains": "android",
    "github_token": "",
}


class LauncherScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.releases = []
        self.selected_release = None

        root = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(18))
        root.add_widget(Label(text="[b]CANRI Android Launcher[/b]", markup=True,
                              font_size="26sp", size_hint_y=None, height=dp(58)))
        self.status = Label(text="מוכן", halign="center", valign="middle",
                            size_hint_y=None, height=dp(70))
        root.add_widget(self.status)

        self.version_button = Button(text="בחר גרסה", size_hint_y=None, height=dp(52))
        self.version_button.bind(on_release=self.open_versions)
        root.add_widget(self.version_button)

        refresh = Button(text="רענן גרסאות מ-GitHub", size_hint_y=None, height=dp(52))
        refresh.bind(on_release=lambda *_: self.refresh_releases())
        root.add_widget(refresh)

        install = Button(text="הורד והתקן את הגרסה", size_hint_y=None, height=dp(58))
        install.bind(on_release=lambda *_: self.install_selected())
        root.add_widget(install)

        run_button = Button(text="הפעל CANRI", size_hint_y=None, height=dp(58))
        run_button.bind(on_release=lambda *_: self.run_canri())
        root.add_widget(run_button)

        settings = Button(text="הגדרות GitHub", size_hint_y=None, height=dp(48))
        settings.bind(on_release=lambda *_: self.open_settings())
        root.add_widget(settings)

        root.add_widget(Label(
            text="גרסת CANRI חייבת להיות מותאמת לאנדרואיד ולהכיל canri_entry.py עם build_screen().",
            font_size="13sp", halign="center", valign="middle"))
        self.add_widget(root)

    @property
    def app(self):
        return App.get_running_app()

    def on_pre_enter(self, *args):
        Clock.schedule_once(lambda *_: self.refresh_releases(), 0.3)

    def set_status(self, text):
        Clock.schedule_once(lambda *_: setattr(self.status, "text", text), 0)

    def auth_headers(self):
        token = self.app.settings_data.get("github_token", "").strip()
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "CANRI-Android-Launcher",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def refresh_releases(self):
        self.set_status("מחפש גרסאות...")
        threading.Thread(target=self._refresh_worker, daemon=True).start()

    def _refresh_worker(self):
        s = self.app.settings_data
        url = f"https://api.github.com/repos/{s['github_owner']}/{s['github_repo']}/releases"
        try:
            r = requests.get(url, headers=self.auth_headers(), timeout=30)
            r.raise_for_status()
            needle = s.get("asset_name_contains", "android").lower().strip()
            found = []
            for release in r.json():
                for asset in release.get("assets", []):
                    name = asset.get("name", "")
                    if name.lower().endswith(".zip") and (not needle or needle in name.lower()):
                        found.append({
                            "tag": release.get("tag_name", "ללא שם"),
                            "asset": asset,
                        })
                        break
            self.releases = found
            if found:
                self.selected_release = found[0]
                Clock.schedule_once(lambda *_: setattr(
                    self.version_button, "text", f"גרסה: {found[0]['tag']}"), 0)
                self.set_status(f"נמצאו {len(found)} גרסאות Android.")
            else:
                self.set_status("לא נמצאו קובצי ZIP ששמם מתאים לאנדרואיד.")
        except requests.HTTPError as exc:
            code = exc.response.status_code if exc.response is not None else "?"
            if code == 404:
                self.set_status("המאגר לא נמצא או פרטי. במאגר פרטי יש להזין Token.")
            elif code == 401:
                self.set_status("ה-Token אינו תקין או חסר הרשאה.")
            else:
                self.set_status(f"שגיאת GitHub: HTTP {code}")
        except Exception as exc:
            self.set_status(f"שגיאה: {exc}")

    def open_versions(self, *_):
        if not self.releases:
            self.set_status("אין גרסאות לבחירה. לחץ על רענון.")
            return
        dropdown = DropDown()
        for release in self.releases:
            b = Button(text=release["tag"], size_hint_y=None, height=dp(48))
            b.bind(on_release=lambda _, rel=release: self.choose_release(dropdown, rel))
            dropdown.add_widget(b)
        dropdown.open(self.version_button)

    def choose_release(self, dropdown, release):
        self.selected_release = release
        self.version_button.text = f"גרסה: {release['tag']}"
        dropdown.dismiss()
        self.set_status(f"נבחרה גרסה {release['tag']}.")

    def install_selected(self):
        if not self.selected_release:
            self.set_status("בחר גרסה תחילה.")
            return
        self.set_status("מוריד את CANRI...")
        threading.Thread(target=self._install_worker, daemon=True).start()

    def _install_worker(self):
        release = self.selected_release
        try:
            r = requests.get(release["asset"]["url"], headers={**self.auth_headers(),
                             "Accept": "application/octet-stream"}, timeout=120, stream=True)
            r.raise_for_status()

            app_dir = self.app.user_data_path_obj
            temp_zip = app_dir / "canri_download.zip"
            staging = app_dir / "canri_staging"
            installed = app_dir / "canri_installed"

            if staging.exists():
                shutil.rmtree(staging)
            staging.mkdir(parents=True)

            with open(temp_zip, "wb") as f:
                for chunk in r.iter_content(256 * 1024):
                    if chunk:
                        f.write(chunk)

            with zipfile.ZipFile(temp_zip) as archive:
                archive.extractall(staging)

            matches = list(staging.rglob("canri_entry.py"))
            if not matches:
                raise RuntimeError("ה-ZIP אינו מכיל canri_entry.py")

            package_root = matches[0].parent
            new_dir = app_dir / "canri_new"
            if new_dir.exists():
                shutil.rmtree(new_dir)
            shutil.copytree(package_root, new_dir)

            if installed.exists():
                shutil.rmtree(installed)
            new_dir.rename(installed)

            (app_dir / "installed_version.json").write_text(
                json.dumps({"tag": release["tag"]}, ensure_ascii=False, indent=2),
                encoding="utf-8")
            temp_zip.unlink(missing_ok=True)
            shutil.rmtree(staging, ignore_errors=True)
            self.set_status(f"גרסה {release['tag']} הותקנה בהצלחה.")
        except Exception as exc:
            self.set_status(f"ההתקנה נכשלה: {exc}")

    def run_canri(self):
        installed = self.app.user_data_path_obj / "canri_installed"
        if not (installed / "canri_entry.py").exists():
            self.set_status("CANRI עדיין לא מותקן.")
            return
        try:
            widget = self.app.load_canri_widget(installed)
            self.app.canri_screen.clear_widgets()
            self.app.canri_screen.add_widget(widget)
            self.app.manager.current = "canri"
        except Exception as exc:
            self.set_status(f"לא ניתן להפעיל את CANRI: {exc}")

    def open_settings(self):
        d = self.app.settings_data
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        owner = TextInput(text=d.get("github_owner", ""), hint_text="GitHub owner", multiline=False)
        repo = TextInput(text=d.get("github_repo", ""), hint_text="Repository", multiline=False)
        needle = TextInput(text=d.get("asset_name_contains", "android"),
                           hint_text="מילה בשם קובץ ה-ZIP", multiline=False)
        token = TextInput(text=d.get("github_token", ""), hint_text="GitHub Token",
                          multiline=False, password=True)
        for label, widget in [("GitHub owner", owner), ("Repository", repo),
                              ("Asset name contains", needle), ("Token — אין לשתף", token)]:
            content.add_widget(Label(text=label))
            content.add_widget(widget)
        buttons = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        save = Button(text="שמור")
        cancel = Button(text="ביטול")
        buttons.add_widget(save)
        buttons.add_widget(cancel)
        content.add_widget(buttons)
        popup = Popup(title="הגדרות", content=content, size_hint=(0.92, 0.88))

        def do_save(*_):
            self.app.settings_data.update({
                "github_owner": owner.text.strip(),
                "github_repo": repo.text.strip(),
                "asset_name_contains": needle.text.strip(),
                "github_token": token.text.strip(),
            })
            self.app.save_settings()
            popup.dismiss()
            self.refresh_releases()

        save.bind(on_release=do_save)
        cancel.bind(on_release=popup.dismiss)
        popup.open()


class CanriScreen(Screen):
    pass


class CanriAndroidLauncher(App):
    def build(self):
        self.title = "CANRI Launcher"
        self.user_data_path_obj = Path(self.user_data_dir)
        self.user_data_path_obj.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.user_data_path_obj / "launcher_settings.json"
        self.settings_data = self.load_settings()
        self.manager = ScreenManager()
        self.launcher_screen = LauncherScreen(name="launcher")
        self.canri_screen = CanriScreen(name="canri")
        self.manager.add_widget(self.launcher_screen)
        self.manager.add_widget(self.canri_screen)
        return self.manager

    def load_settings(self):
        if not self.settings_file.exists():
            return dict(DEFAULT_SETTINGS)
        try:
            loaded = json.loads(self.settings_file.read_text(encoding="utf-8"))
            result = dict(DEFAULT_SETTINGS)
            result.update(loaded)
            return result
        except Exception:
            return dict(DEFAULT_SETTINGS)

    def save_settings(self):
        self.settings_file.write_text(
            json.dumps(self.settings_data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_canri_widget(self, package_dir):
        import importlib.util
        import sys
        name = "downloaded_canri_entry"
        sys.modules.pop(name, None)
        path = package_dir / "canri_entry.py"
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError("לא ניתן לטעון את canri_entry.py")
        module = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(package_dir))
        try:
            spec.loader.exec_module(module)
        finally:
            if str(package_dir) in sys.path:
                sys.path.remove(str(package_dir))
        build_screen = getattr(module, "build_screen", None)
        if not callable(build_screen):
            raise RuntimeError("חסרה פונקציה build_screen()")
        return build_screen(on_back=lambda: setattr(self.manager, "current", "launcher"))


if __name__ == "__main__":
    CanriAndroidLauncher().run()
