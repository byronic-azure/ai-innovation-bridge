# dd7-health-attestor-go

Go implementation of the DD7 GPU Health Attestation service.

## Endpoints

- `GET /v1/healthz` - Health check endpoint
- `POST /v1/attest` - General attestation
- `POST /v1/attest/gpu` - GPU-specific attestation

## Building

```bash
go build -o dd7-health-attestor ./cmd/server
```

## Running

```bash
DD7_PORT=8080 ./dd7-health-attestor
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DD7_PORT` | Server port | `8080` |
| `NODE_NAME` | Kubernetes node name | `unknown` |

## Docker

```bash
docker build -t dd7/health-attestor-go:latest .
docker run -p 8080:8080 dd7/health-attestor-go:latest
```
