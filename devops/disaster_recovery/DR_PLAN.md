# TiranaFly Disaster Recovery Plan

## 1. Objectives
- Recovery Time Objective (RTO): 4 hours
- Recovery Point Objective (RPO): 24 hours

## 2. Backup Strategy
- **PostGIS**: Daily automated snapshots and SQL dumps (see `devops/backup/backup_db.sh`).
- **Redis**: Persistent Append-Only-Files (AOF) enabled.
- **Source Code**: Multi-region GitHub repositories.

## 3. Failure Scenarios

### Scenario A: Database Corruption
1. Shutdown API services.
2. Restore latest SQL dump to a fresh PostGIS instance.
3. Run schema migrations.
4. Point API to new instance and restart.

### Scenario B: Cloud Region Outage (AWS)
1. Initialize Terraform in secondary region (e.g., `eu-central-1`).
2. Deploy EKS cluster and RDS instance.
3. Restore database from cross-region replicated snapshot.
4. Update Route53 DNS to point to new Load Balancer.

### Scenario C: Frontend Hijack
1. Re-run CI/CD pipeline from known good commit.
2. Invalidate CloudFront/CDN cache.
3. Rotate all API keys and secrets.
