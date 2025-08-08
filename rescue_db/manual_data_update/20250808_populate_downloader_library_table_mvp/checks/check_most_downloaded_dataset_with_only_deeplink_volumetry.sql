SELECT COUNT(*) AS row_count,
	COUNT(DISTINCT d.id) AS distinct_dataset_count
FROM public.datasets d
JOIN public.dataset_ranks dr ON dr.dataset_id = d.id
WHERE d.access_direct_dl_count = d.access_total_count 
AND dr.ranking_id = 8