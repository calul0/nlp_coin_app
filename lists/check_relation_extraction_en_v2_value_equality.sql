#gibt die Anzahl aller relation extractions aus
select count(*) from nlp_relation_extraction_en_v3;

# gibt die Anzahl aller Einträge, die sowohl in Extraction, als auch in entity vorhanden sind (name oder alternativ name)
select distinct count(*)
from nlp_relation_extraction_en_v2 re, nlp_list_entities subj, nlp_list_entities praed, nlp_list_entities obj
where (re.subject = subj.id and
      ((re.subject_str = subj.name_en) or(subj.alternativenames_en  like concat('%', re.subject_str , '%'))))
and (re.predicate = praed.id and
      ((re.predicate_str = praed.name_en) or(praed.alternativenames_en  like concat('%', re.predicate_str , '%'))))
and (re.object = obj.id and
      ((re.object_str = obj.name_en) or(obj.alternativenames_en  like concat('%', re.object_str , '%'))))

# erzeugt ein View aller richtig orientierte Einträge in Extraction version 2
# Stand: 19.06. sind 1950/2390 Einträge
create View nlp_right_table as select re.*
from nlp_relation_extraction_en_v2 re, nlp_list_entities subj, nlp_list_entities praed, nlp_list_entities obj
where (re.subject = subj.id and re.subject_str = subj.name_en)
and (re.predicate = praed.id and re.predicate_str = praed.name_en)
and (re.object = obj.id and re.object_str = obj.name_en)

# gibt die Anzahl für alle richtig orientierten Einträge
select count(*)
from nlp_relation_extraction_en_v3 re, nlp_list_entities_v3 subj, nlp_list_entities_v3 praed, nlp_list_entities_v3 obj
where (re.subject = subj.id and re.subject_str = subj.name_en)
and (re.predicate = praed.id and re.predicate_str = praed.name_en)
and (re.object = obj.id and re.object_str = obj.name_en)

# überschreibt alle alternativ namen mit dem orginalen englischen namen um in relation extraction
UPDATE nlp_relation_extraction_en_v3 re
JOIN nlp_list_entities_v3 subj ON re.subject = subj.id
JOIN nlp_list_entities_v3 praed ON re.predicate = praed.id
JOIN nlp_list_entities_v3 obj ON re.object = obj.id
SET re.subject_str = subj.name_en,
    re.predicate_str = praed.name_en,
    re.object_str = obj.name_en;
