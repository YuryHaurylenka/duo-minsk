UPDATE public.places
SET website_url = CASE slug
    WHEN 'музеи-миниатюр-страна-мини' THEN 'https://belarusmini.by/'
    WHEN 'bergamo-minsk' THEN 'https://bergamo.by/'
    WHEN 'burgerlab' THEN 'https://burgerlab.by/'
    WHEN 'клуб-настольных-игр-people-meeple' THEN 'https://peoplemeeple.by/'
    WHEN 'скалодром-трапеция' THEN 'https://trapezia.by/'
    WHEN 'кухмистр' THEN 'https://www.kuhmistr.by/'
    WHEN 'il-patio-minsk' THEN 'https://www.ilpatio.by/'
    WHEN 'tokiny-minsk' THEN 'https://tokiny.by/'
    WHEN 'umami-minsk' THEN 'https://umami.by/'
    ELSE website_url
END,
updated_at = now()
WHERE slug IN ('музеи-миниатюр-страна-мини', 'bergamo-minsk', 'burgerlab', 'клуб-настольных-игр-people-meeple', 'скалодром-трапеция', 'кухмистр', 'il-patio-minsk', 'tokiny-minsk', 'umami-minsk')
  AND is_active;
