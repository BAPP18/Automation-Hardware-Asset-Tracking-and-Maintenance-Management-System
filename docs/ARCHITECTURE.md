# System Architecture

## Context

The application supports a practical IT operations workflow around hardware ownership, assignment, maintenance, documents, warranty monitoring, and auditability.

```mermaid
flowchart LR
    U[Admin / Engineer] --> W[Flask Web App]

    W --> A[Asset Management]
    W --> M[Maintenance]
    W --> D[Document Management]
    W --> R[Reporting / Excel]
    W --> L[Activity Audit Log]

    A --> DB[(SQL Database)]
    M --> DB
    D --> DB
    L --> DB

    D --> FS[(Upload Storage)]
    R --> EX[(Generated Exports)]
```

## Application layers

| Layer | Responsibility | Location |
|---|---|---|
| Web routes | HTTP flow, permissions, request/response | `routes/` |
| Services | Import/export/file/business operations | `services/` |
| Domain models | Asset, maintenance, user, vendor, department, documents | `models/` |
| Presentation | Jinja templates, Bootstrap, Chart.js | `templates/`, `static/` |
| Persistence | SQLAlchemy + SQLite/default or `DATABASE_URL` | `database/` / external DB |

## Asset lifecycle

```mermaid
stateDiagram-v2
    [*] --> Available
    Available --> Assigned
    Assigned --> Available
    Available --> Maintenance
    Assigned --> Maintenance
    Maintenance --> Available
    Maintenance --> Assigned
    Available --> Retired
    Assigned --> Retired
    Maintenance --> Retired
    Retired --> [*]
```

Current application stores status directly. A future version should formalize lifecycle transition rules in a service layer so invalid transitions cannot be introduced by UI or import.

## Maintenance lifecycle

```mermaid
stateDiagram-v2
    [*] --> Scheduled
    Scheduled --> Completed
    Scheduled --> Scheduled
    Completed --> [*]
```

Recommended future statuses: `Planned`, `Scheduled`, `In Progress`, `Blocked`, `Completed`, `Cancelled`.

## Deployment

- Local demo: Flask + SQLite
- Container: Gunicorn, non-root user
- Render: production env + generated secret + health check
- Future enterprise: PostgreSQL + object storage + managed secrets + observability
