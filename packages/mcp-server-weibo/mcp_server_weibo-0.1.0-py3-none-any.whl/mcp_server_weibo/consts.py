# Default HTTP headers for Weibo API requests
DEFAULT_HEADERS = { 'Content-Type': 'application/json' }

# URL template for fetching user profile information
# {userId} will be replaced with the actual user ID
PROFILE_URL = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={userId}'

# URL template for fetching user's Weibo feeds
# {userId}: User's unique identifier
# {containerId}: Container ID for the user's feed
# {sinceId}: ID of the last feed for pagination
FEEDS_URL = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={userId}&containerid={containerId}&since_id={sinceId}'