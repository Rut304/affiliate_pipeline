import time

from affiliate_video_pipeline.manifest_compiler.audit_logger import \
    log_pipeline_run
from affiliate_video_pipeline.manifest_compiler.batch_patcher import \
    patch_all_manifests
from affiliate_video_pipeline.manifest_compiler.batch_validator import \
    validate_all_manifests
from affiliate_video_pipeline.manifest_compiler.git_snapshot import \
    snapshot_manifests
from affiliate_video_pipeline.registry.registry_indexer import \
    generate_registry_index


def full_pipeline(commit_msg="Update manifests"):
    start_time = time.time()
    log_lines = []

    # 🔧 Step 1: Patch manifests
    log_lines.append("🔧 Batch patcher:")
    patched_manifests = patch_all_manifests()
    if patched_manifests:
        for manifest in patched_manifests:
            log_lines.append(f"  - Patched: {manifest}")
    else:
        log_lines.append("  - No changes needed.")

    # 🧪 Step 2: Validate manifests
    log_lines.append("\n🧪 Batch validator:")
    validation_results = validate_all_manifests()
    for manifest, result in validation_results.items():
        log_lines.append(f"  - {manifest}: {result}")

    # 📦 Step 3: Git snapshot
    log_lines.append("\n📦 Git commit status:")
    git_status, git_sha = snapshot_manifests(commit_msg)
    log_lines.append(f"  - {git_status}")
    if git_sha:
        log_lines.append(f"  - Commit SHA: {git_sha}")

    # 📊 Step 4: Registry index
    index_path = generate_registry_index()
    log_lines.append("\n📊 Registry index:")
    log_lines.append(f"  - Index written to: {index_path}")

    # ⏱️ Step 5: Runtime
    duration = round(time.time() - start_time, 2)
    log_lines.append(f"\n⏱️ Runtime: {duration} seconds")

    # 📝 Step 6: Audit log
    log_pipeline_run("Full pipeline completed successfully.", log_lines)
