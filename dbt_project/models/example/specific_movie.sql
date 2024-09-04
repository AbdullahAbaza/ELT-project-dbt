{% set film_title = 'Inception' %}

SELECT * 
FROM {{ ref('films') }}
WHERE title = '{{ film_title}}'