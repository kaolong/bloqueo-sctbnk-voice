# Deployment & DevOps: Bloqueo de Tarjetas SCTBNK con Rasa Pro

## Visión General
Estrategia completa de deployment, CI/CD y DevOps para el sistema de asistente virtual de bloqueo de tarjetas desarrollado con Rasa Pro, Twilio y Freshdesk.

## Arquitectura de Deployment

### **Entornos**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Development   │    │     Staging     │    │   Production    │
│   (Local)       │    │   (Testing)     │    │   (Live)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Docker Compose│    │   Kubernetes    │    │   Kubernetes    │
│   + Local DB    │    │   + Staging DB  │    │   + Production  │
│                 │    │                 │    │   DB            │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Componentes de Infraestructura**
- **Containerization**: Docker + Kubernetes
- **Database**: PostgreSQL con replicación
- **Cache**: Redis para sesiones de Rasa
- **Load Balancer**: NGINX Ingress
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Telephony**: Twilio Voice API
- **Ticketing**: Freshdesk API

## Pipeline de CI/CD

### **GitHub Actions Workflow**
```yaml
# .github/workflows/ci-cd.yml
name: SCTBNK Rasa Pro CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run Rasa tests
        run: |
          rasa test
          pytest tests/
      
      - name: Run security scan
        run: |
          bandit -r actions/
          safety check

  train-model:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Train Rasa model
        run: rasa train
      
      - name: Upload model artifact
        uses: actions/upload-artifact@v3
        with:
          name: rasa-model
          path: models/

  build:
    needs: train-model
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Download model artifact
        uses: actions/download-artifact@v3
        with:
          name: rasa-model
          path: models/
      
      - name: Build Docker image
        run: |
          docker build -t sctbnk-rasa:${{ github.sha }} .
          docker tag sctbnk-rasa:${{ github.sha }} sctbnk-rasa:latest
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push sctbnk-rasa:${{ github.sha }}
          docker push sctbnk-rasa:latest

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Deploy to staging
        run: |
          kubectl config use-context staging
          kubectl set image deployment/sctbnk-rasa rasa=sctbnk-rasa:${{ github.sha }}
          kubectl rollout status deployment/sctbnk-rasa

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          kubectl config use-context production
          kubectl set image deployment/sctbnk-rasa rasa=sctbnk-rasa:${{ github.sha }}
          kubectl rollout status deployment/sctbnk-rasa
      
      - name: Run smoke tests
        run: |
          ./scripts/smoke-tests.sh
```

### **Stages del Pipeline**
1. **Code Quality**: Linting, formatting, security scanning
2. **Testing**: Rasa tests, unit tests, integration tests
3. **Model Training**: Entrenamiento automático del modelo
4. **Building**: Docker image creation
5. **Security**: Vulnerability scanning
6. **Deployment**: Staging and production deployment
7. **Monitoring**: Health checks and monitoring setup

## Configuración de Docker

### **Dockerfile**
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p models logs data actions

# Copy trained model
COPY models/ ./models/

# Expose ports
EXPOSE 5005 5055

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5005/health || exit 1

# Start Rasa
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--debug"]
```

### **Docker Compose (Development)**
```yaml
# docker-compose.yml
version: '3.8'
services:
  rasa:
    build: .
    ports:
      - "5005:5005"
      - "5055:5055"
    environment:
      - RASA_TOKEN=${RASA_TOKEN}
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - DATABASE_URL=${DATABASE_URL}
      - FRESHDESK_API_KEY=${FRESHDESK_API_KEY}
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: sctbnk_cards
      POSTGRES_USER: sctbnk_user
      POSTGRES_PASSWORD: sctbnk_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - rasa
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## Configuración de Kubernetes

### **Namespace**
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: sctbnk-rasa
  labels:
    name: sctbnk-rasa
    environment: production
```

### **ConfigMap**
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: rasa-config
  namespace: sctbnk-rasa
data:
  RASA_TOKEN: "your_rasa_token"
  TWILIO_ACCOUNT_SID: "your_account_sid"
  TWILIO_WEBHOOK_URL: "https://your-domain.com/webhooks/twilio/webhook"
  FRESHDESK_API_URL: "https://pocsctbnk.freshdesk.com/api/v2"
  LOG_LEVEL: "INFO"
  LOG_FILE_PATH: "/app/logs/rasa.log"
```

### **Secrets**
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: rasa-secrets
  namespace: sctbnk-rasa
