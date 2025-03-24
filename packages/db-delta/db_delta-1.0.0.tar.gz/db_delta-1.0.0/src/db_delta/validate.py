import json
import hashlib
from typing import Dict, Callable, Tuple, Any
from contextlib import contextmanager

from boto3.dynamodb.table import TableResource

from .models import (
    PutItem,
    UpdatedItem,
    DeletedItem,
    ChangeSet,
    UpdateTypeEnum,
    FieldUpdate,
)


def get_key_fields_from_table(table: TableResource) -> Tuple[str, str]:
    """Takes a DynamoDB table instance and returns
    the name of the hash and sort key"""

    key_schema = table.key_schema
    pk_name = key_schema[0]["AttributeName"]
    sk_name = key_schema[1]["AttributeName"]

    return pk_name, sk_name


def hash_key(key: Dict[str, str | int | float]) -> str:
    """Hashes a DynamoDB key by JSON encoding the key dict
    and returning its MD5 hash"""

    encoded = json.dumps(key, sort_keys=True)
    return hashlib.md5(encoded.encode()).hexdigest()


def get_table_state(table: TableResource) -> Dict[str, Dict[str, Any]]:
    """Scans a DynamoDB table and hashes all keys, returning
    all items in a map keyed on the hash of the item key."""

    items = []

    response = table.scan()
    for item in response["Items"]:
        items.append(item)

    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        for item in response["Items"]:
            items.append(item)

    # get key schema fom dynamodb table
    pk, sk = get_key_fields_from_table(table)

    state = {}
    for item in items:
        # generate item key using extracted pk and sk
        # and generate hash for key
        key = {
            pk: item[pk],
            sk: item[sk],
        }
        key_hash = hash_key(key)
        # store item against the key hash
        state[key_hash] = item

    return state


def validate_put_item(
    initial_state: Dict,
    updated_state: Dict,
    change: PutItem,
    formatter: Callable = lambda x: x,
):
    """Validates a NewItem change by ensuring that the key is in the updated
    state, but not in the initial state, and that the item matches the expected
    state."""

    # take DynamoDB key and convert into hash
    key_hash = hash_key(change.key)

    assert (
        key_hash in updated_state
    ), f"NewItem validation: Key {change.key} not found in updated table."

    assert (
        key_hash not in initial_state
    ), f"NewItem validation: Key {change.key} found in initial table."

    new_item = formatter(updated_state[key_hash])

    assert (
        new_item == change.item
    ), f"NewItem validation: Key {change.key} does not match expected state. Expected {change.item}, Actual {new_item}."  # noqa


def validate_updated_item_new_field(
    update: UpdatedItem, field: FieldUpdate, initial_item: Dict, updated_item: Dict
):
    # check that the field is not already in the item
    assert (
        field.field not in initial_item
    ), f"UpdateItem validation: Field '{field.field}' for key {update.key} has been added, but already exists."  # noqa

    assert (
        field.field in updated_item
    ), f"UpdateItem validation: Field '{field.field}' for key {update.key} has been added, but not found in updated item."  # noqa

    assert (
        field.new_value == updated_item[field.field]
    ), f"UpdateItem validation: Field '{field.field}' for key {update.key} has been added, but does not match expected value."  # noqa


def validate_updated_item_updated_field(
    update: UpdatedItem, field: FieldUpdate, initial_item: Dict, updated_item: Dict
):
    # check that the field is not already in the item
    assert (
        field.field in initial_item
    ), f"UpdateItem validation: Field '{field.field}' for key {update.key} has been updated, but not found in initial item."  # noqa

    assert (
        field.field in updated_item
    ), f"UpdateItem validation: Field '{field.field}' for key {update.key} has been updated, but not found in updated item."  # noqa

    assert (
        field.new_value == updated_item[field.field]
    ), f"UpdateItem validation: Field '{field.field}' for key {update.key} has been updated, but does not match expected value. Expected '{field.new_value}', got '{updated_item[field.field]}'."  # noqa


def validate_updated_item_removed_field(
    update: UpdatedItem, field: FieldUpdate, initial_item: Dict, updated_item: Dict
):

    assert (
        field.field in initial_item
    ), f"UpdateItem validation: Field '{field.field}' for key {update.key} has been removed, but not found in initial item."  # noqa

    assert (
        field.field not in updated_item
    ), f"UpdateItem validation: Field '{field.field}' for key {update.key} has been removed, but found in updated item."  # noqa


