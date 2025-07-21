import os
import redis
import json
import logging
from typing import Any, Optional, Dict, List
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


class RedisClient:
    """
    Centralized Redis client for use across different containers
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize Redis client
        
        Args:
            redis_url: Redis connection URL. If None, uses settings.redis_url
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self._client = None
        self._connection_pool = None
        
    def _get_connection_params(self) -> Dict[str, Any]:
        """Parse Redis URL and return connection parameters"""
        parsed = urlparse(self.redis_url)
        
        params = {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 6379,
            'decode_responses': True,
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'retry_on_timeout': True,
            'health_check_interval': 30
        }
        
        if parsed.password:
            params['password'] = parsed.password
            
        if parsed.path and len(parsed.path) > 1:
            # Remove leading slash and convert to int
            params['db'] = int(parsed.path[1:])
        else:
            params['db'] = 0
            
        return params
    
    @property
    def client(self) -> redis.Redis:
        """Get Redis client instance (lazy initialization)"""
        if self._client is None:
            try:
                connection_params = self._get_connection_params()
                self._connection_pool = redis.ConnectionPool(**connection_params)
                self._client = redis.Redis(connection_pool=self._connection_pool)
                
                # Test connection
                self._client.ping()
                logger.info(f"Redis connection established to {connection_params['host']}:{connection_params['port']}")
                
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
                
        return self._client
    
    def ping(self) -> bool:
        """Test Redis connection"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        Set a key-value pair in Redis
        
        Args:
            key: Redis key
            value: Value to store (will be JSON serialized if not string)
            ex: Expiration time in seconds
        """
        try:
            if not isinstance(value, str):
                value = json.dumps(value)
            return self.client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis SET failed for key {key}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from Redis
        
        Args:
            key: Redis key
            default: Default value if key doesn't exist
        """
        try:
            value = self.client.get(key)
            if value is None:
                return default
            
            # Try to deserialize JSON, fallback to string
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"Redis GET failed for key {key}: {e}")
            return default
    
    def delete(self, *keys: str) -> int:
        """Delete one or more keys"""
        try:
            return self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE failed for keys {keys}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS failed for key {key}: {e}")
            return False
    
    def expire(self, key: str, time: int) -> bool:
        """Set expiration time for a key"""
        try:
            return self.client.expire(key, time)
        except Exception as e:
            logger.error(f"Redis EXPIRE failed for key {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """Get time to live for a key"""
        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL failed for key {key}: {e}")
            return -1
    
    def hset(self, name: str, mapping: Dict[str, Any]) -> int:
        """Set hash fields"""
        try:
            # Convert non-string values to JSON
            json_mapping = {}
            for k, v in mapping.items():
                if not isinstance(v, str):
                    json_mapping[k] = json.dumps(v)
                else:
                    json_mapping[k] = v
            return self.client.hset(name, mapping=json_mapping)
        except Exception as e:
            logger.error(f"Redis HSET failed for hash {name}: {e}")
            return 0
    
    def hget(self, name: str, key: str, default: Any = None) -> Any:
        """Get hash field value"""
        try:
            value = self.client.hget(name, key)
            if value is None:
                return default
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"Redis HGET failed for hash {name}, key {key}: {e}")
            return default
    
    def hgetall(self, name: str) -> Dict[str, Any]:
        """Get all hash fields"""
        try:
            data = self.client.hgetall(name)
            
            # Try to deserialize JSON values
            result = {}
            for k, v in data.items():
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    result[k] = v
                    
            return result
            
        except Exception as e:
            logger.error(f"Redis HGETALL failed for hash {name}: {e}")
            return {}
    
    def lpush(self, name: str, *values: Any) -> int:
        """Push values to the left of a list"""
        try:
            json_values = []
            for value in values:
                if not isinstance(value, str):
                    json_values.append(json.dumps(value))
                else:
                    json_values.append(value)
            return self.client.lpush(name, *json_values)
        except Exception as e:
            logger.error(f"Redis LPUSH failed for list {name}: {e}")
            return 0
    
    def rpush(self, name: str, *values: Any) -> int:
        """Push values to the right of a list"""
        try:
            json_values = []
            for value in values:
                if not isinstance(value, str):
                    json_values.append(json.dumps(value))
                else:
                    json_values.append(value)
            return self.client.rpush(name, *json_values)
        except Exception as e:
            logger.error(f"Redis RPUSH failed for list {name}: {e}")
            return 0
    
    def lrange(self, name: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get list elements in range"""
        try:
            values = self.client.lrange(name, start, end)
            
            # Try to deserialize JSON values
            result = []
            for value in values:
                try:
                    result.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.append(value)
                    
            return result
            
        except Exception as e:
            logger.error(f"Redis LRANGE failed for list {name}: {e}")
            return []
    
    def publish(self, channel: str, message: Any) -> int:
        """Publish message to a channel"""
        try:
            if not isinstance(message, str):
                message = json.dumps(message)
            return self.client.publish(channel, message)
        except Exception as e:
            logger.error(f"Redis PUBLISH failed for channel {channel}: {e}")
            return 0
    
    def close(self):
        """Close Redis connection"""
        try:
            if self._client:
                self._client.close()
            if self._connection_pool:
                self._connection_pool.disconnect()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")


# Global Redis client instance
redis_client = RedisClient()


# Session management utilities
class RedisSessionManager:
    """Redis-based session management"""
    
    def __init__(self, client: RedisClient = None, prefix: str = "session"):
        self.client = client or redis_client
        self.prefix = prefix
    
    def create_session(self, session_id: str, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Create a new session"""
        key = f"{self.prefix}:{session_id}"
        return self.client.set(key, data, ex=ttl)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        key = f"{self.prefix}:{session_id}"
        return self.client.get(key)
    
    def update_session(self, session_id: str, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Update session data"""
        key = f"{self.prefix}:{session_id}"
        return self.client.set(key, data, ex=ttl)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        key = f"{self.prefix}:{session_id}"
        return bool(self.client.delete(key))
    
    def extend_session(self, session_id: str, ttl: int = 3600) -> bool:
        """Extend session TTL"""
        key = f"{self.prefix}:{session_id}"
        return self.client.expire(key, ttl)


# Cache utilities
class RedisCache:
    """Redis-based caching utilities"""
    
    def __init__(self, client: RedisClient = None, prefix: str = "cache"):
        self.client = client or redis_client
        self.prefix = prefix
    
    def set_cache(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set cache value"""
        cache_key = f"{self.prefix}:{key}"
        return self.client.set(cache_key, value, ex=ttl)
    
    def get_cache(self, key: str, default: Any = None) -> Any:
        """Get cache value"""
        cache_key = f"{self.prefix}:{key}"
        return self.client.get(cache_key, default)
    
    def delete_cache(self, key: str) -> bool:
        """Delete cache entry"""
        cache_key = f"{self.prefix}:{key}"
        return bool(self.client.delete(cache_key))
    
    def clear_cache_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern"""
        try:
            cache_pattern = f"{self.prefix}:{pattern}"
            keys = self.client.client.keys(cache_pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Failed to clear cache pattern {pattern}: {e}")
            return 0


# Global instances
session_manager = RedisSessionManager()
cache_manager = RedisCache()