from pathlib import Path

import mammoth.models


def get_import_list(code):
    code = Path(code).read_text() if code.endswith(".py") else code
    found_imports = list()
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("import "):
            imported_modules = line.split("import", 1)[1].strip().split(",")
            for module in imported_modules:
                module_name = module.split()[0].split(".")[0].strip()
                found_imports.append(module_name)
        elif line.startswith("from "):
            parts = line.split()
            if len(parts) > 1:
                module_name = parts[1].split(".")[0]
                found_imports.append(module_name)
    return found_imports


def safeexec(code: str, out: str = "commons", whitelist: list[str] = None):
    code = Path(code).read_text() if code.endswith(".py") else code
    whitelist = () if whitelist is None else set(whitelist)
    for module_name in get_import_list(code):
        assert (
            module_name in whitelist
        ), f"Disallowed import detected: '{module_name}'. Only these are allowed: {','.join(whitelist)}"
    exec_context = locals().copy()
    exec(code, exec_context)
    assert (
        out in exec_context
    ), f"The provided script or file did not contain an {out} variable"
    return exec_context[out]


def get_model_layer_list(model):
    try:
        model = model.model
        return [name for name, _ in model.named_modules() if name]
    except Exception as e:
        print(e)
        return []