type: Opaque
data:
  TWILIO_AUTH_TOKEN: <base64-encoded-auth-token>
  FRESHDESK_API_KEY: <base64-encoded-api-key>
  DATABASE_URL: <base64-encoded-db-url>
  ENCRYPTION_KEY: <base64-encoded-encryption-key>
```

### **Deployment**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sctbnk-rasa
  namespace: sctbnk-rasa
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sctbnk-rasa
  template:
    metadata:
      labels:
        app: sctbnk-rasa
    spec:
      containers:
      - name: rasa
        image: sctbnk-rasa:latest
        ports:
        - containerPort: 5005
          name: rasa-api
        - containerPort: 5055
          name: rasa-actions
        env:
        - name: RASA_TOKEN
          valueFrom:
            configMapKeyRef:
              name: rasa-config
              key: RASA_TOKEN
        - name: TWILIO_ACCOUNT_SID
          valueFrom:
            configMapKeyRef:
              name: rasa-config
              key: TWILIO_ACCOUNT_SID
        - name: TWILIO_AUTH_TOKEN
          valueFrom:
            secretKeyRef:
              name: rasa-secrets
              key: TWILIO_AUTH_TOKEN
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: rasa-secrets
              key: DATABASE_URL
        - name: FRESHDESK_API_KEY
          valueFrom:
            secretKeyRef:
              name: rasa-secrets
              key: FRESHDESK_API_KEY
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5005
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 5005
          initialDelaySeconds: 30
          periodSeconds: 10
        volumeMounts:
        - name: rasa-models
          mountPath: /app/models
        - name: rasa-logs
          mountPath: /app/logs
      volumes:
      - name: rasa-models
        persistentVolumeClaim:
          claimName: rasa-models-pvc
      - name: rasa-logs
        persistentVolumeClaim:
          claimName: rasa-logs-pvc
```

### **Service**
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: sctbnk-rasa-service
  namespace: sctbnk-rasa
spec:
  selector:
    app: sctbnk-rasa
  ports:
  - name: rasa-api
    protocol: TCP
    port: 5005
    targetPort: 5005
  - name: rasa-actions
    protocol: TCP
    port: 5055
    targetPort: 5055
  type: ClusterIP
```

### **Ingress**
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sctbnk-rasa-ingress
  namespace: sctbnk-rasa
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: sctbnk-rasa-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /webhooks
        pathType: Prefix
        backend:
          service:
            name: sctbnk-rasa-service
            port:
              number: 5005
      - path: /model
        pathType: Prefix
        backend:
          service:
            name: sctbnk-rasa-service
            port:
              number: 5005
```

### **Persistent Volume Claims**
```yaml
# k8s/persistent-volumes.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rasa-models-pvc
  namespace: sctbnk-rasa
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: nfs-storage

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rasa-logs-pvc
  namespace: sctbnk-rasa
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 20Gi
  storageClassName: nfs-storage
```

## Monitoreo y Observabilidad

### **Prometheus Configuration**
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sctbnk-rasa'
    static_configs:
      - targets: ['sctbnk-rasa-service:5005']
    metrics_path: '/metrics'
    scrape_interval: 10s
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: sctbnk-rasa
        action: keep
