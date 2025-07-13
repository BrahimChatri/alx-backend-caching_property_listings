from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import Property
from .utils import get_all_properties, get_redis_cache_metrics


@cache_page(60 * 15)  # Cache for 15 minutes
def property_list(request):
    """Return all properties with caching"""
    properties = get_all_properties()
    
    # Convert queryset to list of dictionaries for JSON response
    properties_data = [
        {
            'id': prop.id,
            'title': prop.title,
            'description': prop.description,
            'price': str(prop.price),
            'location': prop.location,
            'created_at': prop.created_at.isoformat(),
        }
        for prop in properties
    ]
    
    return JsonResponse({
        'properties': properties_data,
        'count': len(properties_data)
    })


def cache_metrics(request):
    """Return Redis cache metrics"""
    metrics = get_redis_cache_metrics()
    return JsonResponse({
        'cache_metrics': metrics,
        'message': 'Redis cache metrics retrieved successfully'
    })
