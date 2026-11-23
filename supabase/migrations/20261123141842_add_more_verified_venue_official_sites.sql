UPDATE public.places
SET website_url = CASE slug
    WHEN 'минскии-планетарии' THEN 'https://planetarium.by/'
    WHEN 'kartlend' THEN 'https://kartland.by/'
    WHEN 'f1-картинг-веснянка' THEN 'https://f1karting.by/'
    WHEN 'минскии-зоопарк' THEN 'https://minskzoo.by/'
    WHEN 'музеи-истории-минска' THEN 'https://minskmuseum.by/'
    ELSE website_url
END,
updated_at = now()
WHERE slug IN ('минскии-планетарии', 'kartlend', 'f1-картинг-веснянка', 'минскии-зоопарк', 'музеи-истории-минска')
  AND is_active;