```

### **Grafana Dashboards**
- **Rasa Overview**: Conversaciones, intents, entidades
- **Twilio Metrics**: Llamadas, duración, estado
- **Freshdesk Metrics**: Tickets creados, resueltos, tiempo de respuesta
- **System Metrics**: CPU, Memory, Disk usage
- **Database Metrics**: Conexiones, consultas, performance

### **Alerting Rules**
```yaml
# monitoring/alerts.yml
groups:
- name: sctbnk-rasa
  rules:
  - alert: HighErrorRate
    expr: rate(rasa_errors_total[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate in Rasa Pro"
      description: "Error rate is {{ $value }}"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(rasa_response_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time in Rasa Pro"
      description: "95th percentile response time is {{ $value }}s"

  - alert: TwilioCallFailure
    expr: rate(twilio_call_failures_total[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High Twilio call failure rate"
      description: "Call failure rate is {{ $value }}"

  - alert: FreshdeskAPIFailure
    expr: rate(freshdesk_api_failures_total[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High Freshdesk API failure rate"
      description: "API failure rate is {{ $value }}"
```

## Logging Strategy

### **ELK Stack Configuration**
```yaml
# logging/logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "sctbnk-rasa" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
    date {
      match => [ "timestamp", "ISO8601" ]
    }
    
    # Anonymizar datos sensibles
    mutate {
      gsub => ["message", "\b\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\b", "**** **** **** ****"]
      gsub => ["message", "\b\d{4}\b", "****"]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "sctbnk-rasa-%{+YYYY.MM.dd}"
  }
}
```

### **Log Levels**
- **ERROR**: Errores críticos que requieren atención inmediata
- **WARN**: Advertencias que pueden indicar problemas
- **INFO**: Información general de operaciones
- **DEBUG**: Información detallada para debugging
- **TRACE**: Información muy detallada para troubleshooting

## Backup y Disaster Recovery

### **Database Backup Strategy**
```bash
#!/bin/bash
# backup-db.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
DB_NAME="sctbnk_cards"

# Create backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Keep only last 30 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload to cloud storage
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://sctbnk-backups/database/
```

### **Model Backup Strategy**
```bash
#!/bin/bash
# backup-models.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/models"
MODELS_DIR="/app/models"

# Create backup of trained models
tar -czf $BACKUP_DIR/models_$DATE.tar.gz -C $MODELS_DIR .

# Keep only last 7 days of model backups
find $BACKUP_DIR -name "models_*.tar.gz" -mtime +7 -delete

# Upload to cloud storage
aws s3 cp $BACKUP_DIR/models_$DATE.tar.gz s3://sctbnk-backups/models/
```

### **Recovery Procedures**
1. **Database Recovery**: Restore from latest backup
2. **Model Recovery**: Restore trained models
3. **Application Recovery**: Redeploy from container registry
4. **Data Validation**: Verify data integrity after recovery
5. **Service Verification**: Confirm all services are operational

## Security Considerations

### **Network Policies**
```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: sctbnk-rasa-network-policy
  namespace: sctbnk-rasa
spec:
  podSelector:
    matchLabels:
      app: sctbnk-rasa
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 5005
    - protocol: TCP
      port: 5055
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 80
```

### **Pod Security Standards**
```yaml
# k8s/pod-security.yaml
apiVersion: v1
kind: Pod
metadata:
  name: sctbnk-rasa-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  containers:
  - name: rasa
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: false
      capabilities:
        drop:
        - ALL
```

## Performance Optimization

### **Resource Limits**
- **CPU**: Request 500m, Limit 1000m per pod
- **Memory**: Request 512Mi, Limit 1Gi per pod
- **Replicas**: 3-5 based on load
- **Horizontal Pod Autoscaler**: Scale based on CPU/memory usage

### **Caching Strategy**
- **Redis**: Session storage and conversation context
- **Model Caching**: Cache trained models in memory
- **Response Caching**: Cache common responses

### **Database Optimization**
- **Connection Pooling**: Optimize database connections
- **Indexing**: Optimize queries for últimos 4 dígitos
- **Query Optimization**: Use prepared statements

## Deployment Checklist

### **Pre-Deployment**
- [ ] All tests passing
- [ ] Security scan completed
- [ ] Performance tests passed
- [ ] Documentation updated
- [ ] Stakeholder approval obtained
- [ ] Backup completed

### **Deployment**
- [ ] Backup current version
- [ ] Deploy to staging
- [ ] Run smoke tests
- [ ] Deploy to production
- [ ] Verify health checks
- [ ] Monitor metrics
- [ ] Test Twilio webhook
- [ ] Test Freshdesk integration

### **Post-Deployment**
- [ ] Verify all services operational
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Update deployment status
- [ ] Schedule post-mortem if needed
- [ ] Monitor Twilio call success rate
- [ ] Monitor Freshdesk ticket creation

## Environment-Specific Configurations

### **Development Environment**
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  rasa:
    environment:
      - NODE_ENV=development
      - LOG_LEVEL=DEBUG
      - RASA_TOKEN=dev_token
    volumes:
      - .:/app
      - /app/node_modules
```

### **Staging Environment**
```yaml
# k8s/staging/
# Similar to production but with:
# - Fewer replicas (1-2)
# - Lower resource limits
# - Staging database
# - Staging Twilio number
# - Staging Freshdesk workspace
```

### **Production Environment**
```yaml
# k8s/production/
# Full production configuration with:
# - High availability (3+ replicas)
# - Production resource limits
# - Production database
# - Production Twilio number
# - Production Freshdesk workspace
# - Full monitoring and alerting
```
