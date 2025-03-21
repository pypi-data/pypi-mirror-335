#    ____   # -------------------------------------------------- #
#   | ^  |  # EPICClient for AUMC               				 #
#   \  --   # o.m.vandermeer@amsterdamumc.nl        			 #
# \_| ﬤ| ﬤ  # If you like this code, treat him to a coffee! ;)	 #
#   |_)_)   # -------------------------------------------------- #

from json import dumps
from epic_api_client.EPICHttpClient import EPICHttpClient
from epic_api_client.FHIRExtension import FHIRExtension
from epic_api_client.InternalExtension import InternalExtension
from epic_api_client.JWTGenerator import JWTGenerator
import requests
import warnings
import importlib


class EPICClient(EPICHttpClient):
    def __init__(
        self,
        base_url: str = None,
        headers: dict = None,
        client_id: str = None,
        jwt_generator: JWTGenerator = None,
        use_unix_socket: bool = False,
        debug_mode: bool = False,
    ):
        super().__init__(base_url, headers, client_id, jwt_generator, use_unix_socket, debug_mode)
        # Pass `self` to extensions
        self.check_for_updates("epic_api_client")
        self.fhir = FHIRExtension(self)
        self.internal = InternalExtension(self)
        self.dino = "Mrauw!"

    def check_for_updates(self, package_name):
        try:
            # Get the installed version
            current_version = importlib.metadata.version(package_name)

            # Query the PyPI API for the latest version
            response = requests.get(
                f"https://pypi.org/pypi/{package_name}/json", timeout=5
            )
            response.raise_for_status()  # Raise HTTPError for bad responses

            latest_version = response.json()["info"]["version"]

            # Compare versions
            if current_version != latest_version:
                print(
                    f"Update available: {package_name} {latest_version} (current: {current_version}).\n"
                    f"Run `pip install --upgrade {package_name}` to update."
                )
            else:
                print(f"{package_name} is up to date: {current_version}")
        except requests.ConnectionError:
            print("No internet connection. Skipping version check.")
        except Exception as e:
            print(f"Version check failed: {e}")

    # deprecated / relocated functions
    def get_metadata(self, *args, **kwargs):
        warnings.warn(
            "get_metadata has been relocated to fhir. "
            "Please update your code to use fhir.get_metadata instead.",
            FutureWarning,
            stacklevel=2,
        )
        return self.fhir.get_metadata(*args, **kwargs)

    def get_resource(self, *args, **kwargs):
        warnings.warn(
            "get_resource has been relocated to fhir. "
            "Please update your code to use fhir.get_resource instead.",
            FutureWarning,
            stacklevel=2,
        )
        return self.fhir.get_resource(*args, **kwargs)

    def patient_read(self, *args, **kwargs):
        warnings.warn(
            "patient_read has been relocated to fhir. "
            "Please update your code to use fhir.patient_read instead.",
            FutureWarning,
            stacklevel=2,
        )
        return self.fhir.patient_read(*args, **kwargs)

    def patient_search_MRN(self, *args, **kwargs):
        warnings.warn(
            "patient_search_MRN has been relocated to fhir. "
            "Please update your code to use fhir.patient_search_MRN instead.",
            FutureWarning,
            stacklevel=2,
        )
        return self.fhir.patient_search_MRN(*args, **kwargs)

    def mrn_to_FHIRid(self, *args, **kwargs):
        warnings.warn(
            "mrn_to_FHIRid has been relocated to fhir. "
            "Please update your code to use fhir.mrn_to_FHIRid instead.",
            FutureWarning,
            stacklevel=2,
        )
        return self.fhir.mrn_to_FHIRid(*args, **kwargs)

    def encounter_read(self, *args, **kwargs):
        warnings.warn(
            "encounter_read has been relocated to fhir. "
            "Please update your code to use fhir.encounter_read instead.",
            FutureWarning,
            stacklevel=2,
        )
        return self.fhir.encounter_read(*args, **kwargs)

    def encounter_search(self, *args, **kwargs):
        warnings.warn(
            "encounter_search has been relocated to fhir. "
            "Please update your code to use fhir.encounter_search instead.",
            FutureWarning,
            stacklevel=2,
        )
        return self.fhir.encounter_search(*args, **kwargs)

    def document_reference_read(self, *args, **kwargs):
        warnings.warn(
            "document_reference_read has been relocated to fhir. "
            "Please update your code to use fhir.document_reference_read instead.",
            FutureWarning,
            stacklevel=2,
        )
        return self.fhir.document_reference_read(*args, **kwargs)

    def document_reference_search(self, *args, **kwargs):
        warnings.warn(
            "document_reference_search has been relocated to fhir. "
            "Please update your code to use fhir.document_reference_search instead.",
            FutureWarning,
            stacklevel=2,
        )
        return self.fhir.document_reference_search(*args, **kwargs)

    def observation_create(self, *args, **kwargs):
        warnings.warn(
            "observation_create has been relocated to fhir. "
            "Please update your code to use fhir.observation_create instead.",
            FutureWarning,
            stacklevel=2,
        )
        return self.fhir.observation_create(*args, **kwargs)

    def document_reference_create(self, *args, **kwargs):
        warnings.warn(
            "document_reference_create has been relocated to fhir. "
            "Please update your code to use fhir.document_reference_create instead.",
            FutureWarning,
            stacklevel=2,
        )
        return self.fhir.document_reference_create(*args, **kwargs)

    def handle_external_model_scores(self, *args, **kwargs):
        warnings.warn(
            "handle_external_model_scores has been relocated to internal. "
            "Please update your code to use internal.handle_external_model_scores instead.",
            FutureWarning,
            stacklevel=2,
        )
        return self.internal.handle_external_model_scores(*args, **kwargs)
