from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests
from artd_partner.models import Partner

from artd_siigo.models import SiigoCredential, EntityImportStatus


class SiigoApiUtil:
    """
    A utility class to manage interactions with the Siigo API,
    handling authentication and requests for a specific
    partner's credentials.
    """

    def __init__(self, partner: Partner) -> None:
        """
        Initializes the SiigoUtil instance, fetching and
        setting up the Siigo credentialsfor the provided partner.

        :param partner: The partner whose Siigo credentials
        will be used.
        :raises Exception: If Siigo credentials are not found
        for the given partner.
        """
        self.__siigo_credential: SiigoCredential = SiigoCredential.objects.get(
            partner=partner
        )

        if not self.__siigo_credential:
            raise Exception("Siigo credentials not found for the specified partner")  # noqa

        self.__api_url = self.__siigo_credential.api_url
        self.__siigo_partner_id = self.__siigo_credential.siigo_partner_id

        # Set the correct username and access key based on
        # environment (sandbox or production)
        if self.__siigo_credential.is_in_sandbox:
            self.__siigo_username = self.__siigo_credential.sandbox_username  # noqa
            self.__siigo_access_key = self.__siigo_credential.sandbox_access_key  # noqa
        else:
            self.__siigo_username = self.__siigo_credential.production_username  # noqa
            self.__siigo_access_key = self.__siigo_credential.production_access_key  # noqa

        self.__headers = {
            "Content-Type": "application/json",
            "Partner-Id": self.__siigo_partner_id,
        }

    def make_a_request(
        self,
        headers: Dict[str, str],
        payload: Dict[str, Any],
        verb: str,
        url_complement: str,
    ) -> requests.Response:
        """
        Makes an HTTP request to the Siigo API using
        the specified HTTP method (verb).

        :param headers: A dictionary of headers to
        include in the request.
        :param payload: A dictionary representing
        the JSON payload for the request body.
        :param verb: The HTTP method to use. Valid options:
            "GET", "OPTIONS", "HEAD", "POST", "PUT",
            "PATCH", or "DELETE".
        :param url_complement: An optional string to append
        to the API URL.
        :return: A `requests.Response` object containing the
        server's response to the request.
        """
        url = f"{self.__api_url}{url_complement}"

        try:
            response = requests.request(
                verb,
                url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response

        except requests.exceptions.HTTPError:
            # Imprimimos el error y el cuerpo completo
            error_body = {}
            try:
                # Intentamos extraer el JSON del cuerpo
                error_body = response.json()
                return error_body
            except ValueError:
                error_body = {
                    "error": "No se pudo decodificar el cuerpo del error como JSON",
                    "raw_body": response.text,
                }
                return error_body

        except Exception:
            return None

        return None

    def is_token_expired(self, expires_in: Optional[int]) -> bool:
        """
        Checks whether the current token has expired based on the token's
        expiration time.

        :param expires_in: The expiration time of the token in seconds.
        If None, assumes the token is expired.
        :return: True if the token is expired or if no expiration
        time is provided, otherwise False.
        """
        if expires_in is None:
            return True  # Treat a missing expiration time as expired

        # Determine the expiration time by adding expires_in
        # seconds to the current time
        token_issue_time = datetime.now()
        expiration_time = token_issue_time + timedelta(seconds=expires_in)

        # Return whether the current time has passed the expiration time
        return datetime.now() > expiration_time

    def get_siigo_token(self) -> Optional[str]:
        """
        Retrieves the Siigo token from the API or the stored
        credential data. If the tokenhas expired or does not exist,
        it will request a new one.

        :return: The Siigo access token as a string, or None
        if the request fails.
        :raises Exception: If Siigo credentials are not found
        for the partner.
        """
        # Retrieve token from stored credentials or request a new one
        siigo_credential_data: dict = self.__siigo_credential.siigo_credential_data  # noqa

        # If no credentials are stored, request a new token
        if not siigo_credential_data:
            response = self.make_a_request(
                headers=self.__headers,
                payload={
                    "username": self.__siigo_username,
                    "access_key": self.__siigo_access_key,
                },
                verb="POST",
                url_complement="/auth",
            )

            if 200 <= response.status_code < 300:
                self.__siigo_credential.siigo_credential_data = response.json()
                self.__siigo_credential.save()
                return self.__siigo_credential.siigo_credential_data.get("access_token")  # noqa
        else:
            # Check if the token has expired
            expires_in = siigo_credential_data.get("expires_in")
            if self.is_token_expired(expires_in):
                # Token expired, request a new one
                response = self.make_a_request(
                    headers=self.__headers,
                    payload={
                        "username": self.__siigo_username,
                        "access_key": self.__siigo_access_key,
                    },
                    verb="POST",
                    url_complement="/auth",
                )

                if 200 <= response.status_code < 300:
                    self.__siigo_credential.siigo_credential_data = response.json()  # noqa
                    self.__siigo_credential.save()
                    return self.__siigo_credential.siigo_credential_data.get(
                        "access_token"
                    )

            # Return the existing token if it is not expired
            return siigo_credential_data.get("access_token")

        # If no token is available, raise an exception
        raise Exception("Siigo credentials not found for the specified partner")  # noqa

    def get_all_results(
        self,
        url_complement: str,
        entity_type: str | None = None,
        partner: Partner | None = None,
    ) -> list:
        """
        Retrieves all results from the paginated Siigo API endpoint
        by iterating through
        each page until no more pages are available, while avoiding
        duplicate URL requests.

        :param url_complement: The URL complement for the API
        endpoint (e.g., "/products").
        :return: A list of all items retrieved from the API.
        """
        all_results = []
        current_url = url_complement
        visited_urls = set()  # To track URLs that have been called
        headers = self.__headers
        headers["Authorization"] = f"Bearer {self.get_siigo_token()}"
        while current_url:
            # Check if the current URL has already been visited
            if current_url in visited_urls:
                print(f"Skipping already visited URL: {current_url}")
            # Add the current URL to the set of visited URLs
            visited_urls.add(current_url)
            splited_url = current_url.split("?")
            url_arguments = splited_url[1] if len(splited_url) > 1 else None
            page_number = 1
            if url_arguments:
                arguments = url_arguments.split("&")
                page_argument = arguments[0].split("=")
                if len(page_argument) > 1:
                    page_number = int(page_argument[1])

            # Make the request for the current page
            response = self.make_a_request(
                headers=headers,
                payload={},
                verb="GET",
                url_complement=current_url,
            )

            # Check if the response is successful
            if response is not None and 200 <= response.status_code < 300:
                data = response.json()
                all_results.extend(
                    data.get("results", [])
                )  # Append the results from this page

                # Check for next page link
                next_link = data.get("_links", {}).get("next", {}).get("href")
                if next_link:
                    current_url = next_link.replace(
                        self.__api_url, ""
                    )  # Only use the URL complement
                else:
                    current_url = None  # noqa

                if entity_type is not None:
                    if partner is not None:
                        if (
                            EntityImportStatus.objects.filter(
                                partner=partner,
                                siigo_entity=entity_type,
                            ).count()
                            == 0
                        ):
                            EntityImportStatus.objects.create(
                                partner=partner,
                                siigo_entity=entity_type,
                                page=1,
                                page_size=100,
                                url_complement=url_complement,
                                next_url=next_link,
                            )
                        else:
                            entity_status = EntityImportStatus.objects.get(
                                partner=partner,
                                siigo_entity=entity_type,
                            )
                            entity_status.page = page_number
                            entity_status.next_url = next_link
                            url_complement = url_complement
                            entity_status.save()
            elif response is None:
                print("Request failed, no response received.")
                break
            else:
                print(
                    f"Failed to retrieve data. Status code: {response.status_code}"  # noqa
                )  # noqa
                break

        return all_results

    def get_account_groups(self) -> list:
        """
        Retrieves the account groups from the API.

        Sends a GET request to the /v1/account-groups endpoint to fetch account groups.
        If the request is successful, the data is returned as a list. If not, an empty list is returned, and an error message is printed.

        Returns:
            list: A list of account groups if successful, otherwise an empty list.
        """
        url_complement = "/v1/account-groups"
        headers = self.__headers
        headers["Authorization"] = f"Bearer {self.get_siigo_token()}"
        response = self.make_a_request(
            headers=headers,
            payload={},
            verb="GET",
            url_complement=url_complement,
        )
        if response is not None and 200 <= response.status_code < 300:
            data = response.json()
            return data
        else:
            print(
                f"Failed to retrieve account groups. Status code: {response.status_code if response else 'No response'}"
            )
            return []

    def get_taxes(self) -> list:
        """
        Retrieves taxes from the API.

        Sends a GET request to the /v1/taxes endpoint to fetch taxes.
        If successful, the data is returned as a list. Otherwise, an empty list is returned and an error message is printed.

        Returns:
            list: A list of taxes if successful, otherwise an empty list.
        """
        url_complement = "/v1/taxes"
        headers = self.__headers
        headers["Authorization"] = f"Bearer {self.get_siigo_token()}"
        response = self.make_a_request(
            headers=headers,
            payload={},
            verb="GET",
            url_complement=url_complement,
        )
        if response is not None and 200 <= response.status_code < 300:
            data = response.json()
            return data
        else:
            print(
                f"Failed to retrieve taxes. Status code: {response.status_code if response else 'No response'}"
            )
            return []

    def get_price_lists(self) -> list:
        """
        Retrieves price lists from the API.

        Sends a GET request to the /v1/price-lists endpoint to fetch price lists.
        Returns the data as a list if successful, or an empty list if the request fails.

        Returns:
            list: A list of price lists if successful, otherwise an empty list.
        """
        url_complement = "/v1/price-lists"
        headers = self.__headers
        headers["Authorization"] = f"Bearer {self.get_siigo_token()}"
        response = self.make_a_request(
            headers=headers,
            payload={},
            verb="GET",
            url_complement=url_complement,
        )
        if response is not None and 200 <= response.status_code < 300:
            data = response.json()
            return data
        else:
            print(
                f"Failed to retrieve price lists. Status code: {response.status_code if response else 'No response'}"
            )
            return []

    def get_warehouses(self) -> list:
        """
        Retrieves warehouses from the API.

        Sends a GET request to the /v1/warehouses endpoint to fetch warehouse data.
        Returns the data as a list if the request is successful, or an empty list if it fails.

        Returns:
            list: A list of warehouses if successful, otherwise an empty list.
        """
        url_complement = "/v1/warehouses"
        headers = self.__headers
        headers["Authorization"] = f"Bearer {self.get_siigo_token()}"
        response = self.make_a_request(
            headers=headers,
            payload={},
            verb="GET",
            url_complement=url_complement,
        )
        if response is not None and 200 <= response.status_code < 300:
            data = response.json()
            return data
        else:
            print(
                f"Failed to retrieve warehouses. Status code: {response.status_code if response else 'No response'}"
            )
            return []

    def get_users(self) -> list:
        """
        Retrieves users from the API.

        Sends a GET request to the /v1/users endpoint to fetch user data.
        Returns the data as a list if successful, or an empty list if the request fails.

        Returns:
            list: A list of users if successful, otherwise an empty list.
        """
        url_complement = "/v1/users"
        headers = self.__headers
        headers["Authorization"] = f"Bearer {self.get_siigo_token()}"
        response = self.make_a_request(
            headers=headers,
            payload={},
            verb="GET",
            url_complement=url_complement,
        )
        if response is not None and 200 <= response.status_code < 300:
            data = response.json()
            return data
        else:
            print(
                f"Failed to retrieve users. Status code: {response.status_code if response else 'No response'}"
            )
            return []

    def get_document_types(self, type: str) -> list:
        """
        Retrieves document types from the API.

        Sends a GET request to the /v1/document-types endpoint to fetch document types.
        Returns the data as a list if the request is successful, or an empty list if it fails.

        Returns:
            list: A list of document types if successful, otherwise an empty list.
        """
        url_complement = f"/v1/document-types?type={type}"
        headers = self.__headers
        headers["Authorization"] = f"Bearer {self.get_siigo_token()}"
        response = self.make_a_request(
            headers=headers,
            payload={},
            verb="GET",
            url_complement=url_complement,
        )
        if response is not None and 200 <= response.status_code < 300:
            data = response.json()
            return data
        else:
            print(
                f"Failed to retrieve document types. Status code: {response.status_code if response else 'No response'}"
            )
            return []

    def get_payment_types(self, document_type: str) -> list:
        """
        Retrieves payment types from the API.

        Sends a GET request to the /v1/payment-types endpoint to fetch payment types.
        Returns the data as a list if successful, or an empty list if the request fails.

        Returns:
            list: A list of payment types if successful, otherwise an empty list.
        """
        url_complement = f"/v1/payment-types?document_type={document_type}"
        headers = self.__headers
        headers["Authorization"] = f"Bearer {self.get_siigo_token()}"
        response = self.make_a_request(
            headers=headers,
            payload={},
            verb="GET",
            url_complement=url_complement,
        )
        if response is not None and 200 <= response.status_code < 300:
            data = response.json()
            return data
        else:
            print(
                f"Failed to retrieve payment types. Status code: {response.status_code if response else 'No response'}"
            )
            return []

    def get_cost_centers(self) -> list:
        """
        Retrieves cost centers from the API.

        Sends a GET request to the /v1/cost-centers endpoint to fetch cost center data.
        Returns the data as a list if the request is successful, or an empty list if it fails.

        Returns:
            list: A list of cost centers if successful, otherwise an empty list.
        """
        url_complement = "/v1/cost-centers"
        headers = self.__headers
        headers["Authorization"] = f"Bearer {self.get_siigo_token()}"
        response = self.make_a_request(
            headers=headers,
            payload={},
            verb="GET",
            url_complement=url_complement,
        )
        if response is not None and 200 <= response.status_code < 300:
            data = response.json()
            return data
        else:
            print(
                f"Failed to retrieve cost centers. Status code: {response.status_code if response else 'No response'}"
            )
            return []

    def get_fixed_assets(self) -> list:
        """
        Retrieves fixed assets from the API.

        Sends a GET request to the /v1/fixed-assets endpoint to fetch fixed asset data.
        Returns the data as a list if successful, or an empty list if the request fails.

        Returns:
            list: A list of fixed assets if successful, otherwise an empty list.
        """
        url_complement = "/v1/fixed-assets"
        headers = self.__headers
        headers["Authorization"] = f"Bearer {self.get_siigo_token()}"
        response = self.make_a_request(
            headers=headers,
            payload={},
            verb="GET",
            url_complement=url_complement,
        )
        if response is not None and 200 <= response.status_code < 300:
            data = response.json()
            return data
        else:
            print(
                f"Failed to retrieve fixed assets. Status code: {response.status_code if response else 'No response'}"
            )
            return []

    def get_all_products(self, partner: Partner) -> list:
        """
        Retrieves all products from the API.

        Calls get_all_results() to retrieve paginated product data from the /v1/products endpoint.

        Returns:
            list: A list of all products.
        """
        url = "/v1/products?page=1&page_size=100"
        siigo_entity_type = "product"
        if (
            EntityImportStatus.objects.filter(
                partner=partner,
                siigo_entity=siigo_entity_type,
            ).count()
            > 0
        ):
            entity_import_status = EntityImportStatus.objects.filter(
                partner=partner,
                siigo_entity=siigo_entity_type,
            ).last()
            url = f"/v1/products?page={entity_import_status.page}&page_size={entity_import_status.page_size}"
        return self.get_all_results(
            url,
            siigo_entity_type,
            partner,
        )

    def create_product(self, product_data: dict) -> dict:
        """
        Creates a new product in the API.

        Sends a POST request to the /v1/products endpoint with the provided product data.
        Returns the response data if successful, or an empty dictionary if the request fails.

        Args:
            product_data (dict): The product data to be created.

        Returns:
            dict: The response data if successful, otherwise an empty dictionary.
        """
        url_complement = "/v1/products"
        headers = self.__headers
        headers["Authorization"] = f"Bearer {self.get_siigo_token()}"
        try:
            response = self.make_a_request(
                headers=headers,
                payload=product_data,
                verb="POST",
                url_complement=url_complement,
            )
            if isinstance(response, dict):
                status_code = "400"
                if "status_code" in response:
                    status_code = response["status_code"]
                message = []
                if "Errors" in response:
                    message = response["Errors"]
                return_dict = {
                    "status_code": status_code,
                    "response": message,
                }
                return return_dict
            if response is not None and 200 <= response.status_code < 300:
                data = response.json()
                return {"status_code": response.status_code, "response": data}
            else:
                if response:
                    return {
                        "status_code": response.status_code,
                        "response": response.json(),
                    }
                else:
                    return {
                        "status_code": "",
                        "response": "",
                    }
        except requests.exceptions.HTTPError:
            return {
                "status_code": response.status_code,
                "response": response.json(),
            }

        except Exception:
            return {
                "status_code": "",
                "response": "",
            }

    def get_all_customers(self, partner: Partner) -> list:
        """
        Retrieves all customers from the API.

        Calls get_all_results() to retrieve paginated customer data from the /v1/customers endpoint.

        Returns:
            list: A list of all customers.
        """
        url = "/v1/customers?page=1&page_size=100"
        siigo_entity_type = "customer"
        if (
            EntityImportStatus.objects.filter(
                partner=partner,
                siigo_entity=siigo_entity_type,
            ).count()
            > 0
        ):
            entity_import_status = EntityImportStatus.objects.filter(
                partner=partner,
                siigo_entity=siigo_entity_type,
            ).last()
            url = f"/v1/customers?page={entity_import_status.page}&page_size={entity_import_status.page_size}"
        return self.get_all_results(
            url,
            siigo_entity_type,
            partner,
        )

    def create_customer(self, customer_data: dict) -> dict:
        """
        Creates a new customer in the API.

        Sends a POST request to the /v1/customers endpoint with the provided customer data.
        Returns the response data if successful, or an empty dictionary if the request fails.

        Args:
            customer_data (dict): The customer data to be created.

        Returns:
            dict: The response data if successful, otherwise an empty dictionary.
        """
        url_complement = "/v1/customers"
        headers = self.__headers
        headers["Authorization"] = f"Bearer {self.get_siigo_token()}"
        try:
            response = self.make_a_request(
                headers=headers,
                payload=customer_data,
                verb="POST",
                url_complement=url_complement,
            )
            if isinstance(response, dict):
                status_code = "400"
                if "status_code" in response:
                    status_code = response["status_code"]
                message = []
                if "Errors" in response:
                    message = response["Errors"]
                return_dict = {
                    "status_code": status_code,
                    "response": message,
                }
                return return_dict
            if response is not None and 200 <= response.status_code < 300:
                data = response.json()
                return {"status_code": response.status_code, "response": data}
            else:
                if response:
                    return {
                        "status_code": response.status_code,
                        "response": response.json(),
                    }
                else:
                    return {
                        "status_code": "",
                        "response": "",
                    }
        except requests.exceptions.HTTPError:
            return {
                "status_code": response.status_code,
                "response": response.json(),
            }

        except Exception:
            return {
                "status_code": "",
                "response": "",
            }

    def create_invoice(self, invoice_data: dict) -> dict:
        """
        Creates a new invoice in the API.

        Sends a POST request to the /v1/invoices endpoint with the provided invoice data.
        Returns the response data if successful, or an empty dictionary if the request fails.

        Args:
            invoice_data (dict): The invoice data to be created.

        Returns:
            dict: The response data if successful, otherwise an empty dictionary.
        """
        url_complement = "/v1/invoices"
        headers = self.__headers
        headers["Authorization"] = f"Bearer {self.get_siigo_token()}"
        response = self.make_a_request(
            headers=headers,
            payload=invoice_data,
            verb="POST",
            url_complement=url_complement,
        )
        if response is not None and 200 <= response.status_code < 300:
            data = response.json()
            return data
        else:
            print(
                f"Failed to create invoice. Status code: {response.status_code if response else 'No response'}"
            )
            return {
                "status_code": response.status_code,
                "response": response.json(),
            }


def to_bool(value):
    """Converts truthy string values to actual booleans."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ["true", "1", "yes"]
    return False
