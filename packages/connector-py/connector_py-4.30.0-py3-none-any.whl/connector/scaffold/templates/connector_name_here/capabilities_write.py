from connector.generated import (
    AssignEntitlementRequest,
    AssignEntitlementResponse,
    ActivateAccountRequest,
    ActivateAccountResponse,
    CreateAccountRequest,
    CreateAccountResponse,
    DeactivateAccountRequest,
    DeactivateAccountResponse,
    DeleteAccountRequest,
    DeleteAccountResponse,
    ListCustomAttributesSchemaRequest,
    ListCustomAttributesSchemaResponse,
    UnassignEntitlementRequest,
    UnassignEntitlementResponse,
)


async def assign_entitlement(args: AssignEntitlementRequest) -> AssignEntitlementResponse:
    raise NotImplementedError


async def unassign_entitlement(
    args: UnassignEntitlementRequest,
) -> UnassignEntitlementResponse:
    raise NotImplementedError


async def create_account(
    args: CreateAccountRequest,
) -> CreateAccountResponse:
    raise NotImplementedError


async def delete_account(
    args: DeleteAccountRequest,
) -> DeleteAccountResponse:
    raise NotImplementedError


async def activate_account(
    args: ActivateAccountRequest,
) -> ActivateAccountResponse:
    raise NotImplementedError


async def deactivate_account(
    args: DeactivateAccountRequest,
) -> DeactivateAccountResponse:
    raise NotImplementedError


async def list_custom_attributes_schema(
    args: ListCustomAttributesSchemaRequest,
) -> ListCustomAttributesSchemaResponse:
    raise NotImplementedError
