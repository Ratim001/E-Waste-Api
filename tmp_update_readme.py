from pathlib import Path

path = Path("c:/Users/USER/OneDrive/E-Waste-Api/README.md")
text = path.read_text()
marker = "# View analytics"
if marker not in text:
    raise SystemExit("Marker not found")
before, _ = text.split(marker, 1)
new_tail = marker + "\n" + "\n".join([
    "# Record transaction (category + weight)",
    "curl -X POST \"$BASE_URL/transactions/\" -H \"Authorization: Bearer $ACCESS\" -H \"Content-Type: application/json\" \\",
    "  -d '{\"category\": 3, \"weight_kg\": \"65.00\", \"sale_price\": \"70000\", \"buyer_name\": \"Isiolo County Gov\", \"status\": \"sold\", \"date_sold\": \"2025-12-06\"}'",
    "",
    "# View analytics",
    "curl -H \"Authorization: Bearer $ACCESS\" \"$BASE_URL/analytics/today\"",
    "```",
    "",
    "## Tooling References",
    "- Postman collection: `postman_collection.json`",
    "- OpenAPI schema: `/schema/`",
    "- Swagger UI: `/docs`",
])
path.write_text(before + new_tail)
