import asyncio
import random
from typing import Optional
from datetime import datetime, timedelta
import lorem

class RateLimitExceeded(Exception):
    """Raised when too many requests are made within a time window"""
    pass

class ServiceUnavailable(Exception):
    """Raised when the service is temporarily unavailable"""
    pass

class InvalidRequestError(Exception):
    """Raised when the request is invalid"""
    pass


RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 60
ERROR_PROBABILITY = 0.05

class TotallyRealRetriever:
    def __init__(self):
        self._requests = []
        self._rate_limit_requests = RATE_LIMIT_REQUESTS
        self._rate_limit_window = RATE_LIMIT_WINDOW_SECONDS
        self._error_probability = ERROR_PROBABILITY

    def _check_rate_limit(self):
        """Check if we've exceeded our rate limit"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self._rate_limit_window)
        
        # Clean up old requests
        self._requests = [ts for ts in self._requests if ts > window_start]
        
        if len(self._requests) >= self._rate_limit_requests:
            raise RateLimitExceeded(
                f"Rate limit of {self._rate_limit_requests} requests per {self._rate_limit_window} seconds exceeded"
            )

    def _maybe_error(self):
        """Randomly throw errors to simulate API instability"""
        if random.random() < self._error_probability:
            error = random.choice([
                ServiceUnavailable("Service is temporarily unavailable"),
                ConnectionError("Connection reset by peer"),
                TimeoutError("Request timed out")
            ])
            raise error

    async def retrieve(self, query: str, top_k: Optional[int] = 3) -> list[dict]:
        """
        Retrieve documents similar to the query.
        
        Args:
            query: The query text
            top_k: Number of results to return
            
        Returns:
            List of documents with id, content, and metadata
        
        Raises:
            RateLimitExceeded: If too many requests are made
            ServiceUnavailable: If service is temporarily down
            InvalidRequestError: If request parameters are invalid
            ConnectionError: If connection fails
            TimeoutError: If request times out
        """
        if not isinstance(query, str) or not query.strip():
            raise InvalidRequestError("Query must be a non-empty string")
            
        if not isinstance(top_k, int) or top_k < 1:
            raise InvalidRequestError("top_k must be a positive integer")

        # Check rate limit
        self._check_rate_limit()
        
        # Record this request
        self._requests.append(datetime.now())
        
        # Maybe throw an error
        self._maybe_error()
        
        # Simulate network latency
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Generate random documents
        results = []
        for _ in range(top_k):
            doc = {
                "id": f"doc_{random.randint(1000, 9999)}",
                "content": lorem.paragraph(),
                "metadata": {
                    "file_name": f"source_{random.randint(1, 5)}.txt",
                    "timestamp": datetime.now().isoformat(),
                    "relevance_score": random.random()
                }
            }
            results.append(doc)
            
        return results


async def _main():
    retriever = TotallyRealRetriever()
    results = await retriever.retrieve("What is the capital of France?")
    print(results)

    jobs = [retriever.retrieve(f"What is the capital of {country}?") for country in ["France", "Germany", "Italy", "Spain", "Portugal", "Greece", "Turkey", "Russia", "China", "Japan", "Korea", "India", "Australia", "New Zealand", "Canada", "United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Portugal", "Greece", "Turkey", "Russia", "China", "Japan", "Korea", "India", "Australia", "New Zealand", "Canada", "United States", "United Kingdom"]]
    results = await asyncio.gather(*jobs)
    print(results)

if __name__ == "__main__":
    asyncio.run(_main())
