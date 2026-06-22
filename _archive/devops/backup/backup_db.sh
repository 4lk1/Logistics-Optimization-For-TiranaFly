#!/bin/bash
# Database Backup Script for TiranaFly

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups/db"
DB_NAME="tiranafly"
DB_USER="tiranafly_admin"
S3_BUCKET="s3://tiranafly-backups/db"

mkdir -p $BACKUP_DIR

echo "Starting backup of $DB_NAME..."

# Perform dump
pg_dump -h db -U $DB_USER -d $DB_NAME -F c -b -v -f "$BACKUP_DIR/tiranafly_$TIMESTAMP.dump"

# Encrypt backup
gpg --encrypt --recipient "admin@tiranafly.com" "$BACKUP_DIR/tiranafly_$TIMESTAMP.dump"

# Upload to S3
aws s3 cp "$BACKUP_DIR/tiranafly_$TIMESTAMP.dump.gpg" "$S3_BUCKET/"

# Clean up old local backups (keep 7 days)
find $BACKUP_DIR -type f -mtime +7 -name "*.dump*" -exec rm {} \;

echo "Backup completed and uploaded to $S3_BUCKET"
