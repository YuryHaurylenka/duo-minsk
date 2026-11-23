UPDATE public.places
SET website_url = CASE slug
    WHEN 'go-greek-minsk' THEN 'https://gogreek.by/'
    WHEN 'gambrinus-minsk' THEN 'https://www.gambrinus.by/'
    WHEN 'golf-park' THEN 'https://golfpark.by/'
    ELSE website_url
END,
updated_at = now()
WHERE slug IN ('go-greek-minsk', 'gambrinus-minsk', 'golf-park')
  AND is_active;
