"""Alexa intent used to find snow emergency parking"""


import mycity.intents.intent_constants as intent_constants
import mycity.intents.speech_constants.snow_parking_intent as constants
from mycity.utilities.finder.FinderCSV import FinderCSV
from mycity.mycity_response_data_model import MyCityResponseDataModel
import logging

PARKING_INFO_URL = "http://bostonopendata-boston.opendata.arcgis.com/datasets/53ebc23fcc654111b642f70e61c63852_0.csv"
SNOW_PARKING_CARD_TITLE = "Snow Parking"
ADDRESS_KEY = "Address"

logger = logging.getLogger(__name__)


def format_record_fields(record):
    """
    Updates the record fields by replacing the raw information with a sentence
    that provides context and will be more easily understood by users.
    
    :param record: a dictionary with driving time, driving_distance and all 
        fields from the closest record
    :return: None
    """
    logger.debug('record: ' + str(record))
    record["Phone"] = constants.PHONE_PREPARED_STRING.format(record["Phone"]) \
        if record["Phone"].strip() != "" else constants.NO_PHONE
    record["Fee"] = constants.FEE_PREPARED_STRING.format(record["Fee"]) \
        if record["Fee"] != "No Charge" else constants.NO_FEE


def get_snow_emergency_parking_intent(mycity_request):
    """
    Populate MyCityResponseDataModel with snow emergency parking response information.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    logger.debug('MyCityRequestDataModel received:' + mycity_request.get_logger_string())

    mycity_response = MyCityResponseDataModel()
    if intent_constants.CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        finder = FinderCSV(mycity_request, PARKING_INFO_URL, ADDRESS_KEY, 
                           constants.OUTPUT_SPEECH_FORMAT, format_record_fields)
        print("Finding snow emergency parking for {}".format(finder.origin_address))
        finder.start()
        mycity_response.output_speech = finder.get_output_speech()

    else:
        print("Error: Called snow_parking_intent with no address")
        mycity_response.output_speech = constants.ERROR_SPEECH

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = SNOW_PARKING_CARD_TITLE
    
    return mycity_response
