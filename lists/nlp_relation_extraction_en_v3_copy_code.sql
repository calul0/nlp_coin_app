create table nlp_relation_extraction_en_v3
(
    design_id     bigint null,
    subject       bigint null,
    subject_str   text   null,
    predicate     bigint null,
    predicate_str text   null,
    object        bigint null,
    object_str    text   null
);

INSERT INTO nlp_relation_extraction_en_v3
SELECT * FROM nlp_relation_extraction_en_v2;

# our data changes (insert and update statements)
UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.predicate_str = 'standing_on'
WHERE t.design_id = 213
  AND t.subject = 724
  AND t.subject_str LIKE 'Bull' ESCAPE '#' AND t.predicate = 830 AND t.predicate_str LIKE 'standing' ESCAPE
                                                                     '#' AND t.object = 738 AND
                                                                     t.object_str LIKE 'dolphin' ESCAPE '#';

INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (213, 724, 'Bull', 1001, 'raising', 1002, 'forehoof');

# after analyzing empty prediction for 269
UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.subject     = 264,
    t.subject_str = 'nymph'
WHERE t.design_id = 269
  AND t.subject = 68
  AND t.subject_str LIKE 'Charites' ESCAPE '#' AND t.predicate = 826 AND t.predicate_str LIKE 'holding' ESCAPE
                                                                         '#' AND t.object = 508 AND
                                                                         t.object_str LIKE 'fillet' ESCAPE '#';

INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (269, 68, 'Charites', 826, 'holding', 690, 'shoulders');

# changes 466
INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (466, 61, 'Caracalla', 827, 'seated_on', 752, 'horseback');

# changes 475
UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.predicate_str = 'wearing'
WHERE t.design_id = 475
  AND t.subject = 61
  AND t.subject_str LIKE 'Caracalla' ESCAPE '#' AND t.predicate = 848 AND t.predicate_str LIKE 'wearing' ESCAPE
                                                                          '#' AND t.object = 569 AND
                                                                          t.object_str LIKE 'paludamentum' ESCAPE '#';

INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (475, 61, 'Caracalla', 848, 'wearing', 447, 'boots');

INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (475, 61, 'Caracalla', 827, 'seated_on', 752, 'horseback');


# changes 476
UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.predicate_str = 'wearing'
WHERE t.design_id = 476
  AND t.subject = 151
  AND t.subject_str LIKE 'Gordian' ESCAPE '#' AND t.predicate = 848 AND t.predicate_str LIKE 'wearing' ESCAPE
                                                                        '#' AND t.object = 569 AND
                                                                        t.object_str LIKE 'paludamentum' ESCAPE '#';

INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (476, 151, 'Gordian', 827, 'seated_on', 752, 'horseback');

#changes 666
UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.predicate_str = 'strangling'
WHERE t.design_id = 666
  AND t.subject = 165
  AND t.subject_str LIKE 'Heracles' ESCAPE '#' AND t.predicate = 841 AND t.predicate_str LIKE 'grasping' ESCAPE
                                                                         '#' AND t.object = 759 AND
                                                                         t.object_str LIKE 'Nemean lion' ESCAPE '#';
# changes 668
UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.predicate_str = 'grasping'
WHERE t.design_id = 668
  AND t.subject = 165
  AND t.subject_str LIKE 'Heracles' ESCAPE '#' AND t.predicate = 841 AND t.predicate_str LIKE 'grasping' ESCAPE
                                                                         '#' AND t.object = 759 AND
                                                                         t.object_str LIKE 'Nemean lion' ESCAPE '#';

# changes 908

INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (908, 259, 'Nike', 826, 'holding', 521, 'head');

# changes 944
UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.object_str = 'gorgoneion'
WHERE t.design_id = 944
  AND t.subject = 284
  AND t.subject_str LIKE 'Perseus' ESCAPE '#' AND t.predicate = 826 AND t.predicate_str LIKE 'holding' ESCAPE
                                                                        '#' AND t.object = 518 AND
                                                                        t.object_str LIKE 'gorgon' ESCAPE '#';

INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (944, 284, 'Persus', 839, 'releasing', 18, 'Andromeda');

#changes 1201

INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (1201, 740, 'eagle', 830, 'standing_on', 676, 'hand');

# changes in 1431
INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (1431, 724, 'Bull', 1001, 'raising', 1002, 'forehoof');

UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.predicate_str = 'standing_on'
WHERE t.design_id = 1431
  AND t.subject = 724
  AND t.subject_str LIKE 'Bull' ESCAPE '#' AND t.predicate = 830 AND t.predicate_str LIKE 'standing' ESCAPE
                                                                     '#' AND t.object = 738 AND
                                                                     t.object_str LIKE 'dolphin' ESCAPE '#';

# changes in 1432
INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (1432, 724, 'Bull', 1001, 'raising', 1002, 'forehoof');

UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.predicate_str = 'standing_on'
WHERE t.design_id = 1432
  AND t.subject = 724
  AND t.subject_str LIKE 'Bull' ESCAPE '#' AND t.predicate = 830 AND t.predicate_str LIKE 'standing' ESCAPE
                                                                     '#' AND t.object = 738 AND
                                                                     t.object_str LIKE 'dolphin' ESCAPE '#';
# changes in 1458
UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.predicate_str = 'standing_on'
WHERE t.design_id = 1458
  AND t.subject = 724
  AND t.subject_str LIKE 'Bull' ESCAPE '#' AND t.predicate = 830 AND t.predicate_str LIKE 'standing' ESCAPE
                                                                     '#' AND t.object = 738 AND
                                                                     t.object_str LIKE 'dolphin' ESCAPE '#';

INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (1458, 724, 'Bull', 1001, 'raising', 1002, 'forehoof');

# changes in 1460
UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.predicate_str = 'standing_on'
WHERE t.design_id = 1460
  AND t.subject = 724
  AND t.subject_str LIKE 'bull' ESCAPE '#' AND t.predicate = 830 AND t.predicate_str LIKE 'standing' ESCAPE
                                                                     '#' AND t.object = 738 AND
                                                                     t.object_str LIKE 'dolphin' ESCAPE '#';

INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (1460, 724, 'Bull', 1001, 'raising', 1002, 'forehoof');

# changes 1684
INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (1684, 304, 'Poseidon', 826, 'holding', 653, 'trident');

# changes in 1819
INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (1819, 42, 'athlete', 840, 'crowning', 42, 'athlete');

# changes in 2206
INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (2206, 754, 'Hydra', 831, 'coiling', 165, 'Heracles');

# changes in 2461
INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (2461, 740, 'Eagle', 826, 'standing_on', 645, 'thunderbolt');

# changes in 5525
INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (5525, 42, 'athlete', 840, 'crowning', 42, 'athlete');

# change in 6789
UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.object_str = 'grape'
WHERE t.design_id = 6789
  AND t.subject = 362
  AND t.subject_str LIKE 'Telesphorus' ESCAPE '#' AND t.predicate = 826 AND t.predicate_str LIKE 'holding' ESCAPE
                                                                            '#' AND t.object = 804 AND
                                                                            t.object_str LIKE 'grapes' ESCAPE '#';

INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (6789, 362, 'Telesphorus', 848, 'wearing', 684, 'mantle');

# change in 6789
UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.object_str = 'grape'
WHERE t.design_id = 6789
  AND t.subject = 362
  AND t.subject_str LIKE 'Telesphorus' ESCAPE '#' AND t.predicate = 826 AND t.predicate_str LIKE 'holding' ESCAPE
                                                                            '#' AND t.object = 804 AND
                                                                            t.object_str LIKE 'grapes' ESCAPE '#';

INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (6789, 362, 'Telesphorus', 848, 'wearing', 684, 'mantle');

# changes in 6912
INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (6912, 740, 'Eagle', 830, 'standing_on', 437, 'base');

# changes 24803
UPDATE nlp_challenge.nlp_relation_extraction_en_v3 t
SET t.subject_str = 'river-god'
WHERE t.design_id = 24803
  AND t.subject = 324
  AND t.subject_str LIKE 'river god' ESCAPE '#' AND t.predicate = 828 AND t.predicate_str LIKE 'resting#_on' ESCAPE
                                                                          '#' AND t.object = 536 AND
                                                                          t.object_str LIKE 'knee' ESCAPE '#';

INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (24803, 324, 'river-god', 826, 'holding', 816, 'reed');

# changes 24815
INSERT INTO nlp_challenge.nlp_relation_extraction_en_v3 (design_id, subject, subject_str, predicate, predicate_str,
                                                         object, object_str)
VALUES (24815, 40, 'Asclepius', 828, 'resting_on', 561, 'object');

