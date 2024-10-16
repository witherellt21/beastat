from .web_scraper import BaseWebScraper


class ScraperManager:

    MANAGERS: dict[str, "ScraperManager"] = {}

    def __new__(cls):
        raise Exception(
            "Cannot be directly instantiated. Instead call 'get_instance' with a specified name for the manager."
        )

    @classmethod
    def get_instance(cls, instance_name: str = "main"):
        if not ScraperManager.MANAGERS.get(instance_name):
            ScraperManager.MANAGERS[instance_name] = super(ScraperManager, cls).__new__(
                cls
            )
            ScraperManager.MANAGERS[instance_name].__init__()
        return ScraperManager.MANAGERS[instance_name]

    def __init__(self):
        self.scrapers: dict[str, BaseWebScraper] = {}

    def register(self, scraper: BaseWebScraper):
        if not isinstance(scraper, BaseWebScraper):
            raise Exception(
                "Scraper must be an instance of the 'BaseWebScraper' class."
            )

        self.scrapers[scraper.name] = scraper

    def get_scraper(self, name: str) -> BaseWebScraper:
        if name not in self.scrapers:
            raise Exception("Scraper {} has not been registered.".format(name))

        return self.scrapers[name]

    def remove_scraper(self, name: str) -> None:
        if name in self.scrapers:
            del self.scrapers[name]

    def run(self):
        for scraper in self.scrapers.values():

            if scraper.RUNNING:
                scraper.daemon = True
                scraper.configure()

                scraper.start()

        return self.scrapers

    def kill(self):
        for scraper in self.scrapers.values():
            scraper.kill()
