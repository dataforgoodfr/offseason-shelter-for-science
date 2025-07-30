-- Creation of a backup of the assets table
CREATE TABLE IF NOT EXISTS public.assets_backup AS TABLE public.assets;

-- Preparation of the assets_deduplicated table
CREATE TABLE IF NOT EXISTS public.assets_deduplicated AS TABLE public.assets;

ALTER TABLE public.assets_deduplicated 
DROP COLUMN IF EXISTS resource_id;

TRUNCATE public.assets_deduplicated;

-- Prepare the data to fit the new table schema

-- Here we want to keep the asset that was created the latest 
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
assets_deduplicated AS (
	SELECT 
		id,
		url,
		kind_id,
		created_at,
		updated_at,
		size,
		mtime
	FROM ranked_assets
	WHERE url_rank = 1
)

-- Migrate data of the assets_deduplicated table
INSERT INTO public.assets_deduplicated (id, url, kind_id, created_at, updated_at, size, mtime)
SELECT id, url, kind_id, created_at, updated_at, size, mtime FROM assets_deduplicated;
