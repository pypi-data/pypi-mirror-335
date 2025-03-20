# Third Party Libraries
import click

# Gitlab-Project-Configurator Modules
from gpc.helpers.error_codes import GPC_CREATE_ERROR
from gpc.helpers.error_codes import GPC_DELETE_ERROR
from gpc.helpers.error_codes import GPC_DUPLICATE_KEY_ERROR
from gpc.helpers.error_codes import GPC_ERR_CODE_PROJECT_FAILURE
from gpc.helpers.error_codes import GPC_ERR_LABEL
from gpc.helpers.error_codes import GPC_ERR_MEMBER
from gpc.helpers.error_codes import GPC_ERR_PROFILE_NO_EXIST
from gpc.helpers.error_codes import GPC_ERR_PROPERTY
from gpc.helpers.error_codes import GPC_ERR_SCHEMA_ERROR
from gpc.helpers.error_codes import GPC_ERR_VALIDATION_ERROR
from gpc.helpers.error_codes import GPC_ERR_VARIABLES
from gpc.helpers.error_codes import GPC_ERROR_CODE_FAILURE
from gpc.helpers.error_codes import GPC_IMPOSSIBLE_CONF
from gpc.helpers.error_codes import GPC_PROTECTED_BRANCHES_ERROR
from gpc.helpers.error_codes import GPC_PROTECTED_TAGS_ERROR
from gpc.helpers.error_codes import GPC_USER_ERR


class GpcError(Exception):
    error_code = GPC_ERROR_CODE_FAILURE

    def __init__(self, inner_exception, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._inner_exception = inner_exception

    def __str__(self):
        return str(self._inner_exception)

    def echo(self):
        click.secho(f"ERROR: {str(self)}", fg="red")


class GpcPermissionError(GpcError):
    error_code = GPC_ERR_CODE_PROJECT_FAILURE


class GpcExecutorNotFound(GpcError):
    error_code = GPC_ERR_PROPERTY


class GPCCreateError(GpcError):
    error_code = GPC_CREATE_ERROR

    def __init__(self, inner_exception, original_response_code, *args, **kwargs):
        super().__init__(inner_exception, *args, **kwargs)
        self.original_response_code = original_response_code


class GPCDeleteError(GpcError):
    error_code = GPC_DELETE_ERROR


class GpcProfileError(GpcError):
    error_code = GPC_ERR_PROFILE_NO_EXIST


class GpcVariableError(GpcError):
    error_code = GPC_ERR_VARIABLES


class GpcMemberError(GpcError):
    error_code = GPC_ERR_MEMBER


class GpcUserError(GpcError):
    error_code = GPC_USER_ERR


class GpcProtectedBranchesError(GpcError):
    error_code = GPC_PROTECTED_BRANCHES_ERROR


class GpcProtectedTagsError(GpcError):
    error_code = GPC_PROTECTED_TAGS_ERROR


class GpcLabelError(GpcError):
    error_code = GPC_ERR_LABEL


class GpcImpossibleConf(GpcError):
    error_code = GPC_IMPOSSIBLE_CONF


class GpcValidationError(GpcError):
    """
    Configuration file does not match schema.
    """

    error_code = GPC_ERR_VALIDATION_ERROR

    def __init__(self, config_file: str, schema_file: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_file = config_file
        self.schema_file = schema_file

    def __str__(self):
        return (
            f"Validation error of {self.config_file} against schema {self.schema_file}:\n\n"
            f"Error: {str(self._inner_exception)}"
        )


class GpcSchemaError(GpcError):
    """
    Error in Schema.
    """

    error_code = GPC_ERR_SCHEMA_ERROR

    def __init__(self, schema_file: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema_file = schema_file

    def __str__(self):
        return f"Error in schema {self.schema_file}\n\nCause: {self._inner_exception}"


class GpcDuplicateKey(Exception):
    error_code = GPC_DUPLICATE_KEY_ERROR

    def __init__(self, schema_file: str, duplicates: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = schema_file
        self.duplicates = duplicates

    def __str__(self):
        msg = f"\nError in schema {self.schema}\n"
        for k, v in self.duplicates.items():
            msg += f"'{k}' appears {v} times in your configuration file\n"
        return msg
