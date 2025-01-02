# Deployment Guide

## Prerequisites

1. Docker and Docker Compose installed
2. API keys for:
   - OpenAI
   - Pinecone
   - Your application's API key

## Local Deployment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/web-page-rag.git
cd web-page-rag
```

2. Create a `.env` file from the template:
```bash
cp .env.example .env
```

3. Update the `.env` file with your API keys and configuration:
```env
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
OPENAI_API_KEY=your_openai_api_key
API_KEY=your_api_key_for_authentication
CORS_ORIGINS=https://your-frontend-domain.com
REDIS_HOST=redis
REDIS_PORT=6379
```

4. Build and start the containers:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

## Production Deployment

### Option 1: Cloud Run (Google Cloud)

1. Install Google Cloud SDK
2. Configure Docker for Google Cloud:
```bash
gcloud auth configure-docker
```

3. Build and push the image:
```bash
docker build -t gcr.io/your-project/web-page-rag .
docker push gcr.io/your-project/web-page-rag
```

4. Deploy to Cloud Run:
```bash
gcloud run deploy web-page-rag \
  --image gcr.io/your-project/web-page-rag \
  --platform managed \
  --allow-unauthenticated \
  --region your-region \
  --set-env-vars "REDIS_HOST=your-redis-host"
```

### Option 2: Digital Ocean App Platform

1. Fork the repository to your GitHub account
2. Connect your GitHub account to Digital Ocean
3. Create a new App:
   - Choose the repository
   - Select Docker as the build method
   - Configure environment variables
   - Deploy

### Option 3: AWS Elastic Beanstalk

1. Install AWS CLI and EB CLI
2. Initialize EB CLI:
```bash
eb init -p docker web-page-rag
```

3. Create and deploy:
```bash
eb create web-page-rag-env
```

## Monitoring

1. Set up logging:
```bash
docker-compose logs -f
```

2. Health check endpoint:
```bash
curl http://your-domain/health
```

3. Monitor rate limits:
```bash
redis-cli KEYS "rate-limit:*"
```

## Security Considerations

1. Always use HTTPS in production
2. Set strong API keys
3. Configure CORS for your specific domains
4. Use rate limiting appropriate for your use case
5. Monitor for abuse

## Scaling

1. Horizontal scaling:
   - Deploy behind a load balancer
   - Use multiple API instances
   - Scale Redis with clustering

2. Vertical scaling:
   - Increase container resources
   - Optimize cache settings
   - Tune rate limits

## Troubleshooting

1. Check logs:
```bash
docker-compose logs api
```

2. Check Redis connection:
```bash
docker-compose exec redis redis-cli ping
```

3. Test rate limiting:
```bash
for i in {1..25}; do curl -H "X-API-Key: your-key" http://localhost:8000/health; done
```

## Backup and Recovery

1. Redis data:
```bash
# Backup
docker-compose exec redis redis-cli SAVE

# Restore
docker-compose down
docker-compose up -d
```

2. Vector store:
   - Use Pinecone's backup features
   - Regular index snapshots 