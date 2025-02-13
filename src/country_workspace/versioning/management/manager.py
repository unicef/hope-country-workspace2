import importlib.util
import re
import sys
from pathlib import Path
from typing import IO, Callable

from country_workspace import VERSION
from country_workspace.versioning.exceptions import ScriptError
from country_workspace.versioning.models import Script

regex = re.compile(r"(\d+).*")


def get_version(filename: str) -> int | None:
    if m := regex.match(filename):
        return int(m.group(1))
    return None


def get_funcs(filename: Path, direction: str = "forward") -> list[Callable]:
    if not filename.exists():  # pragma: no cover
        raise FileNotFoundError(filename)
    spec = importlib.util.spec_from_file_location(filename.stem, filename.absolute())
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    funcs = []
    for op in module.Scripts.operations:
        if isinstance(op, (list | tuple)):
            if direction == "forward":
                funcs.append(op[0])
            else:
                funcs.append(op[1])
        elif direction == "forward":
            funcs.append(op)
        else:
            funcs.append(lambda: True)

    return funcs


class Manager:
    default_folder = Path(__file__).parent.parent / "scripts"

    def __init__(self, folder: str | Path | None = None) -> None:
        self.folder = folder or self.default_folder
        self.existing = []
        self.applied = list(Script.objects.order_by("name").values_list("name", flat=True))
        self.max_version = 0
        self.max_applied_version = 0
        for applied in self.applied:
            self.max_applied_version = max(get_version(applied), self.max_applied_version)

        for filename in sorted(self.folder.iterdir()):
            if v := get_version(filename.name):
                self.existing.append(filename)
                self.max_version = max(self.max_version, v)

    def is_processed(self, entry: str) -> bool:
        return Path(entry).name in self.applied

    def zero(self, out: IO = sys.stdout) -> None:
        self.backward(0, out=out)

    def _process_file(self, entry: Path) -> list[Callable]:
        funcs = get_funcs(entry, direction="forward")
        for func in funcs:
            try:
                func()
            except Exception as e:  # pragma: no cover
                raise ScriptError(f"Error executing {entry.stem}.{func.__name__}") from e
        return funcs

    def force_apply(self) -> None:
        for entry in self.existing:
            if entry.name not in self.applied:
                self._process_file(entry)

    def forward(
        self,
        to_num: int | None = None,
        fake: bool = False,
        out: IO = sys.stdout,
    ) -> list[tuple[Path, list[Callable[[None], None]]]]:
        out.write("Upgrading...\n")
        if not to_num:
            to_num = self.max_version
        processed = []
        for entry in self.existing:
            if get_version(entry.stem) > to_num:
                break
            if entry.name not in self.applied:
                if fake:
                    out.write(f"   Applying {entry.stem} (fake)\n")
                else:
                    out.write(f"   Applying {entry.stem}\n")
                funcs = self._process_file(entry)
                Script.objects.create(name=entry.name, version=VERSION)
                processed.append((entry, funcs))
        self.applied = list(Script.objects.order_by("name").values_list("name", flat=True))
        return processed

    def backward(self, to_num: int, out: IO = sys.stdout) -> list[tuple[Path, list[Callable[[None], None]]]]:
        out.write("Downgrading...\n")
        processed = []
        for entry in reversed(self.applied):
            if get_version(entry) <= to_num:
                break
            file_path = Path(self.folder) / entry
            funcs = get_funcs(file_path, direction="backward")
            out.write(f"   Discharging {file_path.stem}\n")
            for func in funcs:
                func()
            Script.objects.get(name=file_path.name).delete()
            processed.append((entry, funcs))
        self.applied = list(Script.objects.order_by("name").values_list("name", flat=True))
        return processed
