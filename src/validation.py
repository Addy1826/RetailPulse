# validation.py - Checks cleaned data before loading into MySQL

import pandas as pd


class ValidationError(Exception):
    pass


def check_no_nulls(df, columns, table):
    """Make sure these columns have no empty values."""
    for col in columns:
        n = df[col].isna().sum()
        if n > 0:
            raise ValidationError(f"[{table}] '{col}' has {n} null values")


def check_unique(df, columns, table):
    """Make sure there are no duplicate rows for these columns."""
    n = df.duplicated(subset=columns, keep=False).sum()
    if n > 0:
        raise ValidationError(f"[{table}] Found {n} duplicate rows on {columns}")


def check_positive(df, columns, table):
    """Make sure values are greater than zero."""
    for col in columns:
        bad = (df[col] <= 0).sum()
        if bad > 0:
            raise ValidationError(f"[{table}] '{col}' has {bad} non-positive values")


def check_values(df, col, valid_set, table):
    """Make sure column only contains expected values."""
    invalid = set(df[col].dropna().unique()) - valid_set
    if invalid:
        raise ValidationError(f"[{table}] '{col}' has invalid values: {invalid}")


def check_foreign_key(df, fk_col, parent_df, pk_col, table):
    """Make sure every foreign key value exists in the parent table."""
    orphans = set(df[fk_col].dropna().unique()) - set(parent_df[pk_col].unique())
    if orphans:
        raise ValidationError(f"[{table}] {len(orphans)} orphan values in '{fk_col}'")


# Individual table validators

def validate_customers(df):
    issues = []
    try:
        check_no_nulls(df, ["customer_id", "first_name", "last_name", "email", "join_date"], "customers")
        check_unique(df, ["email"], "customers")
        check_values(df, "segment", {"Regular", "Premium", "VIP"}, "customers")
    except ValidationError as e:
        issues.append(str(e))
    return issues


def validate_categories(df):
    issues = []
    try:
        check_no_nulls(df, ["category_id", "category_name"], "categories")
        check_unique(df, ["category_name"], "categories")
    except ValidationError as e:
        issues.append(str(e))
    return issues


def validate_products(df, categories):
    issues = []
    try:
        check_no_nulls(df, ["product_id", "product_name", "unit_price", "cost_price", "sku"], "products")
        check_unique(df, ["sku"], "products")
        check_positive(df, ["unit_price", "cost_price"], "products")
        check_foreign_key(df, "category_id", categories, "category_id", "products")
    except ValidationError as e:
        issues.append(str(e))
    return issues


def validate_stores(df):
    issues = []
    try:
        check_no_nulls(df, ["store_id", "store_name", "city", "state", "region"], "stores")
        check_unique(df, ["store_id"], "stores")
        check_values(df, "region", {"North", "South", "East", "West"}, "stores")
        check_values(df, "store_type", {"Flagship", "Mall", "Outlet", "Online"}, "stores")
    except ValidationError as e:
        issues.append(str(e))
    return issues


def validate_orders(df, customers, stores):
    issues = []
    try:
        check_no_nulls(df, ["order_id", "customer_id", "store_id", "order_date"], "orders")
        check_unique(df, ["order_id"], "orders")
        check_foreign_key(df, "customer_id", customers, "customer_id", "orders")
        check_foreign_key(df, "store_id", stores, "store_id", "orders")
        check_values(df, "status", {"Completed", "Returned", "Cancelled"}, "orders")
    except ValidationError as e:
        issues.append(str(e))
    return issues


def validate_order_items(df, orders, products):
    issues = []
    try:
        check_no_nulls(df, ["item_id", "order_id", "product_id", "quantity", "unit_price"], "order_items")
        check_positive(df, ["quantity"], "order_items")
        check_foreign_key(df, "order_id", orders, "order_id", "order_items")
        check_foreign_key(df, "product_id", products, "product_id", "order_items")
    except ValidationError as e:
        issues.append(str(e))
    return issues


def validate_inventory(df, stores, products):
    issues = []
    try:
        check_no_nulls(df, ["inventory_id", "store_id", "product_id", "qty_on_hand"], "inventory")
        check_unique(df, ["store_id", "product_id"], "inventory")
        check_foreign_key(df, "store_id", stores, "store_id", "inventory")
        check_foreign_key(df, "product_id", products, "product_id", "inventory")
    except ValidationError as e:
        issues.append(str(e))
    return issues


def run_all_validations(customers, categories, products, stores,
                        orders, order_items, inventory):
    """Run all validators and return a dict of {table: [issues]}."""
    return {
        "customers":   validate_customers(customers),
        "categories":  validate_categories(categories),
        "products":    validate_products(products, categories),
        "stores":      validate_stores(stores),
        "orders":      validate_orders(orders, customers, stores),
        "order_items": validate_order_items(order_items, orders, products),
        "inventory":   validate_inventory(inventory, stores, products),
    }
