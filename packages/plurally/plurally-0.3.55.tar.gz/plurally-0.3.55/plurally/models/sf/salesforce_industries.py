import re

industrie_names = (
    "Agriculture",
    "Apparel",
    "Banking",
    "Biotechnology",
    "Chemicals",
    "Communications",
    "Construction",
    "Consulting",
    "Education",
    "Electronics",
    "Energy",
    "Engineering",
    "Entertainment",
    "Environmental",
    "Finance",
    "Food & Beverage",
    "Government",
    "Healthcare",
    "Hospitality",
    "Insurance",
    "Machinery",
    "Manufacturing",
    "Media",
    "Not For Profit",
    "Other",
    "Recreation",
    "Retail",
    "Shipping",
    "Technology",
    "Telecommunications",
    "Transportation",
    "Utilities",
)


def to_enum_value_case(name):
    if not name:
        return name
    name = re.sub(r"[^a-zA-Z0-9]", "_", name)  # replace all non-alphanumeric characters with underscores
    name = re.sub(r"__+", "_", name)  # replace multiple underscores with a single underscore
    return name.upper()  # convert to uppercase


INDUSTRIES = tuple(to_enum_value_case(industry) for industry in industrie_names)
