CREATE TABLE `nlp_list_entities_v3` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `class` text,
  `name_en` text,
  `name_ger` text,
  `alternativenames_en` text,
  `alternativenames_ger` text,
  `description` text,
  `link` text,
  `Cat_I` text,
  `Cat_II` text,
  `Cat_III` text,
  `Cat_IV` text,
  `Cat_V` text,
  `typos_en` text,
  `typos_ger` text,
  `related` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO nlp_list_entities_v3
SELECT * FROM nlp_list_entities;

INSERT INTO nlp_challenge.nlp_list_entities_v3 (class, name_en, name_ger, alternativenames_en, alternativenames_ger,
                                                description, link, Cat_I, Cat_II, Cat_III, Cat_IV, Cat_V, typos_en,
                                                typos_ger, related)
VALUES ('VERB', 'raising', 'None', 'None', '', 'None', 'https://www.wikidata.org/wiki/Q74026067', 'None', 'None',
        'None', 'None', 'None', 'None', 'None', 'None'),
    ('OBJECT', 'forehoof', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None',
        'None', 'None');

# changes 464
UPDATE nlp_challenge.nlp_list_entities_v3 t
SET t.alternativenames_en = 'Philippus I, Philipp I., Philip the Arab, philip_the_arab, Philip I, Philip the Elder'
WHERE t.id = 290;

# changes 475
UPDATE nlp_challenge.nlp_list_entities_v3 t
SET t.alternativenames_en = 'wearing_fluttering'
WHERE t.id = 848;

# changes 666

UPDATE nlp_challenge.nlp_list_entities_v3 t
SET t.alternativenames_en = 'clasping, pushing, strangling'
WHERE t.id = 841;

# changes 908
UPDATE nlp_challenge.nlp_list_entities_v3 t
SET t.alternativenames_en = 'ploughing,  removing, covering,  containing,  brandishing,  carrying,  forming,  raising,  cradling,  touching,  drawing, supporting'
WHERE t.id = 826;

# changes 24747

UPDATE nlp_challenge.nlp_list_entities_v3 t
SET t.alternativenames_en = 'ploughing,  removing, covering,  containing,  brandishing,  carrying,  forming,  raising,  cradling,  touching,  drawing, supporting, hanging_on'
WHERE t.id = 826;


