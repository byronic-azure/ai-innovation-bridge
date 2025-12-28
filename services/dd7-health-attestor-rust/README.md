# dd7-health-attestor-rust

Rust implementation of the DD7 GPU Health Attestation service.

## Endpoints

- `GET /v1/healthz` - Health check endpoint
- `POST /v1/attest` - General attestation
- `POST /v1/attest/gpu` - GPU-specific attestation

## Building

```bash
cargo build --release
```

## Running

```bash
DD7_PORT=8080 ./target/release/dd7-health-attestor
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DD7_PORT` | Server port | `8080` |
| `NODE_NAME` | Kubernetes node name | (not set) |
| `RUST_LOG` | Log level | `info` |

## Docker

```bash
docker build -t dd7/health-attestor-rust:latest .
docker run -p 8080:8080 dd7/health-attestor-rust:latest
```

## Performance

The Rust implementation is optimized for:
- Low memory footprint
- High throughput
- Minimal latency

Use `DD7_ATTESTOR_IMPL=rust` to select this implementation in the unified container.
