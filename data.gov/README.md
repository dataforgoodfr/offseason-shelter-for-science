# data.gov

## CKAN API

User guide : https://data.gov/user-guide/#data-gov-ckan-api
API link : https://catalog.data.gov/api/3/

Exemple :

```bash
curl -X POST "https://catalog.data.gov/api/3/action/package_search" \
     -H "Content-Type: application/json" \
     -d '{"fq": "organization:\"census-gov\""}' |json_pp
```

## NOCODB API

### Insert rows

```bash
curl --request POST \
	--url 'https://noco.services.dataforgood.fr/api/v2/tables/TABLE_ID/records' \
	--header 'xc-token: <TOKEN>' \
    --header 'Content-Type: application/json' \
    --data '[{"foo": "Foo bar", "bar": "2025-05-30", "unknown_field": "ERROR!"}, {"foo": "bar", "bar": "2025-05-31", "unknown_field": "?"}]'
```

### Documentation and tools

Guide : https://docs.ckan.org/en/latest/api/
Github : https://github.com/ckan/ckanapi

#### Fonctions

package_search : https://docs.ckan.org/en/latest/api/#ckan.logic.action.get.package_search