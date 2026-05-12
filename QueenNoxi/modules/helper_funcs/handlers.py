from pyrate_limiter import (
    BucketFullException,
    Duration,
    Limiter,
    MemoryListBucket,
    RequestRate,
)
import QueenNoxi.modules.sql.blacklistusers_sql as sql
from QueenNoxi import DEMONS, DEV_USERS, DRAGONS, TIGERS, WOLVES

class AntiSpam:
    def __init__(self):
        self.whitelist = (
            (DEV_USERS or [])
            + (DRAGONS or [])
            + (WOLVES or [])
            + (DEMONS or [])
            + (TIGERS or [])
        )
        # 6 requests per 15 seconds, 20 per min, 100 per hour, 1000 per day
        self.rates = [
            RequestRate(6, 15 * Duration.SECOND),
            RequestRate(20, Duration.MINUTE),
            RequestRate(100, Duration.HOUR),
            RequestRate(1000, Duration.DAY),
        ]
        self.limiter = Limiter(*self.rates, bucket_class=MemoryListBucket)

    def check_user(self, user_id: int):
        """
        Return True if user is to be ignored (spaming) else False
        """
        if user_id in self.whitelist:
            return False
        try:
            self.limiter.try_acquire(user_id)
            return False
        except BucketFullException:
            return True

SpamChecker = AntiSpam()

def is_user_blacklisted(user_id: int) -> bool:
    return sql.is_user_blacklisted(user_id)
