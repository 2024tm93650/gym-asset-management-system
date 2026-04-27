# Kubernetes manifests — ACEest Fitness & Gym (Step 7)

Five deployment strategies, one folder each. The image used everywhere is
`2024tm93650/aceest-fitness:latest` (already on Docker Hub from Step 4).

| #  | Folder                  | Strategy           | Service NodePort |
|----|-------------------------|--------------------|------------------|
| 1  | `01-rolling-update/`    | Rolling Update     | `30080`          |
| 2  | `02-blue-green/`        | Blue / Green       | `30081`          |
| 3  | `03-canary/`            | Canary (4 : 1)     | `30082`          |
| 4  | `04-shadow/`            | Shadow / Mirroring | `30083` (prod only) |
| 5  | `05-ab-testing/`        | A/B Testing        | via Ingress, host `aceest.local` |

## Prerequisites

```bash
# one-time
brew install minikube kubectl
minikube start --driver=docker --cpus=2 --memory=4096
minikube addons enable ingress           # required only for strategy 5
kubectl apply -f k8s/00-namespace.yaml
```

Use `./k8s/deploy.sh <strategy>` to apply one strategy at a time and tear the
others down so NodePorts don't collide.

## Quick demo per strategy

### 1. Rolling update
```bash
./k8s/deploy.sh rolling
minikube service -n aceest aceest-fitness --url
# Promote a new image (zero downtime):
kubectl -n aceest set image deployment/aceest-fitness aceest-fitness=2024tm93650/aceest-fitness:latest --record
kubectl -n aceest rollout status deployment/aceest-fitness
# Rollback:
kubectl -n aceest rollout undo deployment/aceest-fitness
```

### 2. Blue / Green
```bash
./k8s/deploy.sh blue-green
# Cut traffic from blue -> green (instant):
kubectl -n aceest patch svc aceest-bluegreen \
  -p '{"spec":{"selector":{"app":"aceest-fitness","color":"green"}}}'
# Rollback: patch the selector back to "blue".
```

### 3. Canary (4:1 = 80/20)
```bash
./k8s/deploy.sh canary
# Show traffic distribution:
for i in $(seq 1 20); do curl -s "$(minikube service -n aceest aceest-canary-svc --url)/version" | head -c 80; echo; done
# Promote canary:
kubectl -n aceest scale deploy/aceest-stable --replicas=0
kubectl -n aceest scale deploy/aceest-canary --replicas=5
```

### 4. Shadow (traffic mirroring)
```bash
./k8s/deploy.sh shadow
kubectl apply -f k8s/04-shadow/shadow-mirror-job.yaml
kubectl -n aceest logs -f job/aceest-shadow-mirror
# Real users only see prod responses; shadow processes mirrored copies.
```

### 5. A/B testing (header-based)
```bash
./k8s/deploy.sh ab
# Add aceest.local -> $(minikube ip) to /etc/hosts (one-off):
echo "$(minikube ip) aceest.local" | sudo tee -a /etc/hosts
curl http://aceest.local/version                          # variant A
curl -H "X-Variant: B" http://aceest.local/version        # variant B
```

## Cleanup
```bash
./k8s/deploy.sh clean        # removes all five strategies
kubectl delete ns aceest     # nuke everything
minikube stop                # free the host resources
```
