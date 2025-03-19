# import notebookutils.runtime # Importing this module inside a notebook from this library will not resolve to correct module
import notebookutils.credentials
import notebookutils.lakehouse
import notebookutils.notebook


class Lakehouse:

    def by_name(self, lakehouse_name: str) -> dict:
        found_lakehouse = notebookutils.lakehouse.get(
            lakehouse_name, Runtime().current_workspace_id()
        )

        if found_lakehouse == None:
            raise Exception(
                f"Lakehouse with name {lakehouse_name} not found in the current workspace"
            )

        return {
            "uid": found_lakehouse.id,
            "abfsPath": found_lakehouse.properties["abfsPath"],
            "displayName": found_lakehouse.displayName,
            "workspaceId": found_lakehouse.workspaceId,
            "description": found_lakehouse.description,
        }


class Runtime:

    def current_workspace_id(self) -> str:
        # notebookutils.runtime is not available in the current version of the SDK but works in notebooks
        current_workspace_id = notebookutils.runtime.getCurrentWorkspaceId()

        if current_workspace_id == None:
            raise Exception(
                "Workspace ID not found. Please ensure you are running this code in an Azure Synapse Notebook."
            )
        return current_workspace_id

    def current_workspace_name(self) -> str:
        # notebookutils.runtime is not available in the current version of the SDK but works in notebooks
        current_workspace_name = notebookutils.runtime.context["currentWorkspaceName"]

        if current_workspace_name == None:
            raise Exception(
                "Workspace Name not found. Please ensure you are running this code in an Azure Synapse Notebook."
            )
        return current_workspace_name

    def current_notebook_name(self) -> str:
        # notebookutils.runtime is not available in the current version of the SDK but works in notebooks
        current_notebook_name = notebookutils.runtime.context["currentNotebookName"]

        if current_notebook_name == None:
            raise Exception(
                "Notebook Name not found. Please ensure you are running this code in an Azure Synapse Notebook."
            )
        return current_notebook_name

    def current_notebook_id(self) -> str:
        # notebookutils.runtime is not available in the current version of the SDK but works in notebooks
        current_notebook_id = notebookutils.runtime.context["currentNotebookId"]

        if current_notebook_id == None:
            raise Exception(
                "Notebook Name not found. Please ensure you are running this code in an Azure Synapse Notebook."
            )
        return current_notebook_id


class Util:
    def dump(self, obj: object) -> None:
        for attr in dir(obj):
            print("obj.%s = %r" % (attr, getattr(obj, attr)))

    def get_secret_from_keyvault(self, keyvault_name: str, secret_name: str) -> str:
        foundSecret = notebookutils.credentials.getSecret(keyvault_name, secret_name)

        if foundSecret == None:
            raise Exception(
                f"Secret with name {secret_name} not found in the keyvault {keyvault_name}"
            )

        return foundSecret
