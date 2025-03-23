SOCIAL_INTELLIGENCE_READ_DB_SECRET_ID = 'social-intelligence-read-db'

GET_ALL_PROXY_QUERY = """
SELECT address, port, username, password
FROM blockchains.proxies
WHERE status
"""
