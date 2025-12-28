# Unified attestor image: ships BOTH Go and Rust implementations
# and selects at runtime via DD7_ATTESTOR_IMPL=go|rust.
#
# Build context: repo root

FROM golang:1.22 AS go_build
WORKDIR /src
COPY services/dd7-health-attestor-go/ services/dd7-health-attestor-go/
WORKDIR /src/services/dd7-health-attestor-go
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /out/dd7-health-attestor-go ./cmd/server

FROM rust:1.79 AS rust_build
WORKDIR /src
COPY services/dd7-health-attestor-rust/ services/dd7-health-attestor-rust/
WORKDIR /src/services/dd7-health-attestor-rust
RUN cargo build --release && cp target/release/dd7-health-attestor /out/dd7-health-attestor-rust

FROM python:3.11-slim
WORKDIR /opt/dd7
# Python spiking engine + runner
COPY python /opt/dd7/python

# Both attestors
COPY --from=go_build /out/dd7-health-attestor-go /usr/local/bin/dd7-health-attestor-go
COPY --from=rust_build /out/dd7-health-attestor-rust /usr/local/bin/dd7-health-attestor-rust

# Runtime selector
COPY services/dd7-health-attestor-unified/entrypoint.sh /usr/local/bin/dd7-attestor-entrypoint.sh
RUN chmod +x /usr/local/bin/dd7-attestor-entrypoint.sh

ENV DD7_ATTESTOR_IMPL=go
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/dd7-attestor-entrypoint.sh"]
