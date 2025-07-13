import logging
from django.core.cache import cache
from django_redis import get_redis_connection
from .models import Property

logger = logging.getLogger(__name__)


def get_all_properties():
    """
    Get all properties with caching.
    
    Checks Redis cache first, if not found, fetches from database
    and stores in cache for 1 hour.
    
    Returns:
        QuerySet: All Property objects
    """
    cache_key = 'all_properties'
    
    # Try to get from cache first
    properties = cache.get(cache_key)
    
    if properties is None:
        # Not in cache, fetch from database
        logger.info("Cache miss: Fetching properties from database")
        properties = list(Property.objects.all())
        
        # Store in cache for 1 hour (3600 seconds)
        cache.set(cache_key, properties, 3600)
        logger.info(f"Cached {len(properties)} properties for 1 hour")
    else:
        logger.info(f"Cache hit: Retrieved {len(properties)} properties from cache")
    
    return properties


def get_redis_cache_metrics():
    """
    Get Redis cache hit/miss metrics and calculate hit ratio.
    
    Returns:
        dict: Dictionary containing cache metrics
    """
    try:
        # Get Redis connection
        redis_conn = get_redis_connection("default")
        
        # Get Redis info
        redis_info = redis_conn.info()
        
        # Extract keyspace statistics
        keyspace_hits = redis_info.get('keyspace_hits', 0)
        keyspace_misses = redis_info.get('keyspace_misses', 0)
        
        # Calculate hit ratio
        total_requests = keyspace_hits + keyspace_misses
        hit_ratio = (keyspace_hits / total_requests) * 100 if total_requests > 0 else 0
        
        metrics = {
            'keyspace_hits': keyspace_hits,
            'keyspace_misses': keyspace_misses,
            'total_requests': total_requests,
            'hit_ratio': round(hit_ratio, 2),
            'hit_ratio_formatted': f"{hit_ratio:.2f}%"
        }
        
        # Log metrics
        logger.info(f"Redis Cache Metrics: {metrics}")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting Redis cache metrics: {e}")
        return {
            'error': str(e),
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'total_requests': 0,
            'hit_ratio': 0,
            'hit_ratio_formatted': "0.00%"
        }


def clear_property_cache():
    """
    Clear the all_properties cache.
    Used by signal handlers when properties are modified.
    """
    cache_key = 'all_properties'
    cache.delete(cache_key)
    logger.info("Cleared all_properties cache")
