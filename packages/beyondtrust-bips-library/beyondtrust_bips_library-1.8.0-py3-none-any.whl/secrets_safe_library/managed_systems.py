"""ManagedSystems Module, all the logic to retrieve managed systems from PS API"""

import logging

from secrets_safe_library import utils
from secrets_safe_library.authentication import Authentication
from secrets_safe_library.core import APIObject


class ManagedSystem(APIObject):

    def __init__(self, authentication: Authentication, logger: logging.Logger = None):
        super().__init__(authentication, logger)

    def get_managed_systems(
        self, limit: int = None, offset: int = None, type: int = None, name: str = None
    ) -> list:
        """
        Returns a list of managed systems.

        API: GET ManagedSystems/

        Args:
            limit (int, optional): Number of records to return. (default: 100000)
            offset (int, optional): Records to skip before returning results
                                    (use with limit). (default: 0)
            type (int, optional): The entity type of the managed system.
            name (str, optional): The managed system name.

        Returns:
            list: List of managed systems.
        """

        params = {"limit": limit, "offset": offset, "type": type, "name": name}
        query_string = self.make_query_string(params)
        endpoint = f"/managedsystems?{query_string}"

        utils.print_log(
            self._logger,
            f"Calling get_managed_systems endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint, include_api_version=False)

        return response.json()

    def get_managed_system_by_id(self, managed_system_id: int) -> dict:
        """
        Find a managed system by ID.

        API: GET ManagedSystems/{id}

        Args:
            managed_system_id (int): The managed system ID.

        Returns:
            dict: Managed system object.
        """

        endpoint = f"/managedsystems/{managed_system_id}"

        utils.print_log(
            self._logger,
            f"Calling get_managed_system_by_id endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint, include_api_version=False)

        return response.json()

    def get_managed_system_by_asset_id(self, asset_id: int) -> dict:
        """
        Find a managed system by asset ID.

        API: GET Assets/{assetId}/ManagedSystems

        Args:
            assetId (int): The asset ID.

        Returns:
            dict: Managed system object.
        """

        endpoint = f"/assets/{asset_id}/managedsystems"

        utils.print_log(
            self._logger,
            f"Calling get_managed_system_by_asset_id endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint, include_api_version=False)

        return response.json()

    def get_managed_system_by_database_id(self, database_id: int) -> dict:
        """
        Find a managed system by database ID.

        API: GET Databases/{databaseID}/ManagedSystems

        Args:
            databaseID (int): The database ID.
        Returns:
            dict: Managed system object.
        """

        endpoint = f"/databases/{database_id}/managedsystems"

        utils.print_log(
            self._logger,
            f"Calling get_managed_system_by_database_id endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint, include_api_version=False)

        return response.json()

    def get_managed_system_by_functional_account_id(
        self,
        functional_account_id: int,
        limit: int = None,
        offset: int = None,
        type: int = None,
        name: str = None,
    ) -> list:
        """
        Returns a list of managed systems auto-managed by the functional
        account referenced by ID.

        API: GET FunctionalAccounts/{id}/ManagedSystems

        Args:
            id (int): The functional account ID.
            limit (int, optional): Number of records to return. (default: 100000)
            offset (int, optional): Records to skip before returning results
                                    (use with limit). (default: 0)
            type (int, optional): The entity type of the managed system.
            name (str, optional): The managed system name.

        Returns:
            list: List of managed systems by functional account id.
        """
        params = {
            "limit": limit,
            "offset": offset,
            "type": type,
            "name": name,
        }
        query_string = self.make_query_string(params)
        endpoint = (
            f"/functionalaccounts/{functional_account_id}/managedsystems?"
            f"{query_string}"
        )

        utils.print_log(
            self._logger,
            f"Calling get_managed_system_by_functional_account_id endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint, include_api_version=False)

        return response.json()

    def get_managed_system_by_workgroup_id(
        self, workgroup_id: int, limit: int = None, offset: int = None
    ) -> list:
        """
        Returns a list of managed systems by Workgroup ID.

        API: GET Workgroups/{id}/ManagedSystems

        Args:
            id (int): The workgroup ID.
            limit (int, optional): Number of records to return. (default: 100000)
            offset (int, optional): Records to skip before returning results
                                    (use with limit). (default: 0)

        Returns:
            list: List of managed systems by workgroup id.
        """

        params = {"limit": limit, "offset": offset}
        query_string = self.make_query_string(params)
        endpoint = f"/workgroups/{workgroup_id}/managedsystems?{query_string}"

        utils.print_log(
            self._logger,
            f"Calling get_managed_system_by_workgroup_id endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint, include_api_version=False)

        return response.json()
