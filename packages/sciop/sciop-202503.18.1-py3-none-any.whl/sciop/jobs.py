from sciop import scheduler, services
from sciop.config import config


@scheduler.interval(
    minutes=config.tracker_scraping.job_interval, enabled=config.tracker_scraping.enabled
)
async def scrape_torrent_stats() -> None:
    await services.scrape_torrent_stats()
