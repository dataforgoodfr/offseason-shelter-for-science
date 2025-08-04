SELECT r.dg_url,a.url FROM public.asset_resource ar
INNER JOIN public.resources r ON ar.resource_id=r.id
INNER JOIN public.assets a ON ar.asset_id=a.id
WHERE a.url NOT LIKE r.dg_url || '%';