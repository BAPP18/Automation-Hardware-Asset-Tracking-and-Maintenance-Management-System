# Project Management Framework

This document positions the repository not only as a software project, but as an IT operations improvement initiative.

## Project objective

Create one operational source for hardware asset ownership, maintenance status, warranty visibility, document evidence, and audit history.

## Business outcomes

1. Reduce manual spreadsheet reconciliation.
2. Improve visibility of asset location/assignment.
3. Reduce overdue preventive maintenance.
4. Surface warranty risk before expiration.
5. Improve traceability of asset changes and maintenance actions.
6. Standardize import/export and operational reporting.

## Scope

### In scope

- hardware asset registry;
- assignment / department / location tracking;
- vendor data;
- maintenance scheduling and history;
- warranty monitoring;
- supporting documents;
- Excel import/export;
- RBAC;
- activity audit log;
- dashboard KPIs.

### Out of scope for current version

- procurement approval workflow;
- financial depreciation;
- CMDB discovery;
- MDM endpoint control;
- SSO/MFA;
- enterprise notification service;
- mobile barcode/QR scanning;
- multi-tenant organizations.

## Work breakdown structure

```text
1. Asset Registry
   1.1 Asset CRUD
   1.2 Vendor & department references
   1.3 Assignment/location
   1.4 Import/export

2. Maintenance
   2.1 Schedule record
   2.2 Engineer ownership
   2.3 Completion tracking
   2.4 Maintenance reports

3. Governance
   3.1 Authentication
   3.2 Role-based access
   3.3 Activity audit
   3.4 Document evidence

4. Reporting
   4.1 Asset KPI
   4.2 Warranty risk
   4.3 Category/department/vendor distribution
   4.4 Overdue maintenance

5. Engineering
   5.1 CI
   5.2 Tests
   5.3 Container
   5.4 Health check
   5.5 Environment configuration
```

## RACI

| Activity | Admin | Engineer | IT Manager | System |
|---|---|---|---|---|
| Create/edit/retire asset | R | C | A | I |
| Record maintenance | A/R | C | I | I |
| Review overdue maintenance | R | R | A | C |
| Upload asset evidence | R | C | I | I |
| Export operational report | R | R | A | C |
| Review audit log | R | I | A | C |

R = Responsible, A = Accountable, C = Consulted, I = Informed.

## Recommended operational KPIs

| KPI | Definition | Suggested target |
|---|---|---|
| Asset data completeness | required asset fields populated | >= 98% |
| Maintenance on-time rate | completed by planned due date | >= 95% |
| Overdue maintenance | open scheduled maintenance past due | downward trend |
| Warranty-at-risk coverage | expiring assets identified before expiry | >= 95% |
| Assignment accuracy | asset owner/location matches operational reality | >= 98% |
| Audit coverage | material changes captured in activity log | 100% |
| Import error rate | rejected/invalid rows per import | < 2% |

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Demo credentials used in production | High | demo seed disabled in production |
| SQLite used for multi-user production | High | move to PostgreSQL |
| Uploaded files stored locally | Medium/High | object storage + malware scanning |
| Asset lifecycle rules remain UI-driven | Medium | transition service + validation |
| No scheduled notifications | Medium | job scheduler / email integration |
| Manual engineer names in maintenance | Medium | link maintenance ownership to User table |
| No migration framework | Medium | add Alembic/Flask-Migrate |

## Roadmap

### Phase 1 — Portfolio hardening
- security/config cleanup;
- CI + tests;
- health check;
- architecture + PM docs.

### Phase 2 — Operations maturity
- normalized maintenance owner relation;
- richer maintenance lifecycle;
- lifecycle transition validation;
- maintenance SLA metrics;
- notification scheduler.

### Phase 3 — Enterprise readiness
- PostgreSQL;
- Flask-Migrate/Alembic;
- SSO/MFA;
- object storage;
- API;
- observability;
- backup/restore runbook.

### Phase 4 — Automation
- QR/barcode labels;
- automated reminders;
- bulk maintenance scheduling;
- reconciliation with procurement/CMDB sources.
