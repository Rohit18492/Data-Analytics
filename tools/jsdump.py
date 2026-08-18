import json, pathlib
ROOT = pathlib.Path("/workspace/js/data")
ROOT.mkdir(parents=True, exist_ok=True)

def dump(name, obj):
    path = ROOT / name
    path.write_text("window.DE = window.DE || {};\nObject.assign(window.DE, " + json.dumps(obj, ensure_ascii=False) + ");\n", encoding="utf-8")
    print(name, path.stat().st_size)
