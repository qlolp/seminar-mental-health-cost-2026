# Проверка научных ссылок для доклада (19.10.2026)

## Как проверяли

- **По DOI:** через инструмент `reference-lookup` плагина Research Desk (база OpenAlex). Поиск по названию в этом инструменте не отвечал, запросы обрывались через 60 секунд.
- **Без DOI или при отказе инструмента:** через веб-поиск точного названия. В этом случае смотрели запись в репозитории, у издателя или в PubMed.
- **Ограничение:** проверены существование статьи, авторы, год и журнал. Соответствие каждого утверждения доклада тексту статьи не проверялось, потому что полные тексты не открывались (статус `unverified`).

## Итог по каждой ссылке

| Ссылка | Статус | Примечание |
|---|---|---|
| Kozma, Mansell, Beadle-Brown 2009, AJIDD 114(3):193–222 | verified* | DOI 10.1352/1944-7558-114.3.193. В OpenAlex первый автор записан как Ágnes Turnpenny (это та же Агнеш Козма, сменившая фамилию). Инструмент выдал `mismatch` только из-за фамилии. https://doi.org/10.1352/1944-7558-114.3.193 |
| May et al. 2019, BMJ Open | verified | DOI 10.1136/bmjopen-2018-025736. https://doi.org/10.1136/bmjopen-2018-025736 |
| McCarron et al. 2019, BMJ Open | verified | DOI 10.1136/bmjopen-2018-025735. https://doi.org/10.1136/bmjopen-2018-025735 |
| Baxter et al. 2019, J Epidemiol Community Health | verified | DOI 10.1136/jech-2018-210981. https://doi.org/10.1136/jech-2018-210981 |
| Hughes et al. 2012, The Lancet | verified | DOI 10.1016/S0140-6736(11)61851-5. https://doi.org/10.1016/s0140-6736(11)61851-5 |
| Strauss, Eyman, Grossman 1996, AJPH 86(10):1422 | verified | DOI 10.2105/AJPH.86.10.1422. По аннотации риск смерти выше примерно на 25 %. |
| Strauss, Kastner 1996, AJMR 101(1):26–40 | verified (по записи) | Риск смерти в сообществе выше на 72 %, по аннотации. https://einstein.elsevierpure.com/en/publications/comparative-mortality-of-people-with-mental-retardation-in-instit |
| Lerman, Apgar, Jordan 2003, Mental Retardation 41(4) | verified (по записи) | https://digitalcommons.njit.edu/fac_pubs/14238. Выводы взяты из аннотации. |
| Emerson et al. 2001, AJMR 106(5):401–415 | verified (по записи) | https://researchonline.lse.ac.uk/id/eprint/19197. Вывод «нет значимой разницы в скорректированных затратах» есть только в тезисах конференции 2000 года, в статье 2001 года он не проверен. Помечать как partial. |
| Hamelin, Sturmey 2011, IDD 49(3):166–171 | verified (по записи) | Вывод авторов: «promising treatment», а не доказанная практика. |
| Flynn et al. 2018, JARID 31(6):983–998 | verified (по записи) | DOI 10.1111/jar.12491. https://research.birmingham.ac.uk/en/publications/effectiveness-of-active-support-for-adults-with-intellectual-disa |
| Munthe-Kaas, Berg, Blaasvær 2018, Campbell Systematic Reviews 14(1) | verified (по записи) | DOI 10.4073/csr.2018.3; 43 исследования. https://pmc.ncbi.nlm.nih.gov/articles/PMC8427990 |
| Lakin, Larson, Kim 2011 | partial | Это не журнальная статья, а Policy Research Brief Университета Миннесоты (апрель 2011). Журнальная версия вышла в 2012 году: Research and Practice for Persons with Severe Disabilities 37(4), «Behavioral outcomes of moving from institutional to community living». https://ici.umn.edu/products/prb/212/default.html |
| «Bigby (2008), критический обзор Active Support, JIDD» | mismatch | Такого обзора за авторством Bigby не найдено. Обзор 2008 года написали Stancliffe, Jones, Mansell, Lowe: «Active support: A critical review and commentary», JIDD 33(3):196–214, doi:10.1080/13668250802315397. Атрибуцию исправить. |
| Mansell, Knapp, Beadle-Brown, Beecham 2007, DECLOC | verified ранее | Прочитан в этой сессии: резюме, том 1, Кентский университет. |

## Что исправить в первую очередь

1. Ссылку «Bigby 2008» заменить на Stancliffe, Jones, Mansell & Lowe (2008).
2. Lakin et al. 2011 описывать как аналитическую записку Университета Миннесоты, упомянув журнальную версию 2012 года.
3. Вывод Emerson et al. о затратах пометить знаком †: он опирается на тезисы конференции 2000 года.
