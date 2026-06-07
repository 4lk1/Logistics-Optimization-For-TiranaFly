#!/bin/bash
# PostGIS Backup Script

DB_NAME=${POSTGRES_DB:-tiranafly}
DB_USER=${POSTGRES_USER:-postgres}
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "Starting backup for $DB_NAME..."
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/${DB_NAME}_$TIMESTAMP.sql

if [ $? -eq 0 ]; then
  echo "Backup successful: $BACKUP_DIR/${DB_NAME}_$TIMESTAMP.sql"
else
  echo "Backup failed!"
  exit 1
fi

# Retention: Delete backups older than 7 days
find $BACKUP_DIR -type f -name "*.sql" -mtime +7 -delete
echo "Old backups cleaned up."
