# Deployment

## Local

Use Docker Compose.

```text
docker compose
|
+-- api
|
+-- postgres
```

The API must work locally without AWS credentials.

## AWS

Target deployment:

```text
API Gateway or Lambda Function URL
                |
        containerized Lambda
                |
           PostgreSQL
```

The exact managed PostgreSQL product is intentionally not fixed yet.

Candidates may include:

- RDS PostgreSQL
- Aurora PostgreSQL / Serverless options

The choice should be made based on actual AWS cost and operational requirements
at deployment time.

## Important design rule

The Lambda handler is an adapter around the application.

Do not make the application itself Lambda-native.

Preferred:

```text
FastAPI application
       ^
       |
Lambda adapter
```

This keeps local execution and testing straightforward.

## Cost principle

Favor:

- low idle cost
- managed infrastructure
- simple backups
- simple upgrades
- minimal operational burden

Do not build a custom PostgreSQL-on-S3 persistence layer.
