🛰️ GeoTrack: High-Performance Real-time Geo-Tracker API

GeoTrack is a scalable, production-ready backend system designed for real-time geolocation tracking. Built with FastAPI and Redis Stack, it handles high-throughput location updates and provides sub-millisecond spatial queries.
🚀 Core Features

    Real-time Synchronization: Bi-directional communication using WebSockets.

    Geo-Spatial Indexing: Efficient radius-based searching (GEORADIUS/GEOSEARCH) using Redis Geo.

    Horizontal Scalability: Stateless architecture powered by Redis Pub/Sub to sync updates across multiple server instances.

    Performance-First: Fully asynchronous implementation with FastAPI and redis-py (async).

    Containerized: One-command deployment using Docker Compose.

    Automated Quality Assurance: CI pipeline integrated with GitHub Actions for linting and syntax validation.

🛠️ Tech Stack

    Language: Python 3.10+

    Framework: FastAPI (Asynchronous)

    Data Store: Redis Stack (Geo-spatial & Pub/Sub)

    Communication: WebSockets

    DevOps: Docker, Docker Compose

    CI/CD: GitHub Actions

🏗️ System Architecture

Unlike traditional CRUD apps, GeoTrack uses an Event-Driven approach:

    Ingestion: Client sends coordinates via HTTP POST.

    Indexing: Server updates Redis Geo-Index and caches metadata.

    Broadcast: Update is published to a Redis Pub/Sub channel.

    Delivery: All active server instances receive the message; those with an active WebSocket connection to the specific device_id push the update to the client.

🚦 Getting Started
Prerequisites

    Docker and Docker Compose installed.

Installation & Execution

Clone the repository and run the following command:
Bash

docker-compose up --build

The API will be available at http://localhost:8000. Interactive API documentation (Swagger) can be accessed at http://localhost:8000/docs.
🔌 API Endpoints
Method	Endpoint	Description
POST	/update_location/{id}	Ingest new coordinates and broadcast.
GET	/nearby	Find devices within a specific radius (km).
WS	/ws/tracker/{id}	Live WebSocket stream for a specific device.
📂 Project Structure
Plaintext

├── .github/workflows/   # CI/CD pipelines
├── main.py              # Application entry point & routes
├── redis_stream.py      # Redis Pub/Sub and Geo-Indexing logic
├── websocket_manager.py # WebSocket connection lifecycle management
├── Dockerfile           # App containerization
├── docker-compose.yml   # Multi-container orchestration
└── requirements.txt     # Project dependencies

🔧 Development
Linting

To check for code quality, this project uses flake8. It is automatically triggered on every Push/PR via GitHub Actions.
Scaling

To scale the web service to 3 instances:
Bash

docker-compose up --scale web=3
