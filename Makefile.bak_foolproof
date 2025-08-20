.PHONY: preflight

preflight:
@echo " Updating segmind_preflight.sh..."
@mkdir -p utils
@cat > utils/segmind_preflight.sh <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail

PROMPT="tiny smoke test"
WIDTH=512
HEIGHT=512
POLL_INTERVAL=2

: "${SEGMIND_API_KEY:?SEGMIND_API_KEY not set}"
: "${SEGMIND_WORKFLOW_URL:?SEGMIND_WORKFLOW_URL not set}"

echo "Triggering Segmind preflight run..."
job=$(curl -s -X POST \
-H "x-api-key: ${SEGMIND_API_KEY}" \
-H "Content-Type: application/json" \
-d "{\"prompt\":\"${PROMPT}\",\"width\":${WIDTH},\"height\":${HEIGHT}}" \
"${SEGMIND_WORKFLOW_URL}")

poll_url=$(echo "$job" | jq -r '.data.poll_url // .poll_url')
if [[ -z "$poll_url" || "$poll_url" == "null" ]]; then
echo " Could not find poll_url in initial response:"
echo "$job" | jq
exit 1
fi

echo " Polling: $poll_url"

while true; do
sleep "$POLL_INTERVAL"
result=$(curl -s -H "x-api-key: ${SEGMIND_API_KEY}" "$poll_url")
status=$(echo "$result" | jq -r '.status')
echo " $status"
case "$status" in
COMPLETED) break ;;
FAILED)
echo " Workflow run failed:"
echo "$result" | jq
exit 1
;;
esac
done

video_url=$(echo "$result" | jq -r '.outputs[] | select(.keyname=="video_out") | .value.data')
if [[ -z "$video_url" || "$video_url" == "null" ]]; then
echo " No video_out.data found in outputs:"
echo "$result" | jq
exit 1
fi

echo " Preflight passed  video_out.data is present:"
echo "$video_url"
SCRIPT
@chmod +x utils/segmind_preflight.sh
@echo " Running preflight..."
@utils/segmind_preflight.sh
