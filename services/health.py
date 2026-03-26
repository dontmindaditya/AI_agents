"""
Health Check Module

Comprehensive health check system for monitoring:
- Application health
- Database connectivity
- External AI API services
- WebSocket connections
- System resources

Usage:
    from services.health import HealthChecker, get_health_status
    
    checker = HealthChecker()
    status = await checker.check_all()
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import httpx
from config import settings
from utils.logger import setup_logger

from services.connection_pool import HTTPConnectionPool, get_http_client

logger = setup_logger(__name__)


class HealthStatus(str, Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status of a single component."""
    name: str
    status: HealthStatus
    latency_ms: Optional[float] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "latency_ms": self.latency_ms,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class HealthReport:
    """Complete health report."""
    overall_status: HealthStatus
    components: List[ComponentHealth]
    total_latency_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.overall_status.value,
            "overall": self.overall_status.value,
            "total_latency_ms": self.total_latency_ms,
            "timestamp": self.timestamp.isoformat(),
            "components": [c.to_dict() for c in self.components],
        }


class HealthChecker:
    """
    Comprehensive health checker for AgentHub services.
    
    Checks:
    - Database (Supabase)
    - External AI APIs (Anthropic, OpenAI, Groq, Gemini)
    - WebSocket manager state
    - System resources
    """
    
    def __init__(self):
        self.timeout = 5.0
        self._http_pool: Optional[HTTPConnectionPool] = None
    
    async def _get_http_pool(self) -> HTTPConnectionPool:
        """Get or create the HTTP connection pool."""
        if self._http_pool is None:
            self._http_pool = await get_http_client()
        return self._http_pool
    
    async def check_all(self) -> HealthReport:
        """Run all health checks and return comprehensive report."""
        start_time = time.time()
        components: List[ComponentHealth] = []
        
        check_tasks = [
            self.check_database(),
            self.check_anthropic(),
            self.check_openai(),
            self.check_groq(),
            self.check_gemini(),
            self.check_websocket(),
            self.check_system(),
        ]
        
        results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, ComponentHealth):
                components.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Health check error: {result}")
        
        total_latency = (time.time() - start_time) * 1000
        overall_status = self._determine_overall_status(components)
        
        return HealthReport(
            overall_status=overall_status,
            components=components,
            total_latency_ms=total_latency,
        )
    
    async def check_database(self) -> ComponentHealth:
        """Check Supabase database connectivity."""
        start = time.time()
        
        try:
            if not settings.SUPABASE_URL:
                return ComponentHealth(
                    name="database",
                    status=HealthStatus.UNKNOWN,
                    message="Supabase URL not configured",
                )
            
            http_pool = await self._get_http_pool()
            response = await http_pool.get(
                f"{settings.SUPABASE_URL}/rest/v1/",
                headers={
                    "apikey": settings.SUPABASE_KEY or "",
                    "Authorization": f"Bearer {settings.SUPABASE_KEY or ''}"
                }
            )
            
            latency = (time.time() - start) * 1000
            
            if response.status_code in (200, 201):
                return ComponentHealth(
                    name="database",
                    status=HealthStatus.HEALTHY,
                    latency_ms=round(latency, 2),
                    message="Database connection successful",
                )
            else:
                return ComponentHealth(
                    name="database",
                    status=HealthStatus.DEGRADED,
                    latency_ms=round(latency, 2),
                    message=f"Database returned status {response.status_code}",
                )
                
        except httpx.TimeoutException:
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.time() - start) * 1000,
                message="Database connection timeout",
            )
        except Exception as e:
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.time() - start) * 1000,
                message=f"Database connection failed: {str(e)}",
            )
    
    async def check_anthropic(self) -> ComponentHealth:
        """Check Anthropic API (Claude) connectivity."""
        start = time.time()
        
        if not settings.ANTHROPIC_API_KEY:
            return ComponentHealth(
                name="anthropic",
                status=HealthStatus.UNKNOWN,
                message="API key not configured",
            )
        
        try:
            http_pool = await self._get_http_pool()
            response = await http_pool.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.CLAUDE_MODEL,
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "ping"}]
                }
            )
            
            latency = (time.time() - start) * 1000
            
            if response.status_code in (200, 201):
                return ComponentHealth(
                    name="anthropic",
                    status=HealthStatus.HEALTHY,
                    latency_ms=round(latency, 2),
                    message=f"API responding with {settings.CLAUDE_MODEL}",
                )
            elif response.status_code == 401:
                return ComponentHealth(
                    name="anthropic",
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=round(latency, 2),
                    message="Invalid API key",
                )
            else:
                return ComponentHealth(
                    name="anthropic",
                    status=HealthStatus.DEGRADED,
                    latency_ms=round(latency, 2),
                    message=f"API returned status {response.status_code}",
                )
                    
        except httpx.TimeoutException:
            return ComponentHealth(
                name="anthropic",
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.time() - start) * 1000,
                message="API timeout",
            )
        except Exception as e:
            return ComponentHealth(
                name="anthropic",
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.time() - start) * 1000,
                message=f"API check failed: {str(e)}",
            )
    
    async def check_openai(self) -> ComponentHealth:
        """Check OpenAI API (GPT) connectivity."""
        start = time.time()
        
        if not settings.OPENAI_API_KEY:
            return ComponentHealth(
                name="openai",
                status=HealthStatus.UNKNOWN,
                message="API key not configured",
            )
        
        try:
            http_pool = await self._get_http_pool()
            response = await http_pool.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.GPT_MODEL,
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "ping"}]
                }
            )
            
            latency = (time.time() - start) * 1000
            
            if response.status_code in (200, 201):
                return ComponentHealth(
                    name="openai",
                    status=HealthStatus.HEALTHY,
                    latency_ms=round(latency, 2),
                    message=f"API responding with {settings.GPT_MODEL}",
                )
            elif response.status_code == 401:
                return ComponentHealth(
                    name="openai",
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=round(latency, 2),
                    message="Invalid API key",
                )
            else:
                return ComponentHealth(
                    name="openai",
                    status=HealthStatus.DEGRADED,
                    latency_ms=round(latency, 2),
                    message=f"API returned status {response.status_code}",
                )
                    
        except httpx.TimeoutException:
            return ComponentHealth(
                name="openai",
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.time() - start) * 1000,
                message="API timeout",
            )
        except Exception as e:
            return ComponentHealth(
                name="openai",
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.time() - start) * 1000,
                message=f"API check failed: {str(e)}",
            )
    
    async def check_groq(self) -> ComponentHealth:
        """Check Groq API connectivity."""
        start = time.time()
        
        if not settings.GROQ_API_KEY:
            return ComponentHealth(
                name="groq",
                status=HealthStatus.UNKNOWN,
                message="API key not configured",
            )
        
        try:
            http_pool = await self._get_http_pool()
            response = await http_pool.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.GROQ_MODEL,
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "ping"}]
                }
            )
            
            latency = (time.time() - start) * 1000
            
            if response.status_code in (200, 201):
                return ComponentHealth(
                    name="groq",
                    status=HealthStatus.HEALTHY,
                    latency_ms=round(latency, 2),
                    message=f"API responding with {settings.GROQ_MODEL}",
                )
            elif response.status_code == 401:
                return ComponentHealth(
                    name="groq",
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=round(latency, 2),
                    message="Invalid API key",
                )
            else:
                return ComponentHealth(
                    name="groq",
                    status=HealthStatus.DEGRADED,
                    latency_ms=round(latency, 2),
                    message=f"API returned status {response.status_code}",
                )
                    
        except httpx.TimeoutException:
            return ComponentHealth(
                name="groq",
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.time() - start) * 1000,
                message="API timeout",
            )
        except Exception as e:
            return ComponentHealth(
                name="groq",
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.time() - start) * 1000,
                message=f"API check failed: {str(e)}",
            )
    
    async def check_gemini(self) -> ComponentHealth:
        """Check Google Gemini API connectivity."""
        start = time.time()
        
        if not settings.GEMINI_API_KEY:
            return ComponentHealth(
                name="gemini",
                status=HealthStatus.UNKNOWN,
                message="API key not configured",
            )
        
        try:
            http_pool = await self._get_http_pool()
            response = await http_pool.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent",
                params={"key": settings.GEMINI_API_KEY},
                headers={"content-type": "application/json"},
                json={"contents": [{"parts": [{"text": "ping"}]}]}
            )
            
            latency = (time.time() - start) * 1000
            
            if response.status_code in (200, 201):
                return ComponentHealth(
                    name="gemini",
                    status=HealthStatus.HEALTHY,
                    latency_ms=round(latency, 2),
                    message=f"API responding with {settings.GEMINI_MODEL}",
                )
            elif response.status_code == 401:
                return ComponentHealth(
                    name="gemini",
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=round(latency, 2),
                    message="Invalid API key",
                )
            else:
                return ComponentHealth(
                    name="gemini",
                    status=HealthStatus.DEGRADED,
                    latency_ms=round(latency, 2),
                    message=f"API returned status {response.status_code}",
                )
                    
        except httpx.TimeoutException:
            return ComponentHealth(
                name="gemini",
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.time() - start) * 1000,
                message="API timeout",
            )
        except Exception as e:
            return ComponentHealth(
                name="gemini",
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.time() - start) * 1000,
                message=f"API check failed: {str(e)}",
            )
    
    async def check_websocket(self) -> ComponentHealth:
        """Check WebSocket manager state."""
        start = time.time()
        
        try:
            from dependencies import get_ws_manager
            
            ws_manager = get_ws_manager()
            connection_count = len(ws_manager.active_connections)
            
            return ComponentHealth(
                name="websocket",
                status=HealthStatus.HEALTHY,
                latency_ms=(time.time() - start) * 1000,
                message=f"{connection_count} active connections",
                details={"active_connections": connection_count},
            )
            
        except RuntimeError:
            return ComponentHealth(
                name="websocket",
                status=HealthStatus.UNKNOWN,
                latency_ms=(time.time() - start) * 1000,
                message="WebSocket manager not initialized",
            )
        except Exception as e:
            return ComponentHealth(
                name="websocket",
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.time() - start) * 1000,
                message=f"WebSocket check failed: {str(e)}",
            )
    
    async def check_system(self) -> ComponentHealth:
        """Check system resources."""
        start = time.time()
        
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": round(memory.available / 1024 / 1024, 2),
            }
            
            if cpu_percent > 90 or memory.percent > 90:
                status = HealthStatus.DEGRADED
                message = f"High resource usage: CPU {cpu_percent:.1f}%, Memory {memory.percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Resources OK: CPU {cpu_percent:.1f}%, Memory {memory.percent:.1f}%"
            
            return ComponentHealth(
                name="system",
                status=status,
                latency_ms=(time.time() - start) * 1000,
                message=message,
                details=details,
            )
            
        except ImportError:
            return ComponentHealth(
                name="system",
                status=HealthStatus.UNKNOWN,
                latency_ms=(time.time() - start) * 1000,
                message="psutil not installed - system checks skipped",
            )
        except Exception as e:
            return ComponentHealth(
                name="system",
                status=HealthStatus.UNKNOWN,
                latency_ms=(time.time() - start) * 1000,
                message=f"System check skipped: {str(e)}",
            )
    
    def _determine_overall_status(self, components: List[ComponentHealth]) -> HealthStatus:
        """Determine overall health status from components."""
        if not components:
            return HealthStatus.UNKNOWN
        
        statuses = [c.status for c in components]
        
        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        elif any(s == HealthStatus.UNKNOWN for s in statuses):
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


health_checker = HealthChecker()


async def get_health_status() -> Dict[str, Any]:
    """Get full health status report."""
    report = await health_checker.check_all()
    return report.to_dict()


async def get_simple_health() -> Dict[str, str]:
    """Get simple health status (for quick checks)."""
    report = await health_checker.check_all()
    return {"status": report.overall_status.value}
