# AI Innovation Bridge

Welcome to our AI Innovation Bridge repo! This repo contains reference solutions, hackathon sample code, workshop content, and more!

## Table of Contents
- [hackathons](hackathons)
- [solutions](hackathons)
- [workshops](hackathons)
- [utilities](hackathons)
- [services](services) - DD7 GPU Health Attestation services
- [k8s](k8s) - Kubernetes manifests

## DD7 GPU Health Attestor

The DD7 Health Attestor provides GPU attestation capabilities for Kubernetes clusters. It ships with both Go and Rust implementations in a single unified container.

### DaemonSet Toggle (Go vs Rust)

Set `DD7_ATTESTOR_IMPL=go|rust` via ConfigMap in `k8s/dd7-health-attestor-daemonset.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dd7-attestor-config
  namespace: iua-runtime-attestation
data:
  DD7_ATTESTOR_IMPL: "go"   # or "rust"
```

### Building the Unified Image

```bash
docker build -f services/dd7-health-attestor-unified/Dockerfile -t dd7/health-attestor-unified:gpu-v1 .
```

### Deploying to Kubernetes

```bash
kubectl apply -f k8s/dd7-health-attestor-daemonset.yaml
```

To switch implementations, update the ConfigMap and restart the pods:

```bash
kubectl -n iua-runtime-attestation patch configmap dd7-attestor-config \
  --type merge -p '{"data":{"DD7_ATTESTOR_IMPL":"rust"}}'
kubectl -n iua-runtime-attestation rollout restart daemonset/dd7-health-attestor
```
