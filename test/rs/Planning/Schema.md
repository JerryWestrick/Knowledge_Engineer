# Database Schema

## Tables and Columns

### menu_h1
| Column Name | Data Type |
|-------------|-----------|
| id          | integer   |
| name        | text      |

### menu_h2
| Column Name | Data Type |
|-------------|-----------|
| id          | integer   |
| menu_h1_id  | integer   |
| name        | text      |

### menu_items
| Column Name | Data Type         |
|-------------|-------------------|
| id          | integer           |
| menu_h2_id  | integer           |
| name        | text              |
| description | text              |
| price       | double precision  |
| quantity    | integer           |

### users
| Column Name | Data Type                   |
|-------------|-----------------------------|
| id          | integer                     |
| email       | text                        |
| password    | text                        |
| role        | text                        |
| last_login  | timestamp without time zone |

### tables
| Column Name    | Data Type |
|----------------|-----------|
| id             | integer   |
| name           | text      |
| default_seats  | integer   |
| order_id       | integer   |

### seats
| Column Name | Data Type |
|-------------|-----------|
| id          | integer   |
| table_id    | integer   |
| name        | text      |

### orders
| Column Name | Data Type               |
|-------------|-------------------------|
| id          | integer                 |
| open_time   | timestamp with time zone|
| state       | text                    |
| table_id    | integer                 |

### order_items
| Column Name  | Data Type |
|--------------|-----------|
| id           | integer   |
| order_id     | integer   |
| seat_id      | integer   |
| menu_item_id | integer   |
| quantity     | integer   |

### order_item_alterations
| Column Name   | Data Type |
|---------------|-----------|
| id            | integer   |
| order_item_id | integer   |
| alteration    | text      |

## Relationships

- `menu_h2` references `menu_h1` (`menu_h1_id` -> `id`)
- `menu_items` references `menu_h2` (`menu_h2_id` -> `id`)
- `seats` references `tables` (`table_id` -> `id`)
- `orders` references `tables` (`table_id` -> `id`)
- `order_items` references `orders` (`order_id` -> `id`)
- `order_items` references `seats` (`seat_id` -> `id`)
- `order_items` references `menu_items` (`menu_item_id` -> `id`)
- `order_item_alterations` references `order_items` (`order_item_id` -> `id`)
