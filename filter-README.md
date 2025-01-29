# API Filtering and Sorting Documentation

This document outlines all available filtering and sorting options for the Products and Product Entries endpoints.

## Products Endpoint (`/products`)

### Basic Pagination
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10, max: 100)

Example:
```
/products?page=1&per_page=20
```

### Search
- `search`: Search query for filtering products by name

Example:
```
/products?search=milk
```

### Category Filter
- `category_id`: Filter products by category ID

Example:
```
/products?category_id=1
```

### Price Entry Filters
- `has_entries`: Filter products that have (true) or don't have (false) price entries
- `min_price`: Filter products by minimum current price
- `max_price`: Filter products by maximum current price

Examples:
```
/products?has_entries=true
/products?min_price=1.99&max_price=5.99
```

### Barcode Filter
- `barcode`: Filter by exact barcode match

Example:
```
/products?barcode=12345670
```

### Sorting Options
- `order_by`: Field to order by
  - `name` (default)
  - `barcode`
  - `created_at`
- `order_direction`: Sort direction
  - `asc` (default)
  - `desc`

Examples:
```
/products?order_by=name&order_direction=asc
/products?order_by=created_at&order_direction=desc
```

### Combining Filters
You can combine any of the above filters:

Example:
```
/products?page=1&per_page=20&search=milk&category_id=1&min_price=1.99&max_price=5.99&has_entries=true&order_by=name&order_direction=asc
```

## Product Entries Endpoint (`/product-entries`)

### Basic Pagination
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10, max: 100)

Example:
```
/product-entries?page=1&per_page=20
```

### Search
- `search`: Search query for filtering entries by product name, store brand name, or store location address

Example:
```
/product-entries?search=milk
```

### Product and Store Filters
- `product_id`: Filter entries by product ID
- `store_brand_id`: Filter entries by store brand ID
- `store_location_id`: Filter entries by store location ID

Examples:
```
/product-entries?product_id=1
/product-entries?store_brand_id=1
/product-entries?store_location_id=1
```

### Price Range Filters
- `min_price`: Filter entries by minimum price
- `max_price`: Filter entries by maximum price

Example:
```
/product-entries?min_price=1.99&max_price=5.99
```

### Date Range Filters
- `from_date`: Filter entries from this date
- `to_date`: Filter entries until this date

Example:
```
/product-entries?from_date=2024-01-01T00:00:00&to_date=2024-01-31T23:59:59
```

### Sorting Options
- `order_by`: Field to order by
  - `created_at` (default)
  - `price`
- `order_direction`: Sort direction
  - `desc` (default for created_at)
  - `asc`

Examples:
```
/product-entries?order_by=price&order_direction=asc
/product-entries?order_by=created_at&order_direction=desc
```

### Combining Filters
You can combine any of the above filters:

Example:
```
/product-entries?page=1&per_page=20&search=milk&product_id=1&store_brand_id=1&min_price=1.99&max_price=5.99&from_date=2024-01-01T00:00:00&order_by=price&order_direction=asc
```

## TypeScript Interfaces

### Products
```typescript
interface ProductFilters {
  page: number;
  per_page: number;
  search?: string;
  category_id?: number;
  has_entries?: boolean;
  min_price?: number;
  max_price?: number;
  barcode?: string;
  order_by?: 'name' | 'barcode' | 'created_at';
  order_direction?: 'asc' | 'desc';
}
```

### Product Entries
```typescript
interface ProductEntryFilters {
  page: number;
  per_page: number;
  search?: string;
  product_id?: number;
  store_brand_id?: number;
  store_location_id?: number;
  min_price?: number;
  max_price?: number;
  from_date?: string; // ISO date string
  to_date?: string; // ISO date string
  order_by?: 'created_at' | 'price';
  order_direction?: 'asc' | 'desc';
}
```

## Best Practices

1. **URL Parameters**
   - Always encode URL parameters properly
   - Use ISO format for dates (YYYY-MM-DDTHH:mm:ss)
   - Use decimal points for prices (not commas)

2. **Error Handling**
   - Handle 400 Bad Request for invalid filter values
   - Handle 404 Not Found for invalid IDs
   - Handle empty result sets appropriately in the UI

3. **Performance**
   - Use reasonable page sizes (10-50 items)
   - Consider implementing client-side caching
   - Use debouncing for search inputs

4. **UX Recommendations**
   - Show active filters to users
   - Provide clear reset/clear filters option
   - Save user's filter preferences locally
   - Use appropriate input types (date pickers, number inputs, etc.)
   - Show loading states during filter changes 