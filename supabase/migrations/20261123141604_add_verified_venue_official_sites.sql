UPDATE public.places
SET website_url = CASE slug
    WHEN 'neurobox' THEN 'https://neurobox.by/'
    WHEN 'квест-пила' THEN 'https://pandorabox.by/'
    WHEN 'квест-проклятие-эмили' THEN 'https://pandorabox.by/'
    WHEN 'vasilki-minsk' THEN 'https://vasilki.by/'
    ELSE website_url
END,
updated_at = now()
WHERE slug IN ('neurobox', 'квест-пила', 'квест-проклятие-эмили', 'vasilki-minsk')
  AND is_active;
