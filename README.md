# E-Waste Collection & Pricing API

Production-ready REST API that powers authenticated collection, pricing, supplier management, transactions, and analytics for e-waste programs. Built for the ALX capstone requirements with Django 4.2, Django REST Framework, PostgreSQL, JWT auth, Swagger docs, CI, and Render deployment readiness.

## Highlights
- JWT authentication with role-based authorization (collectors vs admins)
- Automatic pricing engine using $estimated_value = $base_price_per_kg × weight_kg × multiplier$
- CRUD endpoints for categories, suppliers, items, and transactions
- Transactions now link directly to item categories and capture sale-specific `weight_kg`
- E-waste analytics: today totals, monthly rollups, supplier ranking
- Postman collection, automated tests, GitHub Actions CI, Render deployment files

## Architecture Overview
- **apps/**: `accounts`, `catalog`, `suppliers`, `items`, `transactions`, `analytics`
- **Core models**: custom `accounts.User`, `catalog.ItemCategory`, `suppliers.Supplier`, `items.EWasteItem`, `transactions.Transaction`
- **FK behaviors**: PROTECT (`EWasteItem.category`, `Transaction.category`), SET NULL (`source_supplier`, `created_by`)
- **Indexes**: `EWasteItem(category,date_collected,created_by,source_supplier)` and `Transaction(category,date_sold)`
- **Docs**: drf-spectacular schema at `/schema/`, interactive Swagger UI at `/docs/`

## Tech Stack
- Python 3.11, Django 4.2, Django REST Framework
- PostgreSQL (Render) with SQLite fallback for local dev
- Auth: djangorestframework-simplejwt
- Docs: drf-spectacular
- Tooling: django-cors-headers, dj-database-url, python-dotenv, gunicorn

## Getting Started
1. **Clone & install**
   ```bash
   git clone https://github.com/<your-user>/E-Waste-Api.git
   cd E-Waste-Api
   python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Configure environment**
   ```bash
   cp .env.example .env
   # update SECRET_KEY, DATABASE_URL (optional), token lifetimes
   ```
3. **Run migrations & seed categories**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py seed_categories
   ```
4. **Start the API**
   ```bash
   python manage.py runserver
   ```
5. **Explore docs** at http://127.0.0.1:8000/docs/

## Environment Variables
| Name | Description | Default |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Django secret key | `insecure-secret-key` |
| `DEBUG` | Toggle debug mode | `false` |
| `ALLOWED_HOSTS` | Comma list of allowed hosts | blank |
| `DATABASE_URL` | Postgres URL (Render injects) | SQLite fallback |
| `DATABASE_SSL_REQUIRE` | Force SSL for Render | `false` |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | Simple JWT access lifetime | `15` |
| `REFRESH_TOKEN_LIFETIME_DAYS` | Simple JWT refresh lifetime | `7` |

## Database Schema (DBML)
```dbml
Table users {
  id bigserial [pk]
  username varchar(150) [unique, not null]
  email varchar(254)
  password_hash varchar(255) [not null]
  role varchar(20) [not null]
  created_at timestamp
}
Table item_categories {
  id bigserial [pk]
  name varchar(100) [unique, not null]
  base_price_per_kg decimal(10,2)
}
Table suppliers {
  id bigserial [pk]
  supplier_name varchar(200) [not null]
  contact varchar(200)
  location varchar(200)
}
Table ewaste_items {
  id bigserial [pk]
  category_id bigint [ref: > item_categories.id]
  weight_kg decimal(10,3) [not null]
  condition varchar(20) [not null]
  source_supplier_id bigint [ref: > suppliers.id]
  date_collected date [not null]
  estimated_value decimal(12,2) [not null]
  created_by bigint [ref: > users.id]
  created_at timestamp
}
Table transactions {
  id bigserial [pk]
  category_id bigint [ref: > item_categories.id]
  weight_kg decimal(10,3) [not null]
  sale_price decimal(12,2) [not null]
  buyer_name varchar(200) [not null]
  date_sold date
  status varchar(20) [not null]
}
```
Use the snippet above to generate an ERD in tools such as dbdiagram.io.

## Roles & Permissions
- **Admin**: manage categories, view all items/transactions, access analytics
- **Collector**: manage only their own items & transactions, view categories/suppliers, analytics for owned data (aggregates respect permissions)
- Default permission class is `IsAuthenticated`; registration and JWT login endpoints are public

## API Summary
| Resource | Endpoint | Notes |
| --- | --- | --- |
| Auth | `POST /auth/register` | Create collector account |
| | `POST /auth/login` | Obtain JWT access/refresh |
| | `POST /auth/refresh` | Refresh access token |
| Categories | `/categories/` | Admin-only writes |
| Suppliers | `/suppliers/` | Collectors + admins |
| Items | `/items/` | Auto price calculation |
| | `/items/{id}/estimate_price` | Recompute estimate |
| Transactions | `/transactions/` | Provide `category` + `weight_kg` per sale |
| Analytics | `/analytics/today` | Daily totals |
| | `/analytics/monthly` | Month aggregates |
| | `/analytics/supplier-ranking` | Ranked suppliers |

## Transactions Payload
- **Request fields**: `category` (1=Motherboards, 2=RAM, 3=Phone Boards), `weight_kg`, `sale_price`, `buyer_name`, optional `date_sold`, and `status` (`stocked`/`sold`).
- **Response fields**: mirrors the request plus `ewaste_item_detail` formatted as `#<category_id> | <category_name> (<weight_kg> kgs)`, `category_name`, `category_base_price_per_kg`, and timestamps.
- **Why**: transactions are now decoupled from individual `EWasteItem` rows, so every sale records its own weight even if no physical inventory item exists.

## Price Estimation
Condition multipliers: `poor=0.8`, `fair=0.9`, `good=1.0`. Values are recomputed automatically when weight, condition, or category changes and exposed via `/items/{id}/estimate_price`.

## Analytics Endpoints
- **Today**: totals for weight, estimated value, and count for current date
- **Monthly**: month-by-month aggregations of totals and counts
- **Supplier ranking**: total estimated value + item count per supplier, sorted descending

## Seeding Categories
Run `python manage.py seed_categories` to insert the baseline catalog:
- Motherboards — 5500 KES/kg
- RAM — 7500 KES/kg
- Phone Boards — 7500 KES/kg

## Testing & CI
- Execute `python manage.py test` for all unit + API tests
- GitHub Actions workflow `.github/workflows/ci.yml` runs Django checks, migrations (dry run), migrations, and tests on push/PR

## Deployment on Render
1. Commit and push to GitHub
2. Create new Render Web Service pointing to the repo
3. Render automatically reads `render.yaml`, provisions `ewaste-db`, injects `DATABASE_URL`, and runs the build/start commands
4. Configure `ALLOWED_HOSTS` env var to match your Render domain
5. Open `<render-domain>/docs` to confirm Swagger UI once migrations finish

## Postman Collection
Import `postman_collection.json` into Postman. Set globals:
- `base_url`: e.g. `https://ewaste-api.onrender.com`
- `access_token`: set via login response
Collection covers auth, categories, suppliers, items, transactions, analytics, and the custom estimate endpoint.

## Example cURL Checks
```bash
# Register
curl -X POST "$BASE_URL/auth/register" -H "Content-Type: application/json" \
  -d '{"username": "demo", "email": "demo@example.com", "password": "DemoPass123"}'

# Login
ACCESS=$(curl -s -X POST "$BASE_URL/auth/login" -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "DemoPass123"}' | jq -r '.access')

# List categories
curl -H "Authorization: Bearer $ACCESS" "$BASE_URL/categories/"

# Create item (collector)
curl -X POST "$BASE_URL/items/" -H "Authorization: Bearer $ACCESS" -H "Content-Type: application/json" \
  -d '{"category": 1, "weight_kg": "3.5", "condition": "good", "date_collected": "2025-01-05"}'

# Record transaction (category + weight)
curl -X POST "$BASE_URL/transactions/" -H "Authorization: Bearer $ACCESS" -H "Content-Type: application/json" \
  -d '{"category": 3, "weight_kg": "65.00", "sale_price": "70000", "buyer_name": "Isiolo County Gov", "status": "sold", "date_sold": "2025-12-06"}'

# View analytics
curl -H "Authorization: Bearer $ACCESS" "$BASE_URL/analytics/today"
```

## Tooling References
- Postman collection: `postman_collection.json`
- OpenAPI schema: `/schema/`
- Swagger UI: `/docs`
