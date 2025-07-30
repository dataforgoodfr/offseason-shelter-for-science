import redis
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RedisUrlCache:
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0, 
                 redis_password=None, expiry_hours=24):
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # Test de connexion
            self.redis_client.ping()
            logger.info(f"Connexion Redis établie: {redis_host}:{redis_port}")
            
        except Exception as e:
            logger.error(f"Erreur connexion Redis: {e}")
            # Fallback vers un cache en mémoire
            self.redis_client = None
            self._memory_cache = {}
            logger.warning("Utilisation du cache en mémoire comme fallback")
        
        self.expiry_seconds = expiry_hours * 3600
        self.key_prefix = "scraper:url:"
        
    def _get_url_key(self, url: str) -> str:
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        return f"{self.key_prefix}{url_hash}"
    
    def is_url_scraped(self, url: str) -> bool:
        try:
            if self.redis_client:
                key = self._get_url_key(url)
                return self.redis_client.exists(key) > 0
            else:
                # Fallback mémoire
                return url in self._memory_cache
                
        except Exception as e:
            logger.error(f"Erreur vérification cache pour {url}: {e}")
            return False
    
    def mark_url_scraped(self, url: str, metadata: Optional[Dict[Any, Any]] = None) -> bool:
        print("*" * 60)
        print("*" * 60)
        print("*" * 60)
        print("*" * 60)
        print(f"Marquage de l'URL comme scrapée: {url}")
        print("*" * 60)
        print("*" * 60)
        print("*" * 60)
        print("*" * 60)
        try:
            cache_data = {
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            if self.redis_client:
                key = self._get_url_key(url)
                # Stockage avec expiration automatique
                self.redis_client.setex(
                    key, 
                    self.expiry_seconds, 
                    json.dumps(cache_data)
                )
                logger.debug(f"URL marquée comme scrapée: {url}")
            else:
                # Fallback mémoire
                self._memory_cache[url] = cache_data
                logger.debug(f"URL marquée en mémoire: {url}")
                
            return True
            
        except Exception as e:
            logger.error(f"Erreur marquage cache pour {url}: {e}")
            return False
    
    def get_url_info(self, url: str) -> Optional[Dict]:
        try:
            if self.redis_client:
                key = self._get_url_key(url)
                data = self.redis_client.get(key)
                if data:
                    return json.loads(data)
            else:
                # Fallback mémoire
                return self._memory_cache.get(url)
                
        except Exception as e:
            logger.error(f"Erreur récupération info pour {url}: {e}")
        
        return None
    
    def clear_cache(self) -> bool:
        try:
            if self.redis_client:
                # Supprime toutes les clés avec le préfixe
                keys = self.redis_client.keys(f"{self.key_prefix}*")
                if keys:
                    self.redis_client.delete(*keys)
                logger.info(f"🗑️ Cache Redis vidé: {len(keys)} URLs supprimées")
            else:
                self._memory_cache.clear()
                logger.info("🗑️ Cache mémoire vidé")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur vidage cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        try:
            if self.redis_client:
                keys = self.redis_client.keys(f"{self.key_prefix}*")
                return {
                    'total_urls': len(keys),
                    'cache_type': 'redis',
                    'expiry_hours': self.expiry_seconds // 3600,
                    'redis_info': {
                        'used_memory': self.redis_client.info().get('used_memory_human', 'N/A'),
                        'connected_clients': self.redis_client.info().get('connected_clients', 0)
                    }
                }
            else:
                return {
                    'total_urls': len(self._memory_cache),
                    'cache_type': 'memory',
                    'expiry_hours': self.expiry_seconds // 3600,
                    'memory_info': 'Fallback cache'
                }
                
        except Exception as e:
            logger.error(f"Erreur statistiques cache: {e}")
            return {'error': str(e)}

