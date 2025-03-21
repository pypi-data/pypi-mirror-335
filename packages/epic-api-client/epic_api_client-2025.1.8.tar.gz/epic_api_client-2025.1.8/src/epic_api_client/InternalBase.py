#    ____   # -------------------------------------------------- #
#   | ^  |  # EPICClient for AUMC               				 #
#   \  --   # o.m.vandermeer@amsterdamumc.nl        			 #
# \_| ﬤ| ﬤ  # If you like this code, treat him to a coffee! ;)	 #
#   |_)_)   # -------------------------------------------------- #

from json import dumps
import uuid
from epic_api_client.EPICClient import EPICHttpClient


class InternalBase:

    def __init__(self, epic_client: EPICHttpClient) -> None:
        """
        Initialize the InternalBase class.

        :param epic_client: The EPICClient instance to use for making requests.
        :type epic_client: EPICClient
        """
        self.epic_client = epic_client
        self.post = self.epic_client.post
        self.get = self.epic_client.get
        self.put = self.epic_client.put
        self.delete = self.epic_client.delete
        self.patch = self.epic_client.patch
        self.base_url = self.epic_client.base_url

    def set_smart_data_values(
        self,
        context_name: str,
        entity_id: str,
        entity_id_type: str,
        user_id: str,
        user_id_type: str,
        smart_data_values: list,
        contact_id: str = None,
        contact_id_type: str = "DAT",
        source: str = "Web Service",
        extra_headers: dict = {},
    ):
        """
        Sets raw values for SmartData elements.

        Args:
            context_name (str): Name of the context associated with SmartData elements (e.g., PATIENT, ENCOUNTER).
            entity_id (str): ID for the entity associated with the context.
            entity_id_type (str): Type of the provided entity ID (e.g., Internal, External, CID).
            user_id (str): User ID used for auditing.
            user_id_type (str): Type of the provided User ID (e.g., Internal, External).
            smart_data_values (list): List of dictionaries representing SmartData values to set.
                Each dictionary should contain keys `Comments`, `SmartDataID`, `SmartDataIDType`, and `Values`.
            contact_id (str, optional): Contact date for the ENCOUNTER context.
            contact_id_type (str, optional): Type for the provided contact date. Defaults to "DAT".
            source (str, optional): Source setting the values. Defaults to "Web Service".
            extra_headers (dict, optional): Additional headers to include in the request.

        Returns:
            dict: Parsed response from the API.
        """
        endpoint = "api/epic/2013/Clinical/Utility/SETSMARTDATAVALUES/SmartData/Values"

        payload = {
            
                #"@xmlns": "urn:Epic-com:Clinical.2012.Services.Utility",
                "ContextName": context_name,
                "EntityID": entity_id,
                "EntityIDType": entity_id_type,
                "UserID": user_id,
                "UserIDType": user_id_type,
                "Source": source,
                "SmartDataValues": {
                    "Value": [
                        {
                            "Comments": {"string": [val["Comments"]]},
                            "SmartDataID": val["SmartDataID"],
                            "SmartDataIDType": val["SmartDataIDType"],
                            "Values": {"string": [val["Values"]]},
                        }
                        for val in smart_data_values
                    ]
                },
            }

        # Include optional fields if provided
        if contact_id:
            payload["ContactID"] = contact_id
            payload["ContactIDType"] = contact_id_type

        return self.put(endpoint, json=payload, extra_headers=extra_headers)

    def get_smart_data_values(
        self,
        context_name: str,
        entity_id: str,
        entity_id_type: str,
        user_id: str,
        user_id_type: str,
        smart_data_ids: list = None,
        contact_id: str = None,
        contact_id_type: str = "DAT",
        extra_headers: dict = {},
    ):
        """
        Retrieves raw values for SmartData elements.

        Args:
            context_name (str): Name of the context associated with SmartData elements (e.g., PATIENT, ENCOUNTER).
            entity_id (str): ID for the entity associated with the context.
            entity_id_type (str): Type of the provided entity ID (e.g., Internal, External, CID).
            user_id (str): User ID used for auditing.
            user_id_type (str): Type of the provided User ID (e.g., Internal, External).
            smart_data_ids (list, optional): List of dictionaries representing SmartData IDs to retrieve.
                Each dictionary should contain keys `ID` and `Type`.
            contact_id (str, optional): Contact date for the ENCOUNTER context.
            contact_id_type (str, optional): Type for the provided contact date. Defaults to "DAT".
            extra_headers (dict, optional): Additional headers to include in the request.

        Returns:
            dict: Parsed response from the API.
        """
        endpoint = "api/epic/2013/Clinical/Utility/GETSMARTDATAVALUES/SmartData/Values"

        payload = {
            
                "ContextName": context_name,
                "EntityID": entity_id,
                "EntityIDType": entity_id_type,
                "UserID": user_id,
                "UserIDType": user_id_type,
                "SmartDataIDs": (
                    {
                        "IDType": [
                            {"ID": val["ID"], "Type": val["Type"]}
                            for val in (smart_data_ids or [])
                        ]
                    }
                    if smart_data_ids
                    else None
                ),
            }
        

        # Include optional fields if provided
        if contact_id:
            payload["ContactID"] = contact_id
            payload["ContactIDType"] = contact_id_type

        return self.post(endpoint, json=payload, extra_headers=extra_headers)

    def handle_external_model_scores(
        self,
        model_id: str,
        entity_ids: list,
        outputs: dict,
        job_id: str = None,
        error_message: str = None,
        output_type: str = "",
        raw: dict = None,
        predictive_context: dict = {},
        ScoreDisplayed: str = "",
    ):
        """
        Send predictive model scores back to the Epic Cognitive Computing Platform for filing.

        :param model_id: str, the ECCP model ID the scores are for
        :param job_id: str, the autogenerated job ID for the evaluation on ECCP
        :param output_type: str, the type of output for the predictive model
        :param entity_ids: list, a list of dictionaries with ID and Type for the entity
        :param outputs: dict, the output values of the predictive model
        :param raw: dict, optional, raw features used to calculate the scores
        :param predictive_context: dict, optional, additional context information for the predictive model
        :param ScoreDisplayed: str, the key for the score to be displayed

        :return: dict, the response from the Epic Cognitive Computing Platform
        """
        if not job_id:
            job_id = uuid.uuid4()
        print("Sending external model scores to ECCP with job ID: {}".format(job_id))
        url = f"/api/epic/2017/Reporting/Predictive/HANDLEEXTERNALMODELSCORES?modelId={model_id}&jobId={job_id}"
        headers = {"Content-Type": "application/json"}

        # check if outputs is in the following format:
        # {
        #     "Output_Name": {
        #         "Scores": {
        #             "Score_Name_1" : { "Values": [val1, val2,.., valN] },
        #             "Score_Name_2" : { "Values": [val1, val2,.., valN] }
        #         },
        #         "Features": {
        #             "Feature1": { "Contributions":[contrib1, contrib2, ..., contribN]},
        #             "Feature2": { "Contributions":[contrib1, contrib2, ..., contribN]}
        #         }
        #     }
        # }
        if not isinstance(outputs, dict):
            raise ValueError("outputs should be a dictionary")
        for output_name, output in outputs.items():
            if not isinstance(output, dict) or "Scores" not in output or "Features" not in output:
                raise ValueError(f"outputs[{output_name}] should be a dictionary with 'Scores' and 'Features' keys")
            scores = output["Scores"]
            features = output["Features"]
            if not isinstance(scores, dict) or not isinstance(features, dict):
                raise ValueError(f"outputs[{output_name}]['Scores'] and outputs[{output_name}]['Features'] should be dictionaries")
            for score_name, score in scores.items():
                if not isinstance(score, dict) or "Values" not in score:
                    raise ValueError(f"outputs[{output_name}]['Scores'][{score_name}] should be a dictionary with 'Values' key")
                if not isinstance(score["Values"], list):
                    raise ValueError(f"outputs[{output_name}]['Scores'][{score_name}]['Values'] should be a list")
            for feature_name, feature in features.items():
                if not isinstance(feature, dict) or "Contributions" not in feature:
                    raise ValueError(f"outputs[{output_name}]['Features'][{feature_name}] should be a dictionary with 'Contributions' key")
                if not isinstance(feature["Contributions"], list):
                    raise ValueError(f"outputs[{output_name}]['Features'][{feature_name}]['Contributions'] should be a list")

        # Build the request payload
        request_body = {
            "result": {
                "exit_code": "0",
                "stdout": [""],
                "stderr": [""],
                "results": {
                    "EntityId": [
                        {"ID": entity["ID"], "Type": entity["Type"]}
                        for entity in entity_ids
                    ],
                    "ScoreDisplayed": ScoreDisplayed,
                    "PredictiveContext": predictive_context or {},
                    "OutputType": output_type,
                    "Outputs": outputs,
                    "Raw": raw or {},
                },
                "messages": [],
            }
        }

        if error_message:
            request_body["result"]["Error"] = error_message

        # Send the request
        response = self.post(url, extra_headers=headers, data=dumps(request_body))

        return response
