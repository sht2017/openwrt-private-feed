import json
import subprocess
import tempfile
import shutil
from pathlib import Path

WORKSPACE = Path(__file__).parent.resolve()

with open("package_list.json", "r", encoding="utf-8") as f:
    package_list: list[dict[str, str | list[dict[str, str]]]] = json.load(f)

for source in package_list:
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            f"git clone --depth=1 {f'--branch {source["branch"]} ' if 'branch' in source else ''}{source['remote']} {temp_dir}",
            check=True,
            shell=True,
        )
        for package in source["packages"]:
            remote = Path(temp_dir) / package["remote"]
            local = (WORKSPACE / package["local"]).resolve()
            if not str(local).startswith(str(WORKSPACE)):
                print(f"Skipping unsafe path: {local}")
                continue
            if remote.exists():
                local.parent.mkdir(parents=True, exist_ok=True)
                if remote.is_file():
                    local.unlink(missing_ok=True)
                    shutil.copy2(remote, local)
                    print(f"[file] Updated {local} from {source['remote']}")
                    continue
                if remote.is_dir():
                    shutil.rmtree(local, ignore_errors=True)
                    shutil.copytree(
                        remote,
                        local,
                        dirs_exist_ok=True,
                    )
                    print(f"[dir] Updated {local} from {source['remote']}")
                    continue
                print(f"Unknown type for {remote}, skipping")
            else:
                print(f"Package {package} not found in {source['remote']}")
