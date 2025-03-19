from inspect import currentframe
from json import load
from locale import getdefaultlocale
from os import environ, makedirs, listdir, walk
from os.path import isdir, isfile
from os.path import join, expanduser, exists
from queue import Queue
from re import split, escape, compile as re_compile
from subprocess import check_output, run
from threading import Thread
from types import ModuleType
from typing import Any
from sys import platform


def cycle_list(list_: list | tuple):
    if len(list_) == 1:
        return list_
    return list_[1:] + list_[:1]


def human_readable_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


def get_files(root_: str = expanduser("~")) -> str:
    to_check_ = [root_]

    while to_check_:
        folder_ = to_check_.pop(0)

        try:
            contents_ = listdir(folder_)
        except PermissionError:
            continue

        for file_ in contents_:
            item = join(folder_, file_)

            if isdir(item):
                to_check_.append(item)
            elif isfile(item):
                yield item


def list_files_in_dir(root: str = "C:\\"):
    """AI GENERATED"""

    def worker_thread_(directory_, files_in_dir_, output_queue_):
        for file_name_ in files_in_dir_:
            file_path_ = join(directory_, file_name_)
            output_queue_.put(file_path_)

    file_queue_ = Queue()
    active_threads_ = []

    for current_directory_, subdirectories_, file_names_ in walk(root):
        thread_ = Thread(
            target=worker_thread_,
            args=(current_directory_, file_names_, file_queue_)
        )
        active_threads_.append(thread_)
        thread_.start()

    for thread_ in active_threads_:
        thread_.join()

    while not file_queue_.empty():
        yield file_queue_.get()


def default(current_var,
            default_value): return default_value if current_var is None else current_var


def gen_context(back: int = 1) -> dict[str, Any]:
    frame = currentframe()

    for _ in range(back):
        frame = frame.f_back

    return frame.f_locals


def re_split(input_string: str, delimiters: list[str]) -> list[str]:
    return split(f"[{''.join(map(escape, delimiters))}]", input_string)


def absorb(func):
    """Wrapper"""

    # noinspection PyUnusedLocal
    def do(*args, **kwargs):
        func()

    return do


class DefaultClass:
    def __repr__(
            self) -> str:
        def nameTo(v):
            return repr(v) if not callable(v) else v.__name__

        return f"{type(self).__name__}({", ".join([f"{nameTo(k)}: {nameTo(v)}" for k, v in self.__dict__.items()])})"


environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

aliaFolder = join(expanduser("~"), "AppData", "Local", "Alia")
makedirs(aliaFolder, exist_ok=True)

# AI generated
# noinspection SpellCheckingInspection
file_formats = {
    "txt": "text/plain",
    "html": "text/html",
    "css": "text/css",
    "js": "application/javascript",
    "json": "application/json",
    "xml": "application/xml",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "pdf": "application/pdf",
    "zip": "application/zip",
    "tar": "application/x-tar",
    "gz": "application/gzip",
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "mp4": "video/mp4",
    "avi": "video/x-msvideo",
    # "json": "application/json",
    "csv": "text/csv",
    "xls": "application/vnd.ms-excel",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "odt": "application/vnd.oasis.opendocument.text",
    "rtf": "application/rtf",
    "epub": "application/epub+zip",
    "mobi": "application/x-mobipocket-ebook",
    "zipx": "application/x-zip-compressed",
    "7z": "application/x-7z-compressed",
    "rar": "application/x-rar-compressed",
    "flac": "audio/flac",
    "ogg": "audio/ogg",
    "webm": "video/webm",
    "mov": "video/quicktime",
    "psd": "image/vnd.adobe.photoshop",
    "ai": "application/postscript",
    "svg": "image/svg+xml",
    "tiff": "image/tiff",
    "woff": "font/woff",
    "woff2": "font/woff2",
    "ttf": "font/ttf",
    "otf": "font/otf",
    "md": "text/markdown",
    "yaml": "text/yaml",
    "sql": "application/sql",
    "apk": "application/vnd.android.package-archive",
    "jar": "application/java-archive",
    "dmg": "application/x-apple-diskimage",
    "iso": "application/x-iso9660-image",
    "exe": "application/vnd.microsoft.portable-executable"
}

keys = load(open(c)) if exists(
    c := join(expanduser("~"), "Code", "keys.json")) else {}

