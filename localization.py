# Load DA and NLP libraries
import pandas as pd
import spacy
from spacy import displacy
from spacy.tokens import Span
import gensim.downloader as api
# Data prep and pint of localized sentences
from IPython.display import Markdown, display
# Load English words
import en_core_web_sm
nlp = en_core_web_sm.load()

model = api.load("word2vec-google-news-300")
word_vectors = model.wv


class Localization(object):
    def __init__(self,input_country, target_country, original_sentence) :
        self.input_country = input_country
        self.target_country = target_country
        self.original_sentence = original_sentence

    # This function do NER over the sentence passed on parameter
    def localisation_ner(self):
        processed_input_text=nlp(self.original_sentence)
        keyword_set = set()
        entity_mapping = []
        for token in processed_input_text.ents:
            if token.text not in keyword_set:
                keyword_set.add(token.text )
                entity_mapping.append((token.text,token.label_))
        print (entity_mapping)
        displacy.render(processed_input_text, style='ent', jupyter=True)
        
        return entity_mapping

    # Filtering relevant words for localisation
    def relevant_word(self, entity_mapping):
        keep_entities_list = ['PERSON','GPE','FAC','ORG','PRODUCT','NORP','MONEY','LOC','WORK_OF_ART','LAW','LANGUAGE','QUANTITY']
        finalized_entity_mapping = {}
        for ent in entity_mapping:
            if ent[1] in keep_entities_list:
                finalized_entity_mapping[ent[0]] = []

        print (finalized_entity_mapping)
        
        return finalized_entity_mapping

    # Localisation using Gensim library
    def localization(self, finalized_entity_mapping):
        #Origin_country='USA' 
        #Target_country='France'

        final_mapping ={}

        for word in finalized_entity_mapping: 
            word = word.strip()
            word = word.replace(" ","_")
            try:
                similar_words_list= model.most_similar(positive=[self.target_country,word],negative=[self.input_country],topn=10)
                # Remove the scores for the retrieved choices
                similar_words_list = [choices[0].replace("_"," ") for choices in similar_words_list ]
                final_mapping[word.replace("_"," ")] = similar_words_list
            except:
                similar_words_list = []
                print (" Fetching similar words failed for ",word)
        print (word," -- Replacement suggestions -- ",similar_words_list)
        
        return final_mapping

    #  Here localization is performed assuming the correct choice is returned first.

    #  This function is used to bolden the relevant entities that are changed.
    def prepare_string(self, mapping, orig=True):
        if orig:
            for k in mapping:
                sentence = self.original_sentence.replace(k,"**"+k+"**")
        else:
            for k in mapping:
                sentence = sentence.replace(mapping[k][0],"**"+mapping[k][0]+"**")

        return sentence

    # Here, we choose the suitable word in mapping list and replace with the right word in the original sentence
    def localize(self,mapping):
        for k in mapping:
            temp_var = ""
            for (cpt,i) in enumerate(mapping[k], start = 0):
                if mapping[k][cpt] not in self.original_sentence :
                    temp_var = mapping[k][cpt]
                    break
            sentence = self.original_sentence.replace(k,"**" + temp_var + "**")
            
        return sentence


    def printmd(self,string):
        return Markdown(string)
