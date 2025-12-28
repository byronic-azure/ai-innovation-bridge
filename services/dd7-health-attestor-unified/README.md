# dd7-health-attestor-unified

Single image containing **both** implementations:
- `/usr/local/bin/dd7-health-attestor-go`
- `/usr/local/bin/dd7-health-attestor-rust`

## Selection

Set the `DD7_ATTESTOR_IMPL` environment variable:
- `DD7_ATTESTOR_IMPL=go` (default)
- `DD7_ATTESTOR_IMPL=rust`

This is the cleanest way to toggle in a **DaemonSet** without swapping images or Helm values.

## Building

Build from repo root:

```bash
docker build -f services/dd7-health-attestor-unified/Dockerfile -t dd7/health-attestor-unified:gpu-v1 .
```

## Usage

### Run with Go implementation (default)
```bash
docker run -p 8080:8080 dd7/health-attestor-unified:gpu-v1
```

### Run with Rust implementation
```bash
docker run -p 8080:8080 -e DD7_ATTESTOR_IMPL=rust dd7/health-attestor-unified:gpu-v1
```

## Kubernetes

In a DaemonSet, use the ConfigMap `dd7-attestor-config` to toggle implementations:

```yaml
envFrom:
- configMapRef:
    name: dd7-attestor-config
```

See `k8s/dd7-health-attestor-daemonset.yaml` for the full manifest.
