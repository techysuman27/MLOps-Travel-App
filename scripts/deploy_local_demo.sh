#!/bin/sh
# Only the named, localhost-only project demo service is replaced.
set -eu
image=$1
name=voyage-api-release
backup=voyage-api-release-previous
docker image inspect "$image" >/dev/null
if docker container inspect "$backup" >/dev/null 2>&1; then
  echo 'A previous rollback container exists; inspect it before another release.' >&2
  exit 1
fi
had_previous=false
if docker container inspect "$name" >/dev/null 2>&1; then
  docker stop "$name"
  docker rename "$name" "$backup"
  had_previous=true
fi
rollback() {
  docker rm -f "$name" >/dev/null 2>&1 || true
  if [ "$had_previous" = true ]; then
    docker rename "$backup" "$name"
    docker start "$name"
  fi
}
trap rollback EXIT
docker run -d --name "$name" --label voyage.component=local-demo-release --restart unless-stopped -p 127.0.0.1:18081:8000 "$image"
docker cp scripts/wait_ready.py "$name:/tmp/wait_ready.py"
docker cp scripts/smoke_test.py "$name:/tmp/smoke_test.py"
docker exec "$name" python /tmp/wait_ready.py --url http://127.0.0.1:8000
docker exec "$name" python /tmp/smoke_test.py --url http://127.0.0.1:8000
trap - EXIT
if [ "$had_previous" = true ]; then docker rm "$backup"; fi
echo "Local deployment verified: http://127.0.0.1:18081 ($image)"
