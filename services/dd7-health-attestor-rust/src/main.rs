use actix_web::{get, post, web, App, HttpResponse, HttpServer, Responder};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Serialize)]
struct HealthResponse {
    status: String,
    implementation: String,
}

#[derive(Serialize)]
struct GPUInfo {
    device_count: u32,
    devices: Vec<String>,
    attested: bool,
}

#[derive(Serialize)]
struct AttestationResponse {
    status: String,
    implementation: String,
    timestamp: DateTime<Utc>,
    #[serde(skip_serializing_if = "Option::is_none")]
    node_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    gpu_info: Option<GPUInfo>,
}

#[get("/v1/healthz")]
async fn health() -> impl Responder {
    HttpResponse::Ok().json(HealthResponse {
        status: "healthy".to_string(),
        implementation: "rust".to_string(),
    })
}

#[post("/v1/attest")]
async fn attest() -> impl Responder {
    let node_id = env::var("NODE_NAME").ok();

    HttpResponse::Ok().json(AttestationResponse {
        status: "attested".to_string(),
        implementation: "rust".to_string(),
        timestamp: Utc::now(),
        node_id,
        gpu_info: None,
    })
}

#[post("/v1/attest/gpu")]
async fn gpu_attest() -> impl Responder {
    let node_id = env::var("NODE_NAME").ok();

    // GPU attestation logic would go here
    // This is a placeholder that would integrate with NVIDIA/AMD attestation
    let gpu_info = GPUInfo {
        device_count: 0,
        devices: vec![],
        attested: true,
    };

    HttpResponse::Ok().json(AttestationResponse {
        status: "attested".to_string(),
        implementation: "rust".to_string(),
        timestamp: Utc::now(),
        node_id,
        gpu_info: Some(gpu_info),
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let port: u16 = env::var("DD7_PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("DD7_PORT must be a valid port number");

    log::info!("DD7 Health Attestor (Rust) starting on port {}", port);

    HttpServer::new(|| {
        App::new()
            .service(health)
            .service(attest)
            .service(gpu_attest)
    })
    .bind(("0.0.0.0", port))?
    .run()
    .await
}
