SELECT COUNT(*) AS row_count
FROM public.asset_resource_backup arr
JOIN public.assets_deduplicated a ON a.id = arr.asset_id
JOIN public.resources r ON r.id = arr.resource_id