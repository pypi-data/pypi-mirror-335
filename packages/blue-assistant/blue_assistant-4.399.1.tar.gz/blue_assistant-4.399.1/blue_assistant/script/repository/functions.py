from typing import List, Tuple

from blue_options import string

from blue_assistant.script.load import load_script


def get_script_versions(
    script_name: str,
) -> List[str]:
    success, script = load_script(
        script_name=script_name,
        object_name=string.timestamp(),
        log=False,
        save_graph=False,
    )

    return list(script.versions.keys()) if success else []
