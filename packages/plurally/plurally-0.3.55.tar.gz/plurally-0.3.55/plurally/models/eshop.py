from plurally.models.source.constant import Text


class EtsyOrder(Text):
    ICON = "etsy"


class ShopifyOrder(Text):
    ICON = "shopify"


__all__ = ["EtsyOrder", "ShopifyOrder"]
