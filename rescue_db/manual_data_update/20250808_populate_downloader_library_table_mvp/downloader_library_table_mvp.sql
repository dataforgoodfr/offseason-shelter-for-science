-- Creation of the downloader library table especially for MVP
CREATE TABLE IF NOT EXISTS public.mvp_downloader_library (
	id BIGSERIAL PRIMARY KEY NOT NULL,
	dataset_id BIGINT,
	resource_id BIGINT,
	dataset_rank INT,
	deeplink TEXT,
	deeplink_file_size BIGINT,
	magnet_link TEXT,
	defective_link_flag BOOLEAN,
	created_at TIMESTAMP DEFAULT NOW(),
	updated_at TIMESTAMP DEFAULT NOW()
);

-- Preparation of the data: we take all the resources
-- of the most downloaded datasets (ranking_id = 8) that 
-- only have deeplinks. 
WITH most_downloaded_dataset_resources AS (
	SELECT 
		d.id 					AS dataset_id,
		r.id 					AS resource_id,
		dr.rank 				AS dataset_rank,
		r.dg_url 				AS deeplink,
		CAST(NULL AS INT) 		AS deeplink_file_size,
		CAST(NULL AS VARCHAR) 	AS magnet_link,
		FALSE 					AS defective_link_flag
	FROM public.datasets d
	JOIN public.dataset_ranks dr ON dr.dataset_id = d.id
	JOIN public.resources r ON r.dataset_id = d.id
	WHERE d.access_direct_dl_count = d.access_total_count 
	AND dr.ranking_id = 8 
	ORDER BY dr.rank
)

-- Populate the newly created table
INSERT INTO public.mvp_downloader_library (dataset_id, resource_id, dataset_rank, deeplink, deeplink_file_size, magnet_link, defective_link_flag)
SELECT dataset_id, resource_id, dataset_rank, deeplink, deeplink_file_size, magnet_link, defective_link_flag FROM most_downloaded_dataset_resources;