# AI generated
region_datetime_formats = {
    "AF": {"date": "%Y/%m/%d", "time": "%H:%M:%S"},  # Afghanistan
    "AL": {"date": "%d/%m/%Y", "time": "%H:%M:%S"},  # Albania
    "DZ": {"date": "%d/%m/%Y", "time": "%H:%M:%S"},  # Algeria
    "AD": {"date": "%d/%m/%Y", "time": "%H:%M:%S"},  # Andorra
    "AO": {"date": "%d/%m/%Y", "time": "%H:%M:%S"},  # Angola
    "AR": {"date": "%d/%m/%Y", "time": "%H:%M:%S"},  # Argentina
    # Australia (12-hour format)
    "AU": {"date": "%d/%m/%Y", "time": "%I:%M:%S %p"},
    "AT": {"date": "%d.%m.%Y", "time": "%H:%M:%S"},  # Austria
    "BR": {"date": "%d/%m/%Y", "time": "%H:%M:%S"},  # Brazil
    # Canada (12-hour format)
    "CA": {"date": "%m/%d/%Y", "time": "%I:%M:%S %p"},
    "CN": {"date": "%Y-%m-%d", "time": "%H:%M:%S"},  # China
    "DE": {"date": "%d.%m.%Y", "time": "%H:%M:%S"},  # Germany
    # Egypt (12-hour format)
    "EG": {"date": "%d/%m/%Y", "time": "%I:%M:%S %p"},
    "FR": {"date": "%d/%m/%Y", "time": "%H:%M:%S"},  # France
    # India (12-hour format)
    "IN": {"date": "%d/%m/%Y", "time": "%I:%M:%S %p"},
    "IT": {"date": "%d/%m/%Y", "time": "%H:%M:%S"},  # Italy
    "JP": {"date": "%Y/%m/%d", "time": "%H:%M:%S"},  # Japan
    "KR": {"date": "%Y.%m.%d", "time": "%H:%M:%S"},  # South Korea
    "MX": {"date": "%d/%m/%Y", "time": "%H:%M:%S"},  # Mexico
    "NL": {"date": "%d-%m-%Y", "time": "%H:%M:%S"},  # Netherlands
    # New Zealand (12-hour format)
    "NZ": {"date": "%d/%m/%Y", "time": "%I:%M:%S %p"},
    # Pakistan (12-hour format)
    "PK": {"date": "%d/%m/%Y", "time": "%I:%M:%S %p"},
    "PL": {"date": "%d.%m.%Y", "time": "%H:%M:%S"},  # Poland
    "RU": {"date": "%d.%m.%Y", "time": "%H:%M:%S"},  # Russia
    # Saudi Arabia (12-hour format)
    "SA": {"date": "%d/%m/%Y", "time": "%I:%M:%S %p"},
    "SE": {"date": "%Y-%m-%d", "time": "%H:%M:%S"},  # Sweden
    "GB": {"date": "%d/%m/%Y", "time": "%H:%M:%S"},  # United Kingdom
    # United States (12-hour format)
    "US": {"date": "%m/%d/%Y", "time": "%I:%M:%S %p"},
}


def get_country_code(): return getdefaultlocale()[0].split("_")[-1]


def get_connected_wifi():
    # AI generated

    output = check_output("netsh wlan show interfaces",
                          shell=True, universal_newlines=True)

    wifi_info = {}

    pattern = re_compile(r"^\s*(?P<key>[\w\s]+):\s*(?P<value>.+)$")

    for line in output.splitlines():
        match = pattern.match(line)
        if match and line.startswith("    "):
            key = match.group("key").strip()
            value = match.group("value").strip()
            wifi_info[key] = value

    return wifi_info


def is_dark_mode():
    # AI generated

    if platform.startswith("win"):
        try:
            from winreg import OpenKey, QueryValueEx, HKEY_CURRENT_USER
            key = OpenKey(
                HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = QueryValueEx(key, "AppsUseLightTheme")
            return value == 0  # 0 = Dark Mode, 1 = Light Mode

        except Exception:
            return False  # Default to light mode if key doesn't exist

    elif platform.startswith("darwin"):  # macOS
        try:
            result = run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip().lower() == "dark"

        except Exception:
            return False  # Default to light mode if setting not found

    elif platform.startswith("linux"):  # Linux (GNOME-based)
        try:
            result = run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                capture_output=True,
                text=True
            )
            return "dark" in result.stdout.strip().lower()

        except Exception:
            return False  # Default to light mode

    return False  # Default to light mode if OS is unknown


def gen_all(include_hidden: bool = False) -> list[str]:
    return [
        name for name, obj in globals().items() if
        (include_hidden and not name.startswith("_")) and
        not isinstance(obj, ModuleType)
    ]


class String(str):
    def __neg__(self):
        return self[::-1]
    

Class = DefaultClass

__all__ = ["aliaFolder", "cycle_list", "human_readable_size", "get_files", "list_files_in_dir", "default",
           "gen_context", "re_split", "absorb", "DefaultClass", "file_formats", "keys", "aliaFolder",
           "region_datetime_formats", "get_country_code", "get_connected_wifi", "is_dark_mode", "Class", "String"]

if __name__ == '__main__':
    # DEBUGGING
    # TODO

    class Example:
        def __getitem__(self, args: slice):
            print(args.start, args.stop, args.step)

    test = Example()
    print(test["start":"stop":"step"])
