-- Creation of the asset_resource_backup table
CREATE TABLE IF NOT EXISTS public.asset_resource_backup (
	id BIGSERIAL PRIMARY KEY NOT NULL,
	asset_id BIGINT,
	resource_id BIGINT,
	created_at TIMESTAMP,
	updated_at TIMESTAMP
);

-- Prepare the data to fit new tables
SET TIMEZONE='Europe/Paris';

-- Here we want to keep the id of the asset that will be kept
-- so the data between `assets` and `asset_resource` are 
-- consistent and can be joined without issues.
-- As a reminder, we keep the asset that was created the latest 
-- among duplicates.
WITH ranked_assets AS (
	SELECT 
		id,
		url,
		kind_id,
		resource_id,
		created_at,
		updated_at,
		size,
		mtime,
		RANK() OVER (PARTITION BY url ORDER BY created_at DESC) AS url_rank
	FROM public.assets
),
final_ranked_assets AS (
	SELECT *, FIRST_VALUE(id) OVER (PARTITION BY url ORDER BY url_rank) AS new_id
	FROM ranked_assets
),
asset_resource AS (
	SELECT 
		new_id AS asset_id, 
		resource_id,
		NOW() AS created_at,
		NOW() AS updated_at
	FROM final_ranked_assets
)

-- Populate the asset_resource_backup table
INSERT INTO public.asset_resource_backup (asset_id, resource_id, created_at, updated_at)
SELECT asset_id, resource_id, created_at, updated_at FROM asset_resource;