def validate_updated_item(
    initial_state: Dict,
    updated_state: Dict,
    change: UpdatedItem,
    formatter: Callable = lambda x: x,
):
    """Validates a UpdatedItem change by ensuring that the key is in both
    the initial and updated states, and that the changed fields match the
    expected values."""

    key_hash = hash_key(change.key)

    assert (
        key_hash in updated_state
    ), f"UpdatedItem validation: Key {change.key} not found in updated table."

    assert (
        key_hash in initial_state
    ), f"UpdatedItem validation: Key {change.key} not found in initial table."

    updated_item = formatter(updated_state[key_hash])
    initial_item = formatter(initial_state[key_hash])

    for field in change.updated_fields:
        if field.update_type == UpdateTypeEnum.ADDED:
            validate_updated_item_new_field(
                change,
                field,
                initial_item,
                updated_item,
            )

        elif field.update_type == UpdateTypeEnum.UPDATED:
            validate_updated_item_updated_field(
                change, field, initial_item, updated_item
            )

        elif field.update_type == UpdateTypeEnum.REMOVED:
            validate_updated_item_removed_field(
                change, field, initial_item, updated_item
            )

    changed_fields = {field.field for field in change.updated_fields}
    for key in initial_item:
        if key in changed_fields:
            continue

        assert (
            key in updated_item
        ), f"UpdatedItem validation: Field '{key}' for key {change.key} not found in updated item."  # noqa

        assert (
            initial_item[key] == updated_item[key]
        ), f"UpdatedItem validation: Field '{key}' for key {change.key} has been modified. Expected: {initial_item[key]}, Actual: {updated_item[key]}."  # noqa


def validate_deleted_item(
    initial_state: Dict,
    updated_state: Dict,
    change: DeletedItem,
):
    """Validates that a DeletedItem change is accurate by ensuring
    that the key is in the initial state, but not in the updated state."""

    key_hash = hash_key(change.key)

    assert (
        key_hash in initial_state
    ), f"DeletedItem validation: Key {change.key} not found in initial table."

    assert (
        key_hash not in updated_state
    ), f"DeletedItem validation: Key {change.key} found in updated table."  # noqa


def validate_unchanged_items(
    table: TableResource,
    initial_state: Dict[str, Dict[str, Any]],
    updated_state: Dict[str, Dict[str, Any]],
    changeset: ChangeSet,
):

    # get key schema fom dynamodb table
    pk, sk = get_key_fields_from_table(table)
    changed_keys = [hash_key(item.key) for item in changeset.changes]

    # get a list of key hashes for items that are in the initial state
    # but not defined in the changeset. These items should not have changed
    # and should be the same in both states
    unchanged_keys = set(initial_state.keys()) - set(changed_keys)
    for key_hash in unchanged_keys:
        # get item from state using hash and generate
        # unhashed key for logging (if required)
        item = initial_state[key_hash]
        unhashed_key = {
            pk: item[pk],
            sk: item[sk],
        }

        # check that item is present in updated table state
        assert (
            key_hash in updated_state
        ), f"Expected key {unhashed_key} not found in updated table."

        initial_item = initial_state[key_hash]
        updated_item = updated_state[key_hash]

        # check that the item has not been modified
        assert (
            initial_item == updated_item
        ), f"Item {unhashed_key} found in updated table, but has been modified. Expected: {initial_item}, Actual: {updated_item}."  # noqa


def validate_new_items(
    table: TableResource,
    initial_state: Dict[str, Dict[str, Any]],
    updated_state: Dict[str, Dict[str, Any]],
    changeset: ChangeSet,
):
    # get key schema fom dynamodb table and get a list of key hashes
    # that are defined in the changeset
    pk, sk = get_key_fields_from_table(table)
    changed_keys = [hash_key(item.key) for item in changeset.changes]

    # get a list of key hashes for items that are present in the
    # new table state but not in the old table state
    new_keys = set(updated_state.keys()) - set(initial_state.keys())
    for key_hash in new_keys:
        # get item from state using hash and generate
        # unhashed key for logging (if required)
        item = updated_state[key_hash]
        unhashed_key = {
            pk: item[pk],
            sk: item[sk],
        }

        # assert that the new key is defined in the changeset
        assert (
            key_hash in changed_keys
        ), f"New item {unhashed_key} found in updated table, but not in expected changeset."  # noqa


@contextmanager
def validate_dynamodb_changeset(
    table: TableResource,
    expected_changeset: ChangeSet,
    formatter: Callable = lambda x: x,
):
    """Validates a provided changeset against a DynamoDB table.
    The initial state of the table is exported using a Scan
    operation, and the final state is exported after the context.
    The changeset is then validated against the initial and final
    states to ensure that the changeset is accurate."""

    initial_state = get_table_state(table)

    yield

    updated_state = get_table_state(table)

    # ensure that all items that are NOT present in changeset have remained
    # unchanged
    validate_unchanged_items(
        table,
        initial_state,
        updated_state,
        expected_changeset,
    )

    # ensure that no new items have been created that are not present
    # in the changeset
    validate_new_items(table, initial_state, updated_state, expected_changeset)

    for change in expected_changeset.changes:
        if isinstance(change, PutItem):
            # check that the key is in the updated table
            validate_put_item(
                initial_state,
                updated_state,
                change,
                formatter,
            )

        elif isinstance(change, UpdatedItem):
            validate_updated_item(
                initial_state,
                updated_state,
                change,
                formatter,
            )

        elif isinstance(change, DeletedItem):
            validate_deleted_item(initial_state, updated_state, change)

        else:
            raise ValueError("Invalid change type")
