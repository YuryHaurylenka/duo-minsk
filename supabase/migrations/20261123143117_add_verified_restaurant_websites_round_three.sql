UPDATE public.places
SET website_url = CASE slug
    WHEN 'malevich-minsk' THEN 'https://malevichrest.by/'
    WHEN 'monemane-minsk' THEN 'https://monemane.by/'
    WHEN 'owino-minsk' THEN 'https://owino.by/'
    WHEN 'zavtraki' THEN 'https://zavtraki.by/'
    WHEN 'kamyanitsa-minsk' THEN 'https://kamyanitsa.by/'
    ELSE website_url
END,
updated_at = now()
WHERE slug IN ('malevich-minsk', 'monemane-minsk', 'owino-minsk', 'zavtraki', 'kamyanitsa-minsk')
  AND is_active;
