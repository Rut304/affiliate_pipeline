from affiliate_video_pipeline.manifest_compiler.batch_patcher import \
    batch_patch
from affiliate_video_pipeline.manifest_compiler.batch_validator import \
    batch_validate


def patch_and_validate():
    print("🔧 Running batch patcher...")
    batch_patch()
    print("\n🧪 Running batch validator...")
    batch_validate()
