# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import sys
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict, TypeAlias
else:
    from typing_extensions import NotRequired, TypedDict, TypeAlias
from . import _utilities
from . import outputs
from ._inputs import *

__all__ = ['SchemaRegistryKekArgs', 'SchemaRegistryKek']

@pulumi.input_type
class SchemaRegistryKekArgs:
    def __init__(__self__, *,
                 kms_key_id: pulumi.Input[str],
                 kms_type: pulumi.Input[str],
                 credentials: Optional[pulumi.Input['SchemaRegistryKekCredentialsArgs']] = None,
                 doc: Optional[pulumi.Input[str]] = None,
                 hard_delete: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 properties: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 rest_endpoint: Optional[pulumi.Input[str]] = None,
                 schema_registry_cluster: Optional[pulumi.Input['SchemaRegistryKekSchemaRegistryClusterArgs']] = None,
                 shared: Optional[pulumi.Input[bool]] = None):
        """
        The set of arguments for constructing a SchemaRegistryKek resource.
        :param pulumi.Input[str] kms_key_id: The ID of the key from KMS. 
               - When using the AWS KMS, this is an ARN, for example, `arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789abc`.
               - When using the Azure Key Vault, this is a Key Identifier (URI), for example, `https://test-keyvault1.vault.azure.net/keys/test-key1/1234567890abcdef1234567890abcdef`.
               - When using the GCP KMS, this is a resource name, for example, `projects/test-project1/locations/us-central1/keyRings/test-keyRing1/cryptoKeys/test-key1`.
        :param pulumi.Input[str] kms_type: The type of Key Management Service (KMS). The supported values include `aws-kms`, `azure-kms`, and `gcp-kms`. Additionally, custom KMS types are supported as well.
        :param pulumi.Input['SchemaRegistryKekCredentialsArgs'] credentials: The Cluster API Credentials.
        :param pulumi.Input[str] doc: The optional description for the KEK.
        :param pulumi.Input[bool] hard_delete: Controls whether a kek should be soft or hard deleted. Set it to `true` if you want to hard delete a schema registry kek
               on destroy. Defaults to `false` (soft delete).
        :param pulumi.Input[str] name: The name for the KEK.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] properties: The custom properties to set (for example, `KeyUsage=ENCRYPT_DECRYPT`, `KeyState=Enabled`):
        :param pulumi.Input[str] rest_endpoint: The REST endpoint of the Schema Registry cluster, for example, `https://psrc-00000.us-central1.gcp.confluent.cloud:443`).
        :param pulumi.Input[bool] shared: The optional flag to control whether the DEK Registry has shared access to the KMS. Defaults to `false`.
        """
        pulumi.set(__self__, "kms_key_id", kms_key_id)
        pulumi.set(__self__, "kms_type", kms_type)
        if credentials is not None:
            pulumi.set(__self__, "credentials", credentials)
        if doc is not None:
            pulumi.set(__self__, "doc", doc)
        if hard_delete is not None:
            pulumi.set(__self__, "hard_delete", hard_delete)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if properties is not None:
            pulumi.set(__self__, "properties", properties)
        if rest_endpoint is not None:
            pulumi.set(__self__, "rest_endpoint", rest_endpoint)
        if schema_registry_cluster is not None:
            pulumi.set(__self__, "schema_registry_cluster", schema_registry_cluster)
        if shared is not None:
            pulumi.set(__self__, "shared", shared)

    @property
    @pulumi.getter(name="kmsKeyId")
    def kms_key_id(self) -> pulumi.Input[str]:
        """
        The ID of the key from KMS. 
        - When using the AWS KMS, this is an ARN, for example, `arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789abc`.
        - When using the Azure Key Vault, this is a Key Identifier (URI), for example, `https://test-keyvault1.vault.azure.net/keys/test-key1/1234567890abcdef1234567890abcdef`.
        - When using the GCP KMS, this is a resource name, for example, `projects/test-project1/locations/us-central1/keyRings/test-keyRing1/cryptoKeys/test-key1`.
        """
        return pulumi.get(self, "kms_key_id")

    @kms_key_id.setter
    def kms_key_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "kms_key_id", value)

    @property
    @pulumi.getter(name="kmsType")
    def kms_type(self) -> pulumi.Input[str]:
        """
        The type of Key Management Service (KMS). The supported values include `aws-kms`, `azure-kms`, and `gcp-kms`. Additionally, custom KMS types are supported as well.
        """
        return pulumi.get(self, "kms_type")

    @kms_type.setter
    def kms_type(self, value: pulumi.Input[str]):
        pulumi.set(self, "kms_type", value)

    @property
    @pulumi.getter
    def credentials(self) -> Optional[pulumi.Input['SchemaRegistryKekCredentialsArgs']]:
        """
        The Cluster API Credentials.
        """
        return pulumi.get(self, "credentials")

    @credentials.setter
    def credentials(self, value: Optional[pulumi.Input['SchemaRegistryKekCredentialsArgs']]):
        pulumi.set(self, "credentials", value)

    @property
    @pulumi.getter
    def doc(self) -> Optional[pulumi.Input[str]]:
        """
        The optional description for the KEK.
        """
        return pulumi.get(self, "doc")

    @doc.setter
    def doc(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "doc", value)

    @property
    @pulumi.getter(name="hardDelete")
    def hard_delete(self) -> Optional[pulumi.Input[bool]]:
        """
        Controls whether a kek should be soft or hard deleted. Set it to `true` if you want to hard delete a schema registry kek
        on destroy. Defaults to `false` (soft delete).
        """
        return pulumi.get(self, "hard_delete")

    @hard_delete.setter
    def hard_delete(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "hard_delete", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name for the KEK.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def properties(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        The custom properties to set (for example, `KeyUsage=ENCRYPT_DECRYPT`, `KeyState=Enabled`):
        """
        return pulumi.get(self, "properties")

    @properties.setter
    def properties(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "properties", value)

    @property
    @pulumi.getter(name="restEndpoint")
    def rest_endpoint(self) -> Optional[pulumi.Input[str]]:
        """
        The REST endpoint of the Schema Registry cluster, for example, `https://psrc-00000.us-central1.gcp.confluent.cloud:443`).
        """
        return pulumi.get(self, "rest_endpoint")

    @rest_endpoint.setter
    def rest_endpoint(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "rest_endpoint", value)

    @property
    @pulumi.getter(name="schemaRegistryCluster")
    def schema_registry_cluster(self) -> Optional[pulumi.Input['SchemaRegistryKekSchemaRegistryClusterArgs']]:
        return pulumi.get(self, "schema_registry_cluster")

    @schema_registry_cluster.setter
    def schema_registry_cluster(self, value: Optional[pulumi.Input['SchemaRegistryKekSchemaRegistryClusterArgs']]):
        pulumi.set(self, "schema_registry_cluster", value)

    @property
    @pulumi.getter
    def shared(self) -> Optional[pulumi.Input[bool]]:
        """
        The optional flag to control whether the DEK Registry has shared access to the KMS. Defaults to `false`.
        """
        return pulumi.get(self, "shared")

    @shared.setter
    def shared(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "shared", value)


@pulumi.input_type
class _SchemaRegistryKekState:
    def __init__(__self__, *,
                 credentials: Optional[pulumi.Input['SchemaRegistryKekCredentialsArgs']] = None,
                 doc: Optional[pulumi.Input[str]] = None,
                 hard_delete: Optional[pulumi.Input[bool]] = None,
                 kms_key_id: Optional[pulumi.Input[str]] = None,
                 kms_type: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 properties: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 rest_endpoint: Optional[pulumi.Input[str]] = None,
                 schema_registry_cluster: Optional[pulumi.Input['SchemaRegistryKekSchemaRegistryClusterArgs']] = None,
                 shared: Optional[pulumi.Input[bool]] = None):
        """
        Input properties used for looking up and filtering SchemaRegistryKek resources.
        :param pulumi.Input['SchemaRegistryKekCredentialsArgs'] credentials: The Cluster API Credentials.
        :param pulumi.Input[str] doc: The optional description for the KEK.
        :param pulumi.Input[bool] hard_delete: Controls whether a kek should be soft or hard deleted. Set it to `true` if you want to hard delete a schema registry kek
               on destroy. Defaults to `false` (soft delete).
        :param pulumi.Input[str] kms_key_id: The ID of the key from KMS. 
               - When using the AWS KMS, this is an ARN, for example, `arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789abc`.
               - When using the Azure Key Vault, this is a Key Identifier (URI), for example, `https://test-keyvault1.vault.azure.net/keys/test-key1/1234567890abcdef1234567890abcdef`.
               - When using the GCP KMS, this is a resource name, for example, `projects/test-project1/locations/us-central1/keyRings/test-keyRing1/cryptoKeys/test-key1`.
        :param pulumi.Input[str] kms_type: The type of Key Management Service (KMS). The supported values include `aws-kms`, `azure-kms`, and `gcp-kms`. Additionally, custom KMS types are supported as well.
        :param pulumi.Input[str] name: The name for the KEK.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] properties: The custom properties to set (for example, `KeyUsage=ENCRYPT_DECRYPT`, `KeyState=Enabled`):
        :param pulumi.Input[str] rest_endpoint: The REST endpoint of the Schema Registry cluster, for example, `https://psrc-00000.us-central1.gcp.confluent.cloud:443`).
        :param pulumi.Input[bool] shared: The optional flag to control whether the DEK Registry has shared access to the KMS. Defaults to `false`.
        """
        if credentials is not None:
            pulumi.set(__self__, "credentials", credentials)
        if doc is not None:
            pulumi.set(__self__, "doc", doc)
        if hard_delete is not None:
            pulumi.set(__self__, "hard_delete", hard_delete)
        if kms_key_id is not None:
            pulumi.set(__self__, "kms_key_id", kms_key_id)
        if kms_type is not None:
            pulumi.set(__self__, "kms_type", kms_type)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if properties is not None:
            pulumi.set(__self__, "properties", properties)
        if rest_endpoint is not None:
            pulumi.set(__self__, "rest_endpoint", rest_endpoint)
        if schema_registry_cluster is not None:
            pulumi.set(__self__, "schema_registry_cluster", schema_registry_cluster)
        if shared is not None:
            pulumi.set(__self__, "shared", shared)

    @property
    @pulumi.getter
    def credentials(self) -> Optional[pulumi.Input['SchemaRegistryKekCredentialsArgs']]:
        """
        The Cluster API Credentials.
        """
        return pulumi.get(self, "credentials")

    @credentials.setter
    def credentials(self, value: Optional[pulumi.Input['SchemaRegistryKekCredentialsArgs']]):
        pulumi.set(self, "credentials", value)

    @property
    @pulumi.getter
    def doc(self) -> Optional[pulumi.Input[str]]:
        """
        The optional description for the KEK.
        """
        return pulumi.get(self, "doc")

    @doc.setter
    def doc(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "doc", value)

    @property
    @pulumi.getter(name="hardDelete")
    def hard_delete(self) -> Optional[pulumi.Input[bool]]:
        """
        Controls whether a kek should be soft or hard deleted. Set it to `true` if you want to hard delete a schema registry kek
        on destroy. Defaults to `false` (soft delete).
        """
        return pulumi.get(self, "hard_delete")

    @hard_delete.setter
    def hard_delete(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "hard_delete", value)

    @property
    @pulumi.getter(name="kmsKeyId")
    def kms_key_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the key from KMS. 
        - When using the AWS KMS, this is an ARN, for example, `arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789abc`.
        - When using the Azure Key Vault, this is a Key Identifier (URI), for example, `https://test-keyvault1.vault.azure.net/keys/test-key1/1234567890abcdef1234567890abcdef`.
        - When using the GCP KMS, this is a resource name, for example, `projects/test-project1/locations/us-central1/keyRings/test-keyRing1/cryptoKeys/test-key1`.
        """
        return pulumi.get(self, "kms_key_id")

    @kms_key_id.setter
    def kms_key_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kms_key_id", value)

    @property
    @pulumi.getter(name="kmsType")
    def kms_type(self) -> Optional[pulumi.Input[str]]:
        """
        The type of Key Management Service (KMS). The supported values include `aws-kms`, `azure-kms`, and `gcp-kms`. Additionally, custom KMS types are supported as well.
        """
        return pulumi.get(self, "kms_type")

    @kms_type.setter
    def kms_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kms_type", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name for the KEK.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def properties(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        The custom properties to set (for example, `KeyUsage=ENCRYPT_DECRYPT`, `KeyState=Enabled`):
        """
        return pulumi.get(self, "properties")

    @properties.setter
    def properties(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "properties", value)

    @property
    @pulumi.getter(name="restEndpoint")
    def rest_endpoint(self) -> Optional[pulumi.Input[str]]:
        """
        The REST endpoint of the Schema Registry cluster, for example, `https://psrc-00000.us-central1.gcp.confluent.cloud:443`).
        """
        return pulumi.get(self, "rest_endpoint")

    @rest_endpoint.setter
    def rest_endpoint(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "rest_endpoint", value)

    @property
    @pulumi.getter(name="schemaRegistryCluster")
    def schema_registry_cluster(self) -> Optional[pulumi.Input['SchemaRegistryKekSchemaRegistryClusterArgs']]:
        return pulumi.get(self, "schema_registry_cluster")

    @schema_registry_cluster.setter
    def schema_registry_cluster(self, value: Optional[pulumi.Input['SchemaRegistryKekSchemaRegistryClusterArgs']]):
        pulumi.set(self, "schema_registry_cluster", value)

    @property
    @pulumi.getter
    def shared(self) -> Optional[pulumi.Input[bool]]:
        """
        The optional flag to control whether the DEK Registry has shared access to the KMS. Defaults to `false`.
        """
        return pulumi.get(self, "shared")

    @shared.setter
    def shared(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "shared", value)


class SchemaRegistryKek(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 credentials: Optional[pulumi.Input[Union['SchemaRegistryKekCredentialsArgs', 'SchemaRegistryKekCredentialsArgsDict']]] = None,
                 doc: Optional[pulumi.Input[str]] = None,
                 hard_delete: Optional[pulumi.Input[bool]] = None,
                 kms_key_id: Optional[pulumi.Input[str]] = None,
                 kms_type: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 properties: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 rest_endpoint: Optional[pulumi.Input[str]] = None,
                 schema_registry_cluster: Optional[pulumi.Input[Union['SchemaRegistryKekSchemaRegistryClusterArgs', 'SchemaRegistryKekSchemaRegistryClusterArgsDict']]] = None,
                 shared: Optional[pulumi.Input[bool]] = None,
                 __props__=None):
        """
        [![General Availability](https://img.shields.io/badge/Lifecycle%20Stage-General%20Availability-%2345c6e8)](https://docs.confluent.io/cloud/current/api.html#section/Versioning/API-Lifecycle-Policy)

        `SchemaRegistryKek` provides a Schema Registry Key Encryption Key (KEK) resource that enables creating, editing, and deleting Schema Registry Key Encryption Keys on Confluent Cloud.

        ## Example Usage

        ### Option #1: Manage multiple Schema Registry clusters in the same Pulumi Stack

        ```python
        import pulumi
        import pulumi_confluentcloud as confluentcloud

        aws_key = confluentcloud.SchemaRegistryKek("aws_key",
            schema_registry_cluster={
                "id": essentials["id"],
            },
            rest_endpoint=essentials["restEndpoint"],
            credentials={
                "key": "<Schema Registry API Key for data.confluent_schema_registry_cluster.essentials>",
                "secret": "<Schema Registry API Secret for data.confluent_schema_registry_cluster.essentials>",
            },
            name="my_key",
            kms_type="aws-kms",
            kms_key_id="key_id",
            doc="test key",
            shared=False,
            hard_delete=True)
        ```

        ### Option #2: Manage a single Schema Registry cluster in the same Pulumi Stack

        ```python
        import pulumi
        import pulumi_confluentcloud as confluentcloud

        pii = confluentcloud.SchemaRegistryKek("pii",
            name="my_key",
            kms_type="aws-kms",
            kms_key_id="key_id",
            doc="test key",
            shared=False,
            hard_delete=True)
        ```

        ## Getting Started

        The following end-to-end example might help to get started with field-level encryption:
          * field-level-encryption-schema

        ## Import

        You can import a Schema Registry Key by using the Schema Registry cluster ID, Kek name in the format `<Schema Registry cluster ID>/<Kek name>`, for example:

        $ export IMPORT_SCHEMA_REGISTRY_API_KEY="<schema_registry_api_key>"

        $ export IMPORT_SCHEMA_REGISTRY_API_SECRET="<schema_registry_api_secret>"

        $ export IMPORT_SCHEMA_REGISTRY_REST_ENDPOINT="<schema_registry_rest_endpoint>"

        ```sh
        $ pulumi import confluentcloud:index/schemaRegistryKek:SchemaRegistryKek aws_key lsrc-8wrx70/aws_key
        ```

        !> **Warning:** Do not forget to delete terminal command history afterwards for security purposes.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Union['SchemaRegistryKekCredentialsArgs', 'SchemaRegistryKekCredentialsArgsDict']] credentials: The Cluster API Credentials.
        :param pulumi.Input[str] doc: The optional description for the KEK.
        :param pulumi.Input[bool] hard_delete: Controls whether a kek should be soft or hard deleted. Set it to `true` if you want to hard delete a schema registry kek
               on destroy. Defaults to `false` (soft delete).
        :param pulumi.Input[str] kms_key_id: The ID of the key from KMS. 
               - When using the AWS KMS, this is an ARN, for example, `arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789abc`.
               - When using the Azure Key Vault, this is a Key Identifier (URI), for example, `https://test-keyvault1.vault.azure.net/keys/test-key1/1234567890abcdef1234567890abcdef`.
               - When using the GCP KMS, this is a resource name, for example, `projects/test-project1/locations/us-central1/keyRings/test-keyRing1/cryptoKeys/test-key1`.
        :param pulumi.Input[str] kms_type: The type of Key Management Service (KMS). The supported values include `aws-kms`, `azure-kms`, and `gcp-kms`. Additionally, custom KMS types are supported as well.
        :param pulumi.Input[str] name: The name for the KEK.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] properties: The custom properties to set (for example, `KeyUsage=ENCRYPT_DECRYPT`, `KeyState=Enabled`):
        :param pulumi.Input[str] rest_endpoint: The REST endpoint of the Schema Registry cluster, for example, `https://psrc-00000.us-central1.gcp.confluent.cloud:443`).
        :param pulumi.Input[bool] shared: The optional flag to control whether the DEK Registry has shared access to the KMS. Defaults to `false`.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: SchemaRegistryKekArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        [![General Availability](https://img.shields.io/badge/Lifecycle%20Stage-General%20Availability-%2345c6e8)](https://docs.confluent.io/cloud/current/api.html#section/Versioning/API-Lifecycle-Policy)

        `SchemaRegistryKek` provides a Schema Registry Key Encryption Key (KEK) resource that enables creating, editing, and deleting Schema Registry Key Encryption Keys on Confluent Cloud.

        ## Example Usage

        ### Option #1: Manage multiple Schema Registry clusters in the same Pulumi Stack

        ```python
        import pulumi
        import pulumi_confluentcloud as confluentcloud

        aws_key = confluentcloud.SchemaRegistryKek("aws_key",
            schema_registry_cluster={
                "id": essentials["id"],
            },
            rest_endpoint=essentials["restEndpoint"],
            credentials={
                "key": "<Schema Registry API Key for data.confluent_schema_registry_cluster.essentials>",
                "secret": "<Schema Registry API Secret for data.confluent_schema_registry_cluster.essentials>",
            },
            name="my_key",
            kms_type="aws-kms",
            kms_key_id="key_id",
            doc="test key",
            shared=False,
            hard_delete=True)
        ```

        ### Option #2: Manage a single Schema Registry cluster in the same Pulumi Stack

        ```python
        import pulumi
        import pulumi_confluentcloud as confluentcloud

        pii = confluentcloud.SchemaRegistryKek("pii",
            name="my_key",
            kms_type="aws-kms",
            kms_key_id="key_id",
            doc="test key",
            shared=False,
            hard_delete=True)
        ```

        ## Getting Started

        The following end-to-end example might help to get started with field-level encryption:
          * field-level-encryption-schema

        ## Import

        You can import a Schema Registry Key by using the Schema Registry cluster ID, Kek name in the format `<Schema Registry cluster ID>/<Kek name>`, for example:

        $ export IMPORT_SCHEMA_REGISTRY_API_KEY="<schema_registry_api_key>"

        $ export IMPORT_SCHEMA_REGISTRY_API_SECRET="<schema_registry_api_secret>"

        $ export IMPORT_SCHEMA_REGISTRY_REST_ENDPOINT="<schema_registry_rest_endpoint>"

        ```sh
        $ pulumi import confluentcloud:index/schemaRegistryKek:SchemaRegistryKek aws_key lsrc-8wrx70/aws_key
        ```

        !> **Warning:** Do not forget to delete terminal command history afterwards for security purposes.

        :param str resource_name: The name of the resource.
        :param SchemaRegistryKekArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(SchemaRegistryKekArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 credentials: Optional[pulumi.Input[Union['SchemaRegistryKekCredentialsArgs', 'SchemaRegistryKekCredentialsArgsDict']]] = None,
                 doc: Optional[pulumi.Input[str]] = None,
                 hard_delete: Optional[pulumi.Input[bool]] = None,
                 kms_key_id: Optional[pulumi.Input[str]] = None,
                 kms_type: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 properties: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 rest_endpoint: Optional[pulumi.Input[str]] = None,
                 schema_registry_cluster: Optional[pulumi.Input[Union['SchemaRegistryKekSchemaRegistryClusterArgs', 'SchemaRegistryKekSchemaRegistryClusterArgsDict']]] = None,
                 shared: Optional[pulumi.Input[bool]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = SchemaRegistryKekArgs.__new__(SchemaRegistryKekArgs)

            __props__.__dict__["credentials"] = None if credentials is None else pulumi.Output.secret(credentials)
            __props__.__dict__["doc"] = doc
            __props__.__dict__["hard_delete"] = hard_delete
            if kms_key_id is None and not opts.urn:
                raise TypeError("Missing required property 'kms_key_id'")
            __props__.__dict__["kms_key_id"] = kms_key_id
            if kms_type is None and not opts.urn:
                raise TypeError("Missing required property 'kms_type'")
            __props__.__dict__["kms_type"] = kms_type
            __props__.__dict__["name"] = name
            __props__.__dict__["properties"] = properties
            __props__.__dict__["rest_endpoint"] = rest_endpoint
            __props__.__dict__["schema_registry_cluster"] = schema_registry_cluster
            __props__.__dict__["shared"] = shared
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["credentials"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(SchemaRegistryKek, __self__).__init__(
            'confluentcloud:index/schemaRegistryKek:SchemaRegistryKek',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            credentials: Optional[pulumi.Input[Union['SchemaRegistryKekCredentialsArgs', 'SchemaRegistryKekCredentialsArgsDict']]] = None,
            doc: Optional[pulumi.Input[str]] = None,
            hard_delete: Optional[pulumi.Input[bool]] = None,
            kms_key_id: Optional[pulumi.Input[str]] = None,
            kms_type: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            properties: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            rest_endpoint: Optional[pulumi.Input[str]] = None,
            schema_registry_cluster: Optional[pulumi.Input[Union['SchemaRegistryKekSchemaRegistryClusterArgs', 'SchemaRegistryKekSchemaRegistryClusterArgsDict']]] = None,
            shared: Optional[pulumi.Input[bool]] = None) -> 'SchemaRegistryKek':
        """
        Get an existing SchemaRegistryKek resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Union['SchemaRegistryKekCredentialsArgs', 'SchemaRegistryKekCredentialsArgsDict']] credentials: The Cluster API Credentials.
        :param pulumi.Input[str] doc: The optional description for the KEK.
        :param pulumi.Input[bool] hard_delete: Controls whether a kek should be soft or hard deleted. Set it to `true` if you want to hard delete a schema registry kek
               on destroy. Defaults to `false` (soft delete).
        :param pulumi.Input[str] kms_key_id: The ID of the key from KMS. 
               - When using the AWS KMS, this is an ARN, for example, `arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789abc`.
               - When using the Azure Key Vault, this is a Key Identifier (URI), for example, `https://test-keyvault1.vault.azure.net/keys/test-key1/1234567890abcdef1234567890abcdef`.
               - When using the GCP KMS, this is a resource name, for example, `projects/test-project1/locations/us-central1/keyRings/test-keyRing1/cryptoKeys/test-key1`.
        :param pulumi.Input[str] kms_type: The type of Key Management Service (KMS). The supported values include `aws-kms`, `azure-kms`, and `gcp-kms`. Additionally, custom KMS types are supported as well.
        :param pulumi.Input[str] name: The name for the KEK.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] properties: The custom properties to set (for example, `KeyUsage=ENCRYPT_DECRYPT`, `KeyState=Enabled`):
        :param pulumi.Input[str] rest_endpoint: The REST endpoint of the Schema Registry cluster, for example, `https://psrc-00000.us-central1.gcp.confluent.cloud:443`).
        :param pulumi.Input[bool] shared: The optional flag to control whether the DEK Registry has shared access to the KMS. Defaults to `false`.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _SchemaRegistryKekState.__new__(_SchemaRegistryKekState)

        __props__.__dict__["credentials"] = credentials
        __props__.__dict__["doc"] = doc
        __props__.__dict__["hard_delete"] = hard_delete
        __props__.__dict__["kms_key_id"] = kms_key_id
        __props__.__dict__["kms_type"] = kms_type
        __props__.__dict__["name"] = name
        __props__.__dict__["properties"] = properties
        __props__.__dict__["rest_endpoint"] = rest_endpoint
        __props__.__dict__["schema_registry_cluster"] = schema_registry_cluster
        __props__.__dict__["shared"] = shared
        return SchemaRegistryKek(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def credentials(self) -> pulumi.Output[Optional['outputs.SchemaRegistryKekCredentials']]:
        """
        The Cluster API Credentials.
        """
        return pulumi.get(self, "credentials")

    @property
    @pulumi.getter
    def doc(self) -> pulumi.Output[str]:
        """
        The optional description for the KEK.
        """
        return pulumi.get(self, "doc")

    @property
    @pulumi.getter(name="hardDelete")
    def hard_delete(self) -> pulumi.Output[Optional[bool]]:
        """
        Controls whether a kek should be soft or hard deleted. Set it to `true` if you want to hard delete a schema registry kek
        on destroy. Defaults to `false` (soft delete).
        """
        return pulumi.get(self, "hard_delete")

    @property
    @pulumi.getter(name="kmsKeyId")
    def kms_key_id(self) -> pulumi.Output[str]:
        """
        The ID of the key from KMS. 
        - When using the AWS KMS, this is an ARN, for example, `arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789abc`.
        - When using the Azure Key Vault, this is a Key Identifier (URI), for example, `https://test-keyvault1.vault.azure.net/keys/test-key1/1234567890abcdef1234567890abcdef`.
        - When using the GCP KMS, this is a resource name, for example, `projects/test-project1/locations/us-central1/keyRings/test-keyRing1/cryptoKeys/test-key1`.
        """
        return pulumi.get(self, "kms_key_id")

    @property
    @pulumi.getter(name="kmsType")
    def kms_type(self) -> pulumi.Output[str]:
        """
        The type of Key Management Service (KMS). The supported values include `aws-kms`, `azure-kms`, and `gcp-kms`. Additionally, custom KMS types are supported as well.
        """
        return pulumi.get(self, "kms_type")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name for the KEK.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def properties(self) -> pulumi.Output[Mapping[str, str]]:
        """
        The custom properties to set (for example, `KeyUsage=ENCRYPT_DECRYPT`, `KeyState=Enabled`):
        """
        return pulumi.get(self, "properties")

    @property
    @pulumi.getter(name="restEndpoint")
    def rest_endpoint(self) -> pulumi.Output[Optional[str]]:
        """
        The REST endpoint of the Schema Registry cluster, for example, `https://psrc-00000.us-central1.gcp.confluent.cloud:443`).
        """
        return pulumi.get(self, "rest_endpoint")

    @property
    @pulumi.getter(name="schemaRegistryCluster")
    def schema_registry_cluster(self) -> pulumi.Output[Optional['outputs.SchemaRegistryKekSchemaRegistryCluster']]:
        return pulumi.get(self, "schema_registry_cluster")

    @property
    @pulumi.getter
    def shared(self) -> pulumi.Output[Optional[bool]]:
        """
        The optional flag to control whether the DEK Registry has shared access to the KMS. Defaults to `false`.
        """
        return pulumi.get(self, "shared")

