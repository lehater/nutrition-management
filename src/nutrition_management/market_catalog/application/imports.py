from nutrition_management.market_catalog.domain.model import FulfilmentChannel, Offer, ProductCard


def import_product(repository, product: ProductCard) -> None:
    if product.edible_grams_per_package <= 0:
        raise ValueError("product package must resolve to positive edible grams")
    repository.add_product(product)


def import_channel(repository, channel: FulfilmentChannel) -> None:
    repository.add_channel(channel)


def import_offer(repository, offer: Offer) -> None:
    if offer.price < 0:
        raise ValueError("offer price must be non-negative")
    repository.add_offer(offer)
