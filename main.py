from flask import Flask, jsonify
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from werkzeug.exceptions import BadRequest
from flask_restplus import Api, Resource, reqparse
import localization
import sys


app = Flask(__name__)
api = Api(app=app, version='0.1', title='Localization Api', description='', validate=True)
n_space = api.namespace('Converteo Tech', 'Welcome to our swagger interface !')


# argument parsing
parser = reqparse.RequestParser()
parser.add_argument('input_country', type=str, choices=['USA', 'France'], required=True, help="Select one origin country.")
parser.add_argument('target_country', type=str, choices=['USA', 'France'], required=True, help='Select one target country.')
parser.add_argument('original_sentence', type=str, help='Please, enter your original input sentence !')


@n_space.route("/results")
class FindLocalization(Resource):
    @api.expect(parser)
    def get(self):
        # use parser and find the user's query
        args = parser.parse_args()
        input_country = args["input_country"]
        target_country = args["target_country"]
        original_sentence = args["original_sentence"]
        localization_instance = localization.Localization(input_country, target_country, original_sentence)
        ner_localization = localization_instance.localisation_ner()
        filtered_words = localization_instance.relevant_word(ner_localization)
        gensim_localization = localization_instance.localization(filtered_words)
        #print('Original Sentence:')
        original_sentence_markdown = localization_instance.printmd(localization_instance.prepare_string(original_sentence,gensim_localization))
        localized_strings = localization_instance.localize(gensim_localization)
        
        #print('\nLocalized Sentence:')
        localized_sentence =localization_instance.printmd(localized_strings)

        output = jsonify({"original sentence" : original_sentence_markdown, "localized sentence" : localized_sentence})

        return output



if __name__ == '__main__':
    app.run(port= 4002, host= 'localhost')