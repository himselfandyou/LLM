"""
Health Check API Routes

API endpoints for health monitoring and system status.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
import psutil
import time
from datetime import datetime

from ...core.config import get_settings
from ...core.database import DatabaseManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime: float
    services: Dict[str, str]

class SystemInfo(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]

class DetailedHealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime: float
    services: Dict[str, str]
    system_info: SystemInfo
    database_status: str

# Global variables for tracking
start_time = time.time()

def get_uptime() -> float:
    """Get server uptime in seconds."""
    return time.time() - start_time

def check_database_health() -> str:
    """Check database connection health."""
    try:
        settings = get_settings()
        if settings.database_url:
            db_manager = DatabaseManager(settings.database_url)
            session = db_manager.get_session()
            session.execute("SELECT 1")
            db_manager.close_session(session)
            return "healthy"
        else:
            return "not_configured"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return "unhealthy"

def get_system_info() -> SystemInfo:
    """Get system resource information."""
    try:
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage = (disk.used / disk.total) * 100
        
        # Network I/O
        network = psutil.net_io_counters()
        network_io = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv
        }
        
        return SystemInfo(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_io
        )
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return SystemInfo(
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0,
            network_io={"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0}
        )

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        Basic health status
    """
    try:
        settings = get_settings()
        
        # Check services
        services = {
            "api": "healthy",
            "database": check_database_health()
        }
        
        # Determine overall status
        overall_status = "healthy"
        if any(status != "healthy" for status in services.values()):
            overall_status = "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version=settings.__class__.__version__ if hasattr(settings, '__version__') else "1.0.0",
            uptime=get_uptime(),
            services=services
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            uptime=get_uptime(),
            services={"api": "unhealthy", "database": "unknown"}
        )

@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Detailed health check endpoint with system information.
    
    Returns:
        Detailed health status with system metrics
    """
    try:
        settings = get_settings()
        
        # Check services
        services = {
            "api": "healthy",
            "database": check_database_health()
        }
        
        # Get system information
        system_info = get_system_info()
        
        # Determine overall status
        overall_status = "healthy"
        if any(status != "healthy" for status in services.values()):
            overall_status = "degraded"
        
        # Check if system resources are critical
        if system_info.cpu_usage > 90 or system_info.memory_usage > 90 or system_info.disk_usage > 90:
            overall_status = "critical"
        
        return DetailedHealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version=settings.__class__.__version__ if hasattr(settings, '__version__') else "1.0.0",
            uptime=get_uptime(),
            services=services,
            system_info=system_info,
            database_status=services["database"]
        )
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return DetailedHealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            uptime=get_uptime(),
            services={"api": "unhealthy", "database": "unknown"},
            system_info=SystemInfo(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0}
            ),
            database_status="unknown"
        )

@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes.
    
    Returns:
        Readiness status
    """
    try:
        # Check if all critical services are ready
        database_status = check_database_health()
        
        if database_status == "healthy":
            return {"status": "ready", "timestamp": datetime.utcnow()}
        else:
            return {"status": "not_ready", "timestamp": datetime.utcnow()}
            
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {"status": "not_ready", "timestamp": datetime.utcnow()}

@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes.
    
    Returns:
        Liveness status
    """
    try:
        # Basic liveness check - just ensure the API is responding
        return {"status": "alive", "timestamp": datetime.utcnow()}
        
    except Exception as e:
        logger.error(f"Liveness check failed: {str(e)}")
        return {"status": "dead", "timestamp": datetime.utcnow()}

@router.get("/metrics")
async def metrics():
    """
    Prometheus-style metrics endpoint.
    
    Returns:
        System metrics in Prometheus format
    """
    try:
        system_info = get_system_info()
        uptime = get_uptime()
        
        metrics = f"""# HELP mcp_server_uptime_seconds Server uptime in seconds
# TYPE mcp_server_uptime_seconds gauge
mcp_server_uptime_seconds {uptime}

# HELP mcp_server_cpu_usage_percent CPU usage percentage
# TYPE mcp_server_cpu_usage_percent gauge
mcp_server_cpu_usage_percent {system_info.cpu_usage}

# HELP mcp_server_memory_usage_percent Memory usage percentage
# TYPE mcp_server_memory_usage_percent gauge
mcp_server_memory_usage_percent {system_info.memory_usage}

# HELP mcp_server_disk_usage_percent Disk usage percentage
# TYPE mcp_server_disk_usage_percent gauge
mcp_server_disk_usage_percent {system_info.disk_usage}

# HELP mcp_server_network_bytes_sent Network bytes sent
# TYPE mcp_server_network_bytes_sent counter
mcp_server_network_bytes_sent {system_info.network_io['bytes_sent']}

# HELP mcp_server_network_bytes_recv Network bytes received
# TYPE mcp_server_network_bytes_recv counter
mcp_server_network_bytes_recv {system_info.network_io['bytes_recv']}

# HELP mcp_server_network_packets_sent Network packets sent
# TYPE mcp_server_network_packets_sent counter
mcp_server_network_packets_sent {system_info.network_io['packets_sent']}

# HELP mcp_server_network_packets_recv Network packets received
# TYPE mcp_server_network_packets_recv counter
mcp_server_network_packets_recv {system_info.network_io['packets_recv']}
"""
        
        return metrics
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}")
        return "# Error collecting metrics"

@router.get("/info")
async def system_info():
    """
    Get detailed system information.
    
    Returns:
        Detailed system information
    """
    try:
        system_info = get_system_info()
        
        # Get additional system information
        additional_info = {
            "platform": psutil.sys.platform,
            "python_version": psutil.sys.version,
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2)
        }
        
        return {
            "system_info": system_info.dict(),
            "additional_info": additional_info,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"System info collection failed: {str(e)}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow()
        }