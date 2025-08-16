-- First fill unique assets
INSERT INTO public.asset_resource (asset_id,resource_id)
SELECT a.id,ab.resource_id FROM public.assets a
INNER JOIN public.assets_deduplicated ad ON ad.url=a.url
INNER JOIN public.assets_backup ab ON ab.id=ad.id;

-- Then add duplicates
INSERT INTO public.asset_resource (asset_id,resource_id)
SELECT a.id,ab.resource_id FROM public.assets a
INNER JOIN public.assets_deduplicated ad ON ad.url=a.url
INNER JOIN public.assets_backup ab ON ab.url=ad.url AND ab.id<>ad.id;