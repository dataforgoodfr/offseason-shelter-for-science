SELECT 
	-- The 2 values below must match
	COUNT(*) AS row_count,
	COUNT(DISTINCT resource_id) AS distinct_resource_count,
	-- The value below must match with the ones of distinct_dataset_count 
	-- in "check_most_downloaded_dataset_with_only_deeplink_volumetry.sql"
	COUNT(DISTINCT dataset_id) AS distinct_dataset_count
FROM public.mvp_downloader_library