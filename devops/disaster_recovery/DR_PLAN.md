# TiranaFly Disaster Recovery Plan (DRP)

## 1. Objectives
*   **RPO (Recovery Point Objective):** 15 minutes
*   **RTO (Recovery Time Objective):** 2 hours

## 2. Backup Strategy
*   **Database:** Continuous WAL archiving to S3 + Daily full backups.
*   **Application Config:** Managed in Git (Infrastructure as Code).
*   **User Assets:** S3 Versioning enabled.

## 3. Recovery Procedures

### 3.1 Regional Failure (AWS)
1.  **Activate Secondary Region:** Use Terraform to spin up an identical VPC/EKS/RDS in `eu-west-1`.
2.  **Restore RDS:** Restore from the latest snapshot/PITR.
3.  **Deploy Application:** Run GitHub Actions with target region set to `eu-west-1`.
4.  **Update DNS:** Switch Route53 failover record to the new Load Balancer.

### 3.2 Data Corruption
1.  **Identify Point of Failure.**
2.  **Restore Database:** Use Point-in-Time Recovery (PITR) to restore to 1 minute before corruption.
3.  **Validate Data.**

### 3.3 Service Outage (Single Service)
1.  **HPA will attempt to scale.**
2.  **If stuck, use `kubectl rollout restart deployment <service-name>`.**
3.  **Check Loki/Prometheus for root cause.**

## 4. Roles and Responsibilities
*   **DevOps Lead:** Coordination of recovery.
*   **DBA:** Database restoration.
*   **Security Officer:** Ensuring TLS/Secrets integrity after restore.
