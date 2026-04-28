from pathlib import Path
import sys


def _add_cram_paths() -> None:
    candidates = (
        Path("/home/jovyan/libs/cognitive_robot_abstract_machine"),
        Path("/root/libs/cognitive_robot_abstract_machine"),
        Path("/workspace/libs/cognitive_robot_abstract_machine"),
    )

    relative_paths = (
        "pycram/src",
        "krrood/src",
        "src",
    )

    for base in candidates:
        if not base.exists():
            continue
        for relative_path in relative_paths:
            path = base / relative_path
            if path.exists() and str(path) not in sys.path:
                sys.path.insert(0, str(path))


_add_cram_paths()
