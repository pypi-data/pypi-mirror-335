import base64
import io
import json
import requests
import time
import uuid
import webbrowser

from keycloak import KeycloakOpenID
from qiskit import qpy
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Pauli, PauliList, SparsePauliOp
from qiskit.quantum_info.operators.linear_op import LinearOp
from urllib.parse import urlencode


def serialize_object(object):
    buffer = io.BytesIO()
    qpy.dump(object, buffer)
    qpy_binary_data = buffer.getvalue()
    base64_encoded_object = base64.b64encode(qpy_binary_data).decode("utf-8")
    return base64_encoded_object


class AuthenticationFailure(Exception):
    def __init__(self, message):
        self.message = message


class Job:
    def __init__(self, job_id):
        self._job_id = job_id

    def id(self):
        return self._job_id


class WorkflowJob:
    def __init__(self, job_id):
        self._job_id = job_id

    def id(self):
        return self._job_id


class InputData:
    def __init__(self, label=None, content=None):
        self.data = {}
        if label:
            self.add_data(label, content)

    def add_data(self, label, content):
        self.check_label(label, self.data)
        try:
            if label == "operator":
                content = self.validate_and_serialize_operator(content)
            elif label == "pub":
                content = self.validate_and_serialize_pub(content)
                if not "pubs" in self.data.keys():
                    self.data["pubs"] = []
                self.data["pubs"].append(content)
            else:
                self.data[label] = content
        except (OverflowError, TypeError, ValueError):
            raise Exception("Input data content must be JSON serializable.")

    def check_label(self, label, data):
        if type(label) != str:
            raise Exception("Input data label must be string.")
        if label not in [
            "ansatz-parameters",
            "ising-model",
            "lattice",
            "molecule-info",
            "operator",
            "pub",
            "qubo-model",
            "vectors-data",
        ]:
            raise Exception(
                f"Input data of type {label} is not supported. Please choose one of the following options: 'ising-model', 'lattice', 'molecule-info', 'operator', 'pub', 'qubo-model', 'data-vectors'."
            )
        if label != "pub" and label in data.keys():
            raise Exception(
                f"An input data item of type '{label}' has already been added to the job input data. Multiple data items of same category are allowed only for PUBs."
            )

    def validate_and_serialize_pub(self, pub):
        shots = None
        paramaters = None
        if type(pub) == QuantumCircuit:
            quantum_circuit = pub
        elif type(pub) != tuple:
            raise Exception(
                "A pub can be either a quantum circuit or a tuple containing a quantum circuit, optionally second a list of circuit parameters and optionally third a number of shots."
            )
        elif len(pub) == 3:
            quantum_circuit, paramaters, shots = pub
        elif len(pub) == 2:
            quantum_circuit, paramaters = pub
        elif len(pub) == 1:
            quantum_circuit = pub[0]
        else:
            raise Exception(
                "A pub can be a tuple with at most 3 elements: a quantum circuit, a list of circuit paramaters and a number of shots."
            )
        if shots is not None and type(shots) != int:
            raise Exception(
                "The 'shots' setting in a PUB must be an integer and be positioned as the third element of a tuple specifying a PUB."
            )
        if paramaters is not None and type(paramaters) != list:
            raise Exception(
                "The 'paramaters' in a PUB must be a list of numbers and be positioned as the second element of a tuple specifying a PUB."
            )
        if quantum_circuit.num_parameters == 0 and (
            paramaters is not None and len(paramaters) != 0
        ):
            raise Exception(
                "A circuit with zero parameters must have 'paramaters' argument 'None' or an empty list."
            )
        elif paramaters is not None and quantum_circuit.num_parameters != len(
            paramaters
        ):
            raise Exception(
                f"The number of paramaters for a quantum circuit {quantum_circuit.num_parameters} is different from the length {len(paramaters)} of the list of aruguments."
            )
        if paramaters is not None and not all(
            isinstance(item, (int, float)) for item in paramaters
        ):
            raise Exception(
                "The 'paramaters' setting in a PUB must be a list of numbers."
            )

        return (serialize_object(quantum_circuit), paramaters, shots)


