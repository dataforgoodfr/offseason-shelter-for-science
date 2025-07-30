-- Replace data of the assets table with the deduplicated ones
TRUNCATE public.assets;

WITH full_assets_deduplicated AS (
	SELECT ad.*, a.resource_id
	FROM public.assets_deduplicated ad
	LEFT JOIN public.assets_backup a ON a.id = ad.id
	WHERE a.id IS NOT NULL
)
INSERT INTO public.assets (id, url, kind_id, resource_id, created_at, updated_at, size, mtime)
SELECT id, url, kind_id, resource_id, created_at, updated_at, size, mtime FROM full_assets_deduplicated;
