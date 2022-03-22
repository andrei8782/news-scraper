class BitcoinmagazineScraper:
    def __init__(self, article_limit=None, ignore_overlap=False) -> None:
        super().__init__("bitcoinmagazine", article_limit, ignore_overlap)