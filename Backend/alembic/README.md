# Alembic Database Migrations for Verolux

## Overview

This directory contains database migration scripts for the Verolux system using Alembic.

## Prerequisites

```bash
pip install alembic
```

## Configuration

Database URL can be set via environment variables:
- `DATABASE_URL` (preferred)
- `POSTGRES_URL` (fallback)

Default (from alembic.ini): `postgresql://verolux:verolux123@localhost:5432/verolux`

## Common Commands

### Create a new migration

**Auto-generate from models:**
```bash
cd Backend
alembic revision --autogenerate -m "Add users table"
```

**Manual migration:**
```bash
cd Backend
alembic revision -m "Add custom index"
```

### Apply migrations

**Upgrade to latest:**
```bash
cd Backend
alembic upgrade head
```

**Upgrade one step:**
```bash
alembic upgrade +1
```

**Upgrade to specific revision:**
```bash
alembic upgrade abc123
```

### Downgrade migrations

**Downgrade one step:**
```bash
cd Backend
alembic downgrade -1
```

**Downgrade to specific revision:**
```bash
alembic downgrade abc123
```

**Downgrade all:**
```bash
alembic downgrade base
```

### View migration history

**Current version:**
```bash
cd Backend
alembic current
```

**Migration history:**
```bash
alembic history
```

**Show SQL without executing:**
```bash
alembic upgrade head --sql
```

## Migration File Structure

```
alembic/
├── versions/           # Migration scripts
│   └── 20241013_abc123_initial.py
├── env.py             # Migration environment
├── script.py.mako     # Migration template
└── README.md          # This file
```

## Example Migration

```python
"""Add users table

Revision ID: abc123
Revises: 
Create Date: 2024-10-13 18:27:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

def downgrade() -> None:
    op.drop_table('users')
```

## Integration with Docker

### In docker-compose.production.yml:

```yaml
  migration:
    image: verolux-backend:latest
    command: alembic upgrade head
    environment:
      - POSTGRES_URL=postgresql://verolux:verolux123@postgres:5432/verolux
    depends_on:
      - postgres
    networks:
      - verolux-net
```

### Or in startup script:

```bash
#!/bin/bash
# Wait for Postgres
while ! pg_isready -h postgres -U verolux; do
  sleep 1
done

# Run migrations
cd /app && alembic upgrade head

# Start application
python backend_server.py
```

## CI/CD Integration

### In GitHub Actions:

```yaml
- name: Run database migrations
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    cd Backend
    alembic upgrade head
```

## Best Practices

1. **Always review auto-generated migrations** - they may need manual adjustments
2. **Test migrations in development first** before applying to production
3. **Keep migrations small and focused** - one logical change per migration
4. **Write reversible migrations** - always implement downgrade()
5. **Use descriptive messages** - future you will thank you
6. **Version control** - commit migration files to git
7. **Never modify existing migrations** - create new ones instead
8. **Backup production database** before running migrations

## Troubleshooting

### Error: "Can't locate revision identified by 'abc123'"
- The migration file is missing from the versions/ directory
- Check git history or restore from backup

### Error: "Target database is not up to date"
- Run: `alembic stamp head` to mark current state
- Or: `alembic upgrade head` to apply pending migrations

### Error: "Multiple heads in database"
- You have branching migrations
- Run: `alembic merge <rev1> <rev2> -m "merge branches"`

## Useful Queries

**Check current migration version in database:**
```sql
SELECT * FROM alembic_version;
```

**View all tables:**
```sql
\dt
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Migration Patterns](https://alembic.sqlalchemy.org/en/latest/cookbook.html)





















