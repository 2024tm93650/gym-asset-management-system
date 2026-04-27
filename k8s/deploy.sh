#!/usr/bin/env bash
# Apply ONE deployment strategy at a time (others are deleted to avoid NodePort
# collisions). Always (re)applies the namespace first.
#
#   ./k8s/deploy.sh rolling | blue-green | canary | shadow | ab | clean | status
set -euo pipefail

NS="aceest"
HERE="$(cd "$(dirname "$0")" && pwd)"

apply_ns() {
  kubectl apply -f "$HERE/00-namespace.yaml" >/dev/null
}

clean_all() {
  echo ">> deleting all aceest workloads"
  kubectl -n "$NS" delete deploy,svc,ingress,job -l 'strategy in (rolling,blue-green,canary,shadow,ab)' --ignore-not-found
  # cover the default rolling deploy that has no strategy label too
  kubectl -n "$NS" delete deploy aceest-fitness svc aceest-fitness --ignore-not-found
}

apply_strategy() {
  local dir="$1" label="$2"
  echo ">> deploying strategy: $label  (k8s/$dir)"
  apply_ns
  clean_all
  kubectl apply -f "$HERE/$dir/"
  echo ">> waiting for rollout..."
  for d in $(kubectl -n "$NS" get deploy -l "strategy=$label" -o name); do
    kubectl -n "$NS" rollout status "$d" --timeout=120s
  done
  echo
  kubectl -n "$NS" get deploy,svc,ingress -l "strategy=$label" -o wide
}

case "${1:-}" in
  rolling)     apply_strategy 01-rolling-update rolling ;;
  blue-green)  apply_strategy 02-blue-green     blue-green ;;
  canary)      apply_strategy 03-canary         canary ;;
  shadow)      apply_strategy 04-shadow         shadow ;;
  ab)          apply_strategy 05-ab-testing     ab ;;
  clean)       apply_ns; clean_all ;;
  status)      kubectl -n "$NS" get deploy,svc,ingress,pods -o wide ;;
  *) echo "usage: $0 {rolling|blue-green|canary|shadow|ab|clean|status}" >&2; exit 1 ;;
esac
