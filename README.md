# Erp-controlplane.ai
AI-Based ERP Security & Intelligence — Technical Specification & Source Manual
​📌 Executive Summary
​Modern Enterprise Resource Planning (ERP) environments process vast volumes of sensitive financial, procurement, and HR data. Traditional rule-based security systems suffer from two core failure modes:
​Alert Fatigue (Overflagging): Up to 85% of security alerts represent benign operational spikes (e.g., month-end financial closing).
​Multi-Turn Conversational Exfiltration: Adversaries use natural-language interfaces to extract sensitive records piecemeal without triggering single-request rule thresholds.
​This platform implements a 9-tier hybrid anomaly detection engine, stateful session context tracking, dynamic business-context suppression, and cross-domain FinOps cloud billing correlation to protect ERP ecosystems.
version: '3.8'

services:
  redis-state-store:
    image: redis:7.2-alpine
    container_name: erp-state-store
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  ai-detection-engine:
    image: python:3.11-slim
    container_name: erp-ai-detection-engine
    volumes:
      - .:/app
    working_dir: /app
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis-state-store
      - REDIS_PORT=6379
      - RISK_THRESHOLD_HIGH=75
      - RISK_THRESHOLD_MED=40
    command: >
      sh -c "pip install fastapi uvicorn redis pydantic pydantic-settings numpy &&
             uvicorn main:app --host 0.0.0.0 --port 8000"
    depends_on:
      redis-state-store:
        condition: service_healthy
