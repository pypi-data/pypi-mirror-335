#    ____   # -------------------------------------------------- #
#   | ^  |  # EPICClient for AUMC               				 #
#   \  --   # o.m.vandermeer@amsterdamumc.nl        			 #
# \_| ﬤ| ﬤ  # If you like this code, treat him to a coffee! ;)	 #
#   |_)_)   # -------------------------------------------------- #

import requests
import base64
from json import dumps
from epic_api_client.SimpleHttpClient import SimpleHttpClient
from datetime import datetime
import uuid


class EPICClient(SimpleHttpClient):
    def __init__(self, base_url=None, headers=None, client_id=None, jwt_generator=None):
        super().__init__(base_url, headers)
        self.set_header("Epic-Client-ID", client_id)
        if base_url is None:
            print("No base URL provided, using sandbox URL")
            base_url = "https://vendorservices.epic.com/interconnect-amcurprd-oauth"
        self.jwt_generator = jwt_generator
        self.client_id = client_id
        self.dino = "Mrauw!"

    def get_metadata(self, version="R4"):
        if version not in ["DSTU2", "STU3", "R4"]:
            raise ValueError(
                "Invalid version. Please specify either 'DSTU2', 'STU3' or 'R4'."
            )

        endpoint = f"/api/FHIR/{version}/metadata"
        endpoint = self.base_url + endpoint
        response = self.get(endpoint)
        print("GET response:", response)

    def set_token(self, token):
        self.set_header("Authorization", f"Bearer {token}")
        self.set_header("Accept", "application/fhir+json")

    def obtain_access_token(self):
        token_endpoint = self.base_url + "/oauth2/token"
        # Generate JWT
        jwt_token = self.jwt_generator.create_jwt(self.client_id, token_endpoint)

        # Set up the POST request data
        data = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": jwt_token,
        }

        # POST the JWT to the token endpoint
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(token_endpoint, data=data, headers=headers)
        response_data = response.json()
        # Check for successful response
        if response.status_code == 200:
            print("authentication successful")
            self.access_token = response_data.get("access_token")
            self.set_token(self.access_token)
            # self.set_header('prefer', 'return=representation')
            if "scope" in response_data:
                print("scope of client id: ", response_data["scope"])
            else:
                print("no scope of client id available")
            return response.json()  # Returns the access token and other data
        else:
            print("Response Status Code:", response.status_code)
            print("Response Text:", response.text)
            response.raise_for_status()

    def get_resource(
        self, resource_type, resource_id=None, version="R4", **optional_params
    ):
        """
        Get a FHIR resource with mandatory and optional parameters.

        :param resource_type: str, the type of the FHIR resource (e.g., 'Patient', 'Encounter')
        :param resource_id: str, the ID of the resource
        :param optional_params: dict, optional query parameters to be added to the URL

        :return: dict, the response from the FHIR server
        """
        base_url = f"api/FHIR/{version}/{resource_type}"

        if resource_id:
            base_url += f"/{resource_id}"

        if optional_params:
            # Append optional query parameters to the URL
            for key, value in optional_params.items():
                if value != None:
                    qlist = [f"{key}={value}"]
            query_string = "&".join(qlist)
            url = f"{base_url}?{query_string}"
        else:
            url = base_url

        return self.get(url)

    def patient_read(self, patient_id):
        """Retrieve patient information by patient ID."""
        return self.get_resource("Patient", patient_id)

    def patient_search_MRN(self, patient_mrn):
        """Retrieve patient information by patient MRN."""
        mrn_id = "UMCA|" + patient_mrn
        return self.get_resource("Patient", identifier=mrn_id)

    def mrn_to_FHIRid(self, patient_mrn):
        result = self.patient_search_MRN(patient_mrn)
        if len(result["entry"]) == 0:
            raise ValueError("Patient not found: ", patient_mrn)
        FHIRid = result["entry"][0]["resource"]["id"]
        return FHIRid

    def encounter_read(self, encounter_id):
        """Retrieve encounter information by patient ID."""
        return self.get_resource("Encounter", encounter_id)

    def encounter_search(self, patient_id):
        """Retrieve encounters by patient ID."""
        return self.get_resource("Encounter", patient=patient_id)

    def document_reference_read(self, document_reference_id):
        """Retrieve document_reference information by document_reference_id."""
        return self.get_resource("DocumentReference", document_reference_id)

    def document_reference_search(
        self,
        category=None,
        date=None,
        docstatus=None,
        encounter=None,
        patient=None,
        period=None,
        subject=None,
        d_type=None,
    ):
        """Retrieve encounters by patient ID."""
        if not (subject or patient):
            raise ValueError("At least one of subject or patient must be provided")
        if not (category or d_type):
            category = "clinical-note"
        return self.get_resource(
            "DocumentReference",
            category=category,
            date=date,
            docstatus=docstatus,
            encounter=encounter,
            patient=patient,
            period=period,
            subject=subject,
            type=d_type,
        )

    def observation_create(self, patient_id, encounter_id, flowsheet_id, name, value):
        """Create observation. For now only 1 entry per call is supported"""
        url = "/api/FHIR/R4/Observation"
        observation = {
            "resourceType": "Observation",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs",
                        }
                    ],
                    "text": "Vital Signs",
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://open.epic.com/FHIR/StructureDefinition/observation-flowsheet-id",  # urn:oid:2.16.840.1.113883.6.88
                        "code": flowsheet_id,
                        "display": name,
                    }
                ],
                "text": name,
            },
            "subject": {
                "reference": "Patient/" + patient_id,
                # "display": "Meiko Lufhir"
            },
            "encounter": {"reference": "Encounter/" + encounter_id},
            "effectiveDateTime": datetime.utcnow().strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),  # "2019-09-05T20:00:00Z",
            "valueQuantity": {
                "value": value,
                # "unit": "",
                # "system": "http://unitsofmeasure.org",
                # "code": "%"
            },
            "status": "final",
        }
        return self.post(url, json=observation)

    def document_reference_create(
        self,
        patient_id,
        encounter_id,
        note_text,
        note_type="Consultation Note",
        doc_status="final",
        prefer="return=representation",
    ):
        """
        Create a DocumentReference resource in the FHIR server.

        :param patient_id: str, the ID of the patient
        :param encounter_id: str, the ID of the encounter
        :param note_text: str, the plain text of the note
        :param note_type: str, the type of the note, default is "Consultation Note"
        :param doc_status: str, the status of the document, default is "final"
        :param prefer: str, the prefer header to control the response, default is "return=representation"

        :return: dict, the response from the FHIR server
        """
        url = "/api/FHIR/R4/DocumentReference"
        headers = {"Content-Type": "application/fhir+json", "Prefer": prefer}

        document_reference = {
            "resourceType": "DocumentReference",
            "docStatus": doc_status,
            "type": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "11488-4",
                        "display": note_type,
                    }
                ],
                "text": note_type,
            },
            "subject": {"reference": f"Patient/{patient_id}"},
            "content": [
                {
                    "attachment": {
                        "contentType": "text/plain",
                        "data": base64.b64encode(note_text.encode("utf-8")).decode(
                            "utf-8"
                        ),
                    }
                }
            ],
            "context": {"encounter": [{"reference": f"Encounter/{encounter_id}"}]},
        }

        return self.post(url, extra_headers=headers, data=dumps(document_reference))

    def handle_external_model_scores(
        self,
        model_id,
        entity_ids,
        outputs,
        job_id=uuid.uuid4(),
        error_message=None,
        output_type="",
        raw=None,
        predictive_context={},
        ScoreDisplayed="",
    ):
        """
        Send predictive model scores back to the Epic Cognitive Computing Platform for filing.

        :param model_id: str, the ECCP model ID the scores are for
        :param job_id: str, the autogenerated job ID for the evaluation on ECCP
        :param output_type: str, the type of output for the predictive model
        :param server_version: str, the server version of the predictive context
        :param session_id: str, the session ID of the predictive context
        :param entity_ids: list, a list of dictionaries with ID and Type for the entity
        :param outputs: dict, the output values of the predictive model
        :param raw: dict, optional, raw features used to calculate the scores
        :param predictive_context: dict, optional, additional context information for the predictive model

        :return: dict, the response from the Epic Cognitive Computing Platform
        """
        print("Sending external model scores to ECCP with job ID: {}".format(job_id))
        url = f"/api/epic/2017/Reporting/Predictive/HANDLEEXTERNALMODELSCORES?modelId={model_id}&jobId={job_id}"
        headers = {"Content-Type": "application/json"}

        # Build the request payload
        request_body = {}

        request_body["OutputType"] = output_type

        request_body["PredictiveContext"] = predictive_context

        if error_message:
            request_body["Error"] = error_message

        request_body["ScoreDisplayed"] = ScoreDisplayed

        # Add entity IDs
        request_body["EntityId"] = [
            {"ID": entity["ID"], "Type": entity["Type"]} for entity in entity_ids
        ]

        # Add outputs and optional raw features
        request_body["Outputs"] = outputs
        if raw:
            request_body["Raw"] = raw

        # Send the request
        response = self.post(url, extra_headers=headers, data=dumps(request_body))

        return response

    def print_json(self, json_object):
        """
        Prints a JSON object in a readable, formatted way.

        Args:
        json_object (dict): The JSON object to be printed.
        """
        formatted_json = dumps(json_object, indent=2, sort_keys=True)
        print(formatted_json)
