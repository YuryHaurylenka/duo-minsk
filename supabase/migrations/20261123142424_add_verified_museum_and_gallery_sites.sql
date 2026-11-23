UPDATE public.places
SET website_url = CASE slug
    WHEN 'музеи-мастерская-заира-азгура' THEN 'https://azgur.by/'
    WHEN 'галерея-арт-беларусь' THEN 'https://artpalace.by/exhibitions/'
    WHEN 'национальныи-историческии-музеи' THEN 'https://histmuseum.by/'
    WHEN 'музеи-древнебелорусскои-культуры' THEN 'https://belcentre.by/ru_ru/%D0%BC%D1%83%D0%B7%D0%B5%D0%B9-%D0%B4%D1%80%D0%B5%D0%B2%D0%BD%D0%B5%D0%B1%D0%B5%D0%BB%D0%BE%D1%80%D1%83%D1%81%D1%81%D0%BA%D0%BE%D0%B9-%D0%BA%D1%83%D0%BB%D1%8C%D1%82%D1%83%D1%80%D1%8B/'
    ELSE website_url
END,
updated_at = now()
WHERE slug IN ('музеи-мастерская-заира-азгура', 'галерея-арт-беларусь', 'национальныи-историческии-музеи', 'музеи-древнебелорусскои-культуры')
  AND is_active;
