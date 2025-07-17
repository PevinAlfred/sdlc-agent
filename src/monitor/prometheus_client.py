
from prometheus_api_client import PrometheusConnect
from loguru import logger

def fetch_metrics(prometheus_url, query="up"):
    """
    Fetch metrics from Prometheus using prometheus-api-client.
    Returns the result of the query as a Python object.
    """
    try:
        prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)
        logger.info(f"Querying Prometheus: {query}")
        result = prom.custom_query(query=query)
        logger.info(f"Prometheus query result: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch metrics from Prometheus: {e}")
        raise
