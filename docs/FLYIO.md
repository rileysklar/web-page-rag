# Deploying to Fly.io

## Prerequisites
- [Fly.io account](https://fly.io/signup)
- [Flyctl installed](https://fly.io/docs/hands-on/install-flyctl/)
- Docker installed and running
- Git repository with your code

## Configuration Files

### fly.toml
Create a `fly.toml` file in the root directory:
```toml
app = "web-page-rag-api"
primary_region = "dfw"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"
  REDIS_HOST = "web-page-rag-redis.internal"
  REDIS_PORT = "6379"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[[services]]
  protocol = "tcp"
  internal_port = 8000
  processes = ["app"]

  [[services.ports]]
    port = 80
    handlers = ["http"]
  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

## Deployment Steps

1. **Login to Fly.io**
```bash
flyctl auth login
```

2. **Launch the Application**
```bash
flyctl launch
```

3. **Set Environment Variables**
```bash
flyctl secrets set PINECONE_API_KEY="your_pinecone_api_key"
flyctl secrets set PINECONE_ENVIRONMENT="your_pinecone_environment"
flyctl secrets set OPENAI_API_KEY="your_openai_api_key"
flyctl secrets set API_KEY="your_api_key"
flyctl secrets set CORS_ORIGINS="https://your-frontend-domain.com"
```

4. **Create Redis Instance**
```bash
flyctl redis create web-page-rag-redis
```

5. **Attach Redis to App**
```bash
flyctl redis attach web-page-rag-redis
```

6. **Deploy the Application**
```bash
flyctl deploy
```

## Monitoring and Maintenance

### View Logs
```bash
flyctl logs
```

### Check Status
```bash
flyctl status
```

### Scale Application
```bash
flyctl scale count 2  # Scale to 2 instances
```

## Usage

After deployment, your API will be available at:
```
https://web-page-rag-api.fly.dev
```

Update your frontend application to use this endpoint:
```typescript
const API_URL = 'https://web-page-rag-api.fly.dev';
```

## Troubleshooting

1. **Connection Issues**
   - Check if the application is running: `flyctl status`
   - Verify Redis connection: Check logs for Redis connection errors
   - Ensure environment variables are set: `flyctl secrets list`

2. **Performance Issues**
   - Monitor resource usage: `flyctl monitor`
   - Scale if needed: `flyctl scale count`
   - Check Redis performance: `flyctl redis status`

3. **SSL/TLS Issues**
   - Verify SSL certificate: `flyctl certs show`
   - Force HTTPS redirect is enabled in `fly.toml`

## Security Considerations

1. **API Key Protection**
   - Never commit API keys to the repository
   - Use Fly.io secrets for sensitive data
   - Rotate API keys periodically

2. **CORS Configuration**
   - Restrict CORS_ORIGINS to your frontend domain
   - Use HTTPS for all communications

3. **Rate Limiting**
   - Configure rate limits based on your needs
   - Monitor for abuse

## Maintenance

1. **Updates**
   - Regular dependency updates
   - Security patches
   - Performance optimizations

2. **Backups**
   - Regular Redis backups
   - Configuration backups
   - Monitoring setup

3. **Scaling**
   - Monitor usage patterns
   - Scale based on demand
   - Optimize resource usage