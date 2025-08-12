import os

from affiliate_video_pipeline.manifest_compiler.audit_logger import \
    log_pipeline_run
from affiliate_video_pipeline.validate_batch_ready import validate_pack


def validate_all_packs():
    content_dir = "content"
    pack_ids = [
        name
        for name in os.listdir(content_dir)
        if os.path.isdir(os.path.join(content_dir, name))
    ]

    log_lines = []
    for pack_id in sorted(pack_ids):
        result = validate_pack(pack_id)
        log_lines.append(f"📦 Pack: {pack_id}")
        for key, value in result.items():
            log_lines.append(f"  - {key}: {value}")
        log_lines.append("")  # Spacer

    log_pipeline_run("Batch pack validation completed.", log_lines)
