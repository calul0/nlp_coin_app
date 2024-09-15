import importlib
import pandas as pd
import cnt.analizer_package.analizer_extractor as extr
import cnt.analizer_package.relation_sentence as reSe

importlib.reload(extr)
importlib.reload(reSe)


class RelationExtractionAnalizer():
    """Was will ich zwischen den beiden Dataframes herausfinden ?
    # 1 - Gleichheit bei der Zuordnung (zb. Person, Verb, Object..)
    # 2 - Gleicheit in der Anzahl der annotierten Elemente eines design_ids?
    # 3 - Elemente, die in Pred-Model existieren, aber nicht in Test-Model
    # 4 - Elemente, die in Test-Model existieren, aber nicht in Pred-Model

    # Ziel eine Auflistung aller Datem, die nicht die Identität zwischen den beiden Modellen entspricht, um eine starke Aussage über die Datenanalyse aussagen zu können."""

    def __init__(self, true, pred, labels=["PERSON", "OBJECT", "ANIMAL", "PLANT"]):
        self.y_test = true
        self.y_pred = pred
        self.labels = labels
        self.analizer = extr.AnalizerExtractor()

    def getDict(self, elem):
        resultDict = dict()
        for rowIdx in elem.index:
            designId = elem.loc[rowIdx, "design_id"]
            list_of_anotated = elem.loc[rowIdx, "y"]
            resultDict[designId] = list_of_anotated
        return resultDict

    def annotated_Dict(self, datas):
        anotatedResultDict = dict()
        # TODO should make a dict with dict[word] = ["Person"]
        return ""

    def hasSameLabels(self, test_data, pred_data):
        testAnnoDict = self.annotated_Dict(test_data)
        predAnnoDict = self.annotated_Dict(pred_data)

        # TODO check if the annotation are the same
        return True

    def prepareRelation(self, re_y_dict):
        relationFrame = pd.DataFrame()
        for design_id in re_y_dict.keys():
            design_content = re_y_dict[design_id]
            constructedID = "{}#".format(int(design_id))
            if len(design_content) > 0:
                for i in range(len(design_content)):
                    designcontentLength = len(design_content[i])
                    for j in range(designcontentLength):
                        constructedID = constructedID + "{}#".format(str(design_content[i][j]))
                    dataFrameRow = pd.DataFrame([{
                        "design_id": design_id,
                        "constructedID": constructedID,
                        "y": design_content
                    }])
                    relationFrame = pd.concat([relationFrame, dataFrameRow], ignore_index=True)
                    constructedID = "{}#".format(int(design_id))
            else:
                dataFrameRow = pd.DataFrame([{
                    "design_id": design_id,
                    "constructedID": constructedID,
                    "y": design_content
                }])
                relationFrame = pd.concat([relationFrame, dataFrameRow], ignore_index=True)
        return relationFrame

    def checkRelation(self, targetFrame, checkFrame, appendVariable):
        check_rel = checkFrame["constructedID"]
        tar_rel = targetFrame["constructedID"]

        for check_rel_design_id in check_rel:
            if check_rel_design_id in tar_rel.values:
                continue
            else:
                # Das bedeutet, dass das Ziel nicht existiert
                split_rel = str(check_rel_design_id).split("#")
                missed_design_Id = split_rel[0]

                if len(split_rel) == 7:
                    # Fall: Ziel existiert nicht und eine Beziehung existiert
                    relation = reSe.RelationSentence(
                        (split_rel[1], split_rel[2]),
                        split_rel[3],
                        (split_rel[4], split_rel[5])
                    )
                    self.analizer.call_method_by_name(appendVariable, missed_design_Id, relation.toTupel())
                else:
                    missed_relation_row = checkFrame[checkFrame["design_id"] == int(missed_design_Id)]
                    if not missed_relation_row.empty:
                        relations = missed_relation_row["y"].values[0]
                        if len(relations) == 0:
                            self.analizer.call_method_by_name(appendVariable, missed_design_Id, None)
                        for relIdx in range(len(relations)):
                            relation_tupel = relations[relIdx]
                            self.analizer.appendNotIdentifiedDesign(missed_design_Id, "{}#{}#{}".format(
                                appendVariable,
                                missed_design_Id,
                                relIdx,
                                relation_tupel
                            ))

    def analyzePredAndTest(self):
        true_dict = self.getDict(self.y_test)
        pred_dict = self.getDict(self.y_pred)

        # prepare dictionary of all GT relations and pred Relations
        gt_relation_frame = self.prepareRelation(true_dict)
        pred_relation_frame = self.prepareRelation(pred_dict)

        #check if all relations in pred exists in gt
        self.checkRelation(gt_relation_frame, pred_relation_frame, "appendPredNotInTest")
        self.checkRelation(pred_relation_frame, gt_relation_frame, "appendTestNotInPred")

        predNotInTest = self.buildOutpuCompareToGT(self.analizer.getPredNotInTest(), pred_relation_frame,
                                                   gt_relation_frame)
        notIdentical = self.buildOutpuCompareToGT(self.analizer.getNotIdenticalDesigns(), pred_relation_frame,
                                                  gt_relation_frame)

        return (predNotInTest, notIdentical)

    def buildOutpuCompareToGT(self, foundedContent, ypred, ytest):
        df = pd.DataFrame(columns=["design_id", "sentence", "prediction", "GT"])

        for design_id in foundedContent:
            content = foundedContent[design_id]

            # get tupel value instead of pandas series
            prediction = ypred[ypred["design_id"] == int(design_id)]["y"]
            prediction_value = prediction.iloc[0] if not prediction.empty else None

            gt = ytest[ytest["design_id"] == int(design_id)]["y"]
            gt_value = gt.iloc[0] if not gt.empty else None

            new_row = pd.DataFrame([{
                "design_id": design_id,
                "sentence": "",
                "prediction": prediction_value,
                "GT": gt_value
            }])
            df = pd.concat([df, new_row], ignore_index=True)

        return df

    def createRelationKey(self, design_id, relation):
        subject, subject_label, predicate, object, object_label = relation
        return ("{}".format(design_id)
                + "#"
                + subject
                + "#"
                + subject_label
                + "#"
                + predicate
                + "#"
                + "VERB"
                + "#"
                + object
                + "#"
                + object_label)

    def countElemInDict(self, elem_dict, key):
        elem_dict[key] = elem_dict[key] + 1 if key in elem_dict else 1
        return elem_dict

    def countWordsOfARelation(self, word_dict, relation):
        for word in relation:
            word_dict = self.countElemInDict(word_dict, word)
        word_dict = self.countElemInDict(word_dict, "VERB")
        return word_dict

    def countPredictionAccuracy(self, alldata):
        # create dataframes for 4 different cases that have same workflows
        rel_acc_df = pd.DataFrame(columns=["design_id", "relation_key", "relation", "missingRelation","prediction", "GT", "Acc"])
        sum_rel_acc_df = pd.DataFrame(columns=["relation_key",
                                       "relation",
                                       "missingRelation",
                                       "prediction",
                                       "GT",
                                       "Acc",
                                       "notInGt",
                                       "missDesignId"])
        word_acc_df = pd.DataFrame(columns=[ 'design_id', 'word', 'total', 'hit', 'miss', 'failed', 'acc'])
        sum_word_acc_df = pd.DataFrame(columns=['word', 'total', 'hit', 'miss', 'failed', 'acc', 'notInGt', 'missDesignId'])

        design_ids = alldata["design_id"]
        allRelations = alldata["relations"]
        allPredictions = alldata["predictions"]
        allGts = alldata["GT"]

        for rowIdx in range(len(alldata)):
            design_id = design_ids[rowIdx]
            relations = allRelations[rowIdx]
            predictions = allPredictions[rowIdx]
            gts = allGts[rowIdx]
            predictions_relation_key_dict = self.create_relation_keys_dict(design_id, predictions)
            gt_relation_key_dict = self.create_relation_keys_dict(design_id, gts)

            word_dict = dict()
            relation_dict = dict()
            for relation in relations:
                relation_key = self.createRelationKey(design_id, relation)
                relation_dict = self.countElemInDict(relation_dict, relation_key)

                # relation analyze:
                relation_is_in_Pred = relation_key in predictions_relation_key_dict
                relation_is_in_Gt = relation_key in gt_relation_key_dict

                new_relation_content = {
                    "design_id": design_id,
                    "relation_key": relation_key,
                    "relation": relation,
                    "missingRelation": relation_is_in_Pred and not relation_is_in_Gt,
                    "prediction": relation_is_in_Pred,
                    "GT": relation_is_in_Gt,
                    "Acc": self.calculate_accuracy_single_relation(relation_is_in_Pred, relation_is_in_Gt)
                }
                relationFrame = pd.DataFrame([new_relation_content])
                rel_acc_df = pd.concat([rel_acc_df, relationFrame], ignore_index=True)
                sum_rel_acc_df = self.update_or_insert_into_summary_relation(sum_rel_acc_df,new_relation_content)

                # handle word count
                word_acc_df, sum_word_acc_df = self.update_single_word_analyse(word_acc_df, sum_word_acc_df, new_relation_content)

        return word_acc_df, rel_acc_df, sum_word_acc_df, sum_rel_acc_df

    def evaluate_content(self, val):
        if val:
            return 1
        else:
            return 0

    def combine_y_dataframes(self, df1, df1_name, df2, df2_name):
        combined_df = pd.merge(df1, df2, on='design_id', how='outer', suffixes=('_df1', '_df2'))

        combined_df.rename(columns={
            'design_id': 'design_id',
            'y_df1': df1_name,
            'y_df2': df2_name,
        }, inplace=True)

        def unique_relations(row):
            relations = []

            if isinstance(row[df1_name], list):
                relations.extend(row[df1_name])
            if isinstance(row[df2_name], list):
                relations.extend(row[df2_name])

            # Entferne Duplikate basierend auf createRelationKey
            unique_relations_lst = list(
                {self.createRelationKey(row["design_id"], relation): relation for relation in relations}.values())
            return unique_relations_lst

        combined_df['relations'] = combined_df.apply(unique_relations, axis=1)

        return combined_df

    def create_single_summarized_word_frame(self, design_id, word_dict):
        word_frame = pd.DataFrame()
        for key in word_dict.keys():
            new_row = pd.DataFrame([{
                "design_id": design_id,
                "word": key,
                "total": word_dict[key],
                "hit": 0,
                "miss": 0,
                "acc": 0,
                "notInGt": list(),
                "missDesignId": list()
            }])
            #word_frame = pd.concat(word_frame, , ignore_index=True)
        pass

    def create_relation_keys_dict(self, design_id, relations):
        relation_key_dict = dict()

        for relation in relations:
            relation_key = self.createRelationKey(design_id, relation)
            relation_key_dict[relation_key] = [relation] if relation not in relation_key_dict else relation_key_dict[relation_key].append(relation)
        return relation_key_dict

    def analyzePredAndTestAccuracy(self):
        # get combined datas as frame
        all_data = self.combine_y_dataframes(self.y_pred, "predictions", self.y_test, "GT", )
        return self.countPredictionAccuracy(all_data)

    def calculate_accuracy_single_relation(self, pred_is_in_relation, gt_is_in_relation):
        if pred_is_in_relation and gt_is_in_relation:
            return 1
        elif pred_is_in_relation and not gt_is_in_relation:
            return -1
        else:
            return 0

    def update_or_insert_into_summary_relation(self, sum_rel_acc_df, new_relation_content):
        relation_key = '#'.join(new_relation_content['relation_key'].split('#')[1:])
        mask_key = sum_rel_acc_df['relation_key'] == relation_key

        if relation_key in sum_rel_acc_df['relation_key'].values:
            prediction_val = sum_rel_acc_df.loc[mask_key, 'prediction']
            gt_val = sum_rel_acc_df.loc[mask_key, 'GT']

            sum_rel_acc_df.loc[mask_key, 'prediction'] += self.evaluate_content(new_relation_content['prediction'])
            sum_rel_acc_df.loc[mask_key, 'GT'] += self.evaluate_content(new_relation_content['GT'])
            sum_rel_acc_df.loc[mask_key, 'missingRelation'] += self.evaluate_content(new_relation_content['missingRelation'])
            sum_rel_acc_df.loc[mask_key, 'Acc'] = round(self.safe_divide(prediction_val,gt_val,-1), 2)

            if new_relation_content['missingRelation']:
                sum_rel_acc_df.loc[mask_key, 'notInGt'].values[0].append(new_relation_content['design_id'])

            if not new_relation_content['prediction'] and new_relation_content['GT']:
                sum_rel_acc_df.loc[mask_key, 'missDesignId'].values[0].append(new_relation_content['design_id'])

        else:
            new_row = new_relation_content.copy()
            new_row['relation_key'] = relation_key
            new_row['missingRelation'] = self.evaluate_content(new_relation_content['missingRelation'])
            new_row['prediction'] = self.evaluate_content(new_relation_content['prediction'])
            new_row['GT'] = self.evaluate_content(new_relation_content['GT'])
            new_row['Acc'] = round(new_relation_content['Acc'], 2)
            new_row['notInGt'] = [new_row['design_id']] if new_relation_content['missingRelation'] else list()
            new_row['missDesignId'] = [new_row['design_id']] \
                if new_relation_content['GT'] and not new_relation_content['prediction'] else list()
            new_row.pop('design_id', None)

            new_row_frame = pd.DataFrame([new_row])
            sum_rel_acc_df = pd.concat([sum_rel_acc_df, new_row_frame], ignore_index=True)
        return sum_rel_acc_df

    def safe_divide(self, a, b, default_value=0):
        """
        Teilt a durch b und gibt das Ergebnis zurück.
        Falls b 0 ist, wird der default_value zurückgegeben.

        :param a: Der Dividend
        :param b: Der Divisor
        :param default_value: Der Wert, der zurückgegeben wird, wenn b 0 ist
        :return: Das Ergebnis der Division oder default_value, wenn b 0 ist
        """
        try:
            return float(a) / float(b)
        except ZeroDivisionError:
            return default_value

    def update_single_word_analyse(self, word_acc_df, sum_word_acc_df, new_relation_content):
        design_id = new_relation_content['relation_key'].split('#')[0]

        for key in new_relation_content["relation"]:
            is_hit = 1 if new_relation_content['prediction'] and new_relation_content['GT'] else 0
            is_miss = 1 if not new_relation_content['prediction'] and new_relation_content['GT'] else 0

            if key in sum_word_acc_df['word'].values:
                mask_key_word = (word_acc_df['design_id'] == design_id)  & (word_acc_df['word'] == key)
                word_acc_df.loc[mask_key_word, 'total'] += 1
                word_acc_df.loc[mask_key_word, 'hit'] += is_hit
                word_acc_df.loc[mask_key_word, 'miss'] += is_miss
                word_acc_df.loc[mask_key_word, 'failed'] = word_acc_df.loc[mask_key_word, 'total'] - word_acc_df.loc[
                    mask_key_word, 'hit'] - word_acc_df.loc[mask_key_word, 'miss']
                word_acc_df.loc[mask_key_word, 'acc'] = round(self.safe_divide(1, 1, -1), 2)

                mask_key = sum_word_acc_df['word'] == key
                sum_word_acc_df.loc[mask_key, 'total'] += 1
                sum_word_acc_df.loc[mask_key, 'hit'] += is_hit
                sum_word_acc_df.loc[mask_key, 'miss'] += is_miss
                sum_word_acc_df.loc[mask_key, 'failed'] = sum_word_acc_df.loc[mask_key, 'total'] - sum_word_acc_df.loc[
                    mask_key, 'hit'] - sum_word_acc_df.loc[mask_key, 'miss']
                sum_word_acc_df.loc[mask_key, 'acc'] = round(self.safe_divide(
                    sum_word_acc_df.loc[mask_key, 'hit'],
                    sum_word_acc_df.loc[mask_key, 'total'],
                    -1)
                    , 2)

                if new_relation_content['missingRelation']:
                    sum_word_acc_df.loc[mask_key, 'notInGt'].values[0].append(new_relation_content['design_id'])

                if not new_relation_content['prediction'] and new_relation_content['GT']:
                    sum_word_acc_df.loc[mask_key, 'missDesignId'].values[0].append(new_relation_content['design_id'])

            else:
                new_row = {
                    'word': key,
                    'total': 1,
                    'hit': is_hit,
                    'miss': is_miss,
                    'failed': 1-is_hit-is_miss,
                    'acc': round(self.safe_divide(is_hit, 1, -1), 2),
                    'notInGt': [design_id] if new_relation_content['missingRelation'] else list(),
                    'missDesignId': [design_id] if new_relation_content['GT'] and not new_relation_content['prediction'] else list()
                }
                new_word_row = {
                    'design_id': design_id,
                    'word': key,
                    'total': 1,
                    'hit': is_hit,
                    'miss': is_miss,
                    'failed': 1 - is_hit - is_miss,
                    'acc': round(self.safe_divide(is_hit, 1, -1), 2),
                }
                new_row_frame = pd.DataFrame([new_row])
                new_row_word_frame = pd.DataFrame([new_word_row])
                sum_word_acc_df = pd.concat([sum_word_acc_df, new_row_frame], ignore_index=True)
                word_acc_df = pd.concat([word_acc_df, new_row_word_frame], ignore_index=True)
        return word_acc_df, sum_word_acc_df