def validate_and_serialize_operator(self, operator):
    if (
        not isinstance(operator, Operator)
        and not isinstance(operator, Pauli)
        and not isinstance(operator, PauliList)
        and not isinstance(operator, SparsePauliOp)
        and not isinstance(operator, LinearOp)
    ):
        raise Exception(
            "The operator must be an instance of the Operator, Pauli, PauliList or SparsePauliOp class."
        )
    return self.serialize_object(operator)


class StrafulProvider:

    _asp_net_port = "5001"
    _key_cloak_port = "8443"
    _client_id = "straful-client"
    _realm_name = "straful-realm"

    def __init__(self, *, url, use_https=True, debug=False):
        self._use_https = use_https
        self._debug = debug
        self._state = None
        self._access_token = None
        self._refresh_token = None
        self._token_expiration_time = None
        self._refresh_token_expiration_time = None
        self._provider_url = url.rstrip("/")
        self._asp_net_url = f"{self._provider_url}:{self._asp_net_port}"
        self._auth_call_back_url = f"{self._asp_net_url}/auth/callback"
        self._show_code_callback_url = f"{self._asp_net_url}/auth/showcode"
        self._keycloak_server_url = f"{self._provider_url}:{self._key_cloak_port}"

        if not self._is_server_online(self._keycloak_server_url):
            raise SystemExit(
                f"The service you are trying to access at: {url}, is not responding. \
In case the service has been recently started please wait 5 minutes for it to become fully functional."
            )

        self._keycloak_openid = KeycloakOpenID(
            server_url=self._keycloak_server_url,
            client_id=self._client_id,
            realm_name=self._realm_name,
            verify=self._use_https,
        )

    def authenticate(self):
        try:
            self._access_token = None
            self._refresh_token = None
            self._token_expiration_time = None
            self._refresh_token_expiration_time = None
            self._store_state()
            auth_url = self._get_authentication_url()
            webbrowser.open(auth_url)
            auth_code = self._get_autehntication_code()
            token_response = self._keycloak_openid.token(
                grant_type="authorization_code",
                code=auth_code,
                redirect_uri=self._auth_call_back_url,
            )
            self._access_token = token_response["access_token"]
            self._refresh_token = token_response["refresh_token"]
            self._token_expiration_time = (
                time.time() + token_response["expires_in"] - 5
            )  # seconds
            self._refresh_token_expiration_time = (
                time.time() + token_response["refresh_expires_in"] - 5
            )  # seconds
        except AuthenticationFailure as ex:
            print("Failed to authenticate with the quantum provider.")
            if self._debug:
                print("More details: ", ex.message)
        except Exception as ex:
            print("Failed to authenticate with the quantum provider.")
            if "Connection refused" in str(ex):
                print("The remote service does not respond. Please try again later.")
            if self._debug:
                print("Unexpected exception: ", ex)

    def submit_job(self, *, backend=None, circuit=None, shots=None, comments=""):
        if not self._verify_user_is_authenticated():
            return
        if not backend:
            print("Please specify the backend name.")
            return
        if not circuit:
            print("The quantum circuit is missing.")
            return
        if shots is None:
            print("Please specify the number of shots.")
            return
        if not isinstance(shots, int):
            print("The number of shots must be specified as an integer number.")
            return
        try:
            job_data = {
                "BackendName": backend,
                "Circuit": serialize_object(circuit),
                "Shots": shots,
                "Comments": comments,
            }
            (status_code, result) = self._make_post_request(
                f"{self._asp_net_url}/api/job", job_data
            )
            if status_code == 201:
                return Job(result["id"])
            else:
                print(
                    f"Job submission has failed with http status code: {status_code}. \nRemote server response: '{result}'"
                )
                return Job(None)
        except Exception as ex:
            print(str(ex))

    def submit_workflow_job(
        self,
        *,
        backend=None,
        shots=None,
        workflow_id=None,
        input_data=InputData(),
        comments="",
    ):
        if not self._verify_user_is_authenticated():
            return
        if not backend:
            print("Please specify a backend name.")
            return
        if not workflow_id:
            print("Please specify a workflow Id.")
            return
        if shots is None:
            shots = 1024
        if not isinstance(shots, int):
            print("The number of shots must be an integer.")
            return
        if not self.is_valid_uuid(workflow_id):
            print("The specified workflow Id is not valid.")
            return
        try:
            input_data_labels = []
            input_data_items = []
            input_data_labels.append("backend")
            input_data_items.append(backend)
            input_data_labels.append("shots")
            input_data_items.append(str(shots))
            for input_data_label in input_data.data.keys():
                input_data_labels.append(input_data_label)
                content = input_data.data[input_data_label]
                input_data_items.append(json.dumps(content, indent=4))
            job_data = {
                "BackendName": backend,
                "WorkflowId": workflow_id,
                "Shots": shots,
                "Comments": comments,
                "InputDataLabels": input_data_labels,
                "InputDataItems": input_data_items,
            }
            (status_code, result) = self._make_post_request(
                f"{self._asp_net_url}/api/workflow-job", job_data
            )
            if status_code == 201:
                return WorkflowJob(result["id"])
            else:
                print(
                    f"Workflow job submission has failed with http status code: {status_code}. \nRemote server response: '{result}'"
                )
                return WorkflowJob(None)
        except Exception as ex:
            print(str(ex))

    def get_backends(self):
        if not self._verify_user_is_authenticated():
            return
        try:
            response = self._make_get_request(f"{self._asp_net_url}/api/backends")
            status_code = response.status_code
            if status_code == 200:
                backends = response.json()
                for backend in backends:
                    print(
                        backend["name"],
                        "-",
                        "Online" if backend["online"] else "Offline",
                    )
            else:
                print(f"Request has failed with http status code: {status_code}.")
        except Exception as ex:
            print(str(ex))

    def get_job_status(self, job):
        if not self._verify_user_is_authenticated():
            return
        if job is None or job.id is None:
            print("This job is not valid.")
            return
        if type(job) == Job:
            try:
                response = self._make_get_request(
                    f"{self._asp_net_url}/api/job/status/{job.id()}"
                )
                status_code = response.status_code
                if status_code == 200:
                    print("Job status: ", response.text)
                else:
                    print(f"Request has failed with http status code: {status_code}.")
            except Exception as ex:
                print(str(ex))
        elif type(job) == WorkflowJob:
            try:
                response = self._make_get_request(
                    f"{self._asp_net_url}/api/workflow-job/status/{job.id()}"
                )
                status_code = response.status_code
                if status_code == 200:
                    print("Job status: ", response.text)
                else:
                    print(f"Request has failed with http status code: {status_code}.")
            except Exception as ex:
                print(str(ex))

    def get_job_result(self, job):
        if not self._verify_user_is_authenticated():
            return
        if job is None or job.id is None:
            print("This job is not valid.")
            return
        if type(job) == Job:
            try:
                response = self._make_get_request(
                    f"{self._asp_net_url}/api/job/result/{job.id()}"
                )
                status_code = response.status_code
                if status_code == 200:
                    print(response.text)
                else:
                    print(f"Request has failed with http status code: {status_code}.")
            except Exception as ex:
                print(str(ex))
        elif type(job) == WorkflowJob:
            print("Operation not supported for workflow jobs.")

    def _verify_user_is_authenticated(self):
        if (
            self._access_token is None
            or self._refresh_token is None
            or self._refresh_token_expiration_time is None
        ):
            print(
                "You are not authorized to access this service. Please try to authenticate first."
            )
            return False
        if self.is_refresh_token_expired():
            print("You session timed out, you need to re-authenticate!")
            return False
        return True

    def _make_get_request(self, api_url):
        if self.is_token_expired():
            self._try_refresh_tokens()
        return requests.get(
            api_url,
            headers={"Authorization": f"Bearer {self._access_token}"},
            verify=self._use_https,
        )

    def _make_post_request(self, api_url, data):
        if self.is_token_expired():
            self._try_refresh_tokens()
        response = requests.post(
            api_url,
            json=data,
            headers={"Authorization": f"Bearer {self._access_token}"},
            verify=self._use_https,
        )
        try:
            json = response.json()
            return (response.status_code, json)
        except:
            return (response.status_code, response.text)

    def is_token_expired(self):
        if self._token_expiration_time is None:
            return True
        return time.time() > self._token_expiration_time

    def is_refresh_token_expired(self):
        if self._refresh_token_expiration_time is None:
            return True
        return time.time() > self._refresh_token_expiration_time

    def _try_refresh_tokens(self):
        try:
            token_response = self._keycloak_openid.token(
                grant_type="refresh_token", refresh_token=self._refresh_token
            )
            self._access_token = token_response["access_token"]
            self._refresh_token = token_response["refresh_token"]
            self._token_expiration_time = (
                time.time() + token_response["expires_in"] - 5
            )  # seconds
            self._refresh_token_expiration_time = (
                time.time() + token_response["refresh_expires_in"] - 5
            )  # seconds
        except:
            pass

    def _is_server_online(self, url):
        try:
            response = requests.get(url, verify=self._use_https)
            if response.status_code == 200:
                return True
            return False
        except requests.exceptions.RequestException as e:
            return False

    def _store_state(self):
        state = str(uuid.uuid4())
        session = requests.Session()
        session_response = session.get(
            f"{self._asp_net_url}/auth/storestate",
            params={"state": state},
            verify=self._use_https,
        )
        if session_response.status_code != 200:
            if not self._is_server_online(self._asp_net_url):
                raise AuthenticationFailure(
                    f"The service you are trying to access at: {self._asp_net_url} is not responding."
                )
            else:
                raise AuthenticationFailure(
                    "Cannot initiate authentication, the authentication provider does not respond."
                )
        self._state = state

    def _get_authentication_url(self):
        auth_url_params = {
            "client_id": self._client_id,
            "redirect_uri": self._auth_call_back_url,
            "response_type": "code",
            "scope": "openid profile email",
            "kc_idp_hint": "google",
            "state": self._state,
        }
        return f"{self._keycloak_server_url}/realms/{self._realm_name}/protocol/openid-connect/auth?{urlencode(auth_url_params)}"

    def _get_autehntication_code(self):

        timeout_seconds = 300
        start_time = time.time()
        delta_t = time.time() - start_time

        while delta_t < timeout_seconds:

            if delta_t < 10:
                time.sleep(1)
            else:
                time.sleep(3)

            delta_t = time.time() - start_time

            try:
                response = requests.get(
                    self._show_code_callback_url,
                    params={"state": self._state},
                    verify=self._use_https,
                )
                if response.status_code == 400:
                    if response.text == "Authorization state is missing.":
                        raise AuthenticationFailure(
                            "Authorization state not found on remote server."
                        )
                    continue
                data = response.text
                auth_code = data.split(": ")[1]
                return auth_code
            except requests.RequestException as e:
                raise AuthenticationFailure(
                    f"Remote server is not responding to attempts to retrieve authorization code, exception is {e}."
                )

        raise AuthenticationFailure("Authorization code not received")

    def is_valid_uuid(self, value: str) -> bool:
        try:
            uuid_obj = uuid.UUID(value)
            return str(uuid_obj) == value.lower()
        except (ValueError, TypeError):
            return False
