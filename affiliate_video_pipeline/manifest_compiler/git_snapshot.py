import subprocess

def snapshot_manifests(commit_msg="Update manifests"):
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "affiliate_video_pipeline/manifests"],
            capture_output=True, text=True
        )

        if not result.stdout.strip():
            return "🟡 No manifest changes to commit.", None

        subprocess.run(["git", "add", "affiliate_video_pipeline/manifests"], check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)

        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True
        )
        git_sha = sha_result.stdout.strip()
        return "📦 Manifests committed to Git.", git_sha
    except subprocess.CalledProcessError:
        return "❌ Git commit failed. Check for staged changes or repo status.", None
