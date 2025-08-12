from compiler import compile_manifest


def batch_compile(packs):
    for pack in packs:
        path = compile_manifest(**pack)
        print(f"✅ Manifest written: {path}")
