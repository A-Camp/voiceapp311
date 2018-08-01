"""
Boston Data Alexa skill.

This module is the entry point for processing voice data from an Alexa device.
"""

from mycity.mycity_request_data_model import MyCityRequestDataModel
from mycity.mycity_controller import execute_request


def lambda_handler(event, context):
    """
    Translate the Amazon request to a MC_Request_Model and call main.

    :param event: JSON object containing the raw request information received
        from the Alexa service platform
    :param context: a LambdaContext object containing runtime info
    :return: JSON response object to be sent to the Alexa service platform 
    """
    print(
        "[module: lambda_function]",
        "[function: lambda_handler]",
        "Amazon request received:\n",
        str(event)
    )

    model = platform_to_mycity_request(event)
    return mycity_response_to_platform(execute_request(model))


def platform_to_mycity_request(event):
    """
    Translates from Amazon platform request to MyCityRequestDataModel

    :param event: JSON object containing the raw request information received
        from the Alexa service platform
    :return: MyCityRequestDataModel object (formatted to be understood and
        acted on by mycity_controller)
    """
    print(
        "\n\n[module: lambda_function]",
        "[function: platform_to_mycity_request]",
        "Amazon request received:\n",
        str(event)
    )
    mycity_request = MyCityRequestDataModel()
    mycity_request.request_type = event['request']['type']
    mycity_request.request_id = event['request']['requestId']
    mycity_request.is_new_session = event['session']['new']
    mycity_request.session_id = event['session']['sessionId']
    mycity_request.device_id = event['context']['System']['device']['deviceId']
    mycity_request.api_access_token = event['context']['System']['apiAccessToken']
    
    if 'attributes' in event['session']:
        mycity_request.session_attributes = event['session']['attributes']
    else:
        mycity_request.session_attributes = {}
    mycity_request.application_id = event['session']['application']['applicationId']
    if 'intent' in event['request']:
        mycity_request.intent_name = event['request']['intent']['name']
        if 'slots' in event['request']['intent']:
            mycity_request.intent_variables = event['request']['intent']['slots']
    else:
        mycity_request.intent_name = None
    mycity_request.output_speech = None
    mycity_request.reprompt_text = None
    mycity_request.should_end_session = False

    return mycity_request


def mycity_response_to_platform(mycity_response):
    """
    Translates from MyCityResponseDataModel to Amazon platform response.

    The platform response contains:
    - a version number,
    - session information,
    - a response "speechlet" dictionary containing information on how Alexa
      responds to the user command.

    :param mycity_response: MyCityResponseDataModel object generated by
        mycity_controller executing a request
    :return: JSON response object that will be sent to the Alexa
        service platform
    """
    print(
        "\n\n[module: lambda_function]",
        "[function: mycity_response_to_platform]",
        "MyCityResponseDataModel object received: " + str(mycity_response)
    )

    if mycity_response.dialog_directive:
        if mycity_response.dialog_directive['type'] == "Dialog.Delegate":
            response = {
                'directives': [
                    mycity_response.dialog_directive
                ]
            }
        else: 
            response = {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': mycity_response.output_speech
             },
                'card': {
                 'type': 'Simple',
                    'title': 'SessionSpeechlet - ' + str(mycity_response.card_title),
                    'content': 'SessionSpeechlet - ' + str(mycity_response.output_speech)
                },
                'reprompt': {
                 'outputSpeech': {
                        'type': 'PlainText',
                        'text': mycity_response.reprompt_text
                 }
             },
                'shouldEndSession': mycity_response.should_end_session,
                'directives' : [
                    mycity_response.dialog_directive
                    ]
            }
    else:
        response = {
            'outputSpeech': {
                'type': 'PlainText',
                'text': mycity_response.output_speech
            },
            'card': {
                'type': 'Simple',
                'title': str(mycity_response.card_title),
                'content': str(mycity_response.output_speech)
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': mycity_response.reprompt_text
                }
            },
            'shouldEndSession': mycity_response.should_end_session
        }

    result = {
        'version': '1.0',
        'sessionAttributes': mycity_response.session_attributes,
        'response': response
    }
    print('Result to platform:\n', result)
    return result
