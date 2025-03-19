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

__all__ = [
    'GetIpAddressesResult',
    'AwaitableGetIpAddressesResult',
    'get_ip_addresses',
    'get_ip_addresses_output',
]

@pulumi.output_type
class GetIpAddressesResult:
    """
    A collection of values returned by getIpAddresses.
    """
    def __init__(__self__, filter=None, id=None, ip_addresses=None):
        if filter and not isinstance(filter, dict):
            raise TypeError("Expected argument 'filter' to be a dict")
        pulumi.set(__self__, "filter", filter)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if ip_addresses and not isinstance(ip_addresses, list):
            raise TypeError("Expected argument 'ip_addresses' to be a list")
        pulumi.set(__self__, "ip_addresses", ip_addresses)

    @property
    @pulumi.getter
    def filter(self) -> Optional['outputs.GetIpAddressesFilterResult']:
        return pulumi.get(self, "filter")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="ipAddresses")
    def ip_addresses(self) -> Sequence['outputs.GetIpAddressesIpAddressResult']:
        """
        (List of Object) List of schemas. Each schema object exports the following attributes:
        """
        return pulumi.get(self, "ip_addresses")


class AwaitableGetIpAddressesResult(GetIpAddressesResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetIpAddressesResult(
            filter=self.filter,
            id=self.id,
            ip_addresses=self.ip_addresses)


def get_ip_addresses(filter: Optional[Union['GetIpAddressesFilterArgs', 'GetIpAddressesFilterArgsDict']] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetIpAddressesResult:
    """
    [![Preview](https://img.shields.io/badge/Lifecycle%20Stage-Preview-%2300afba)](https://docs.confluent.io/cloud/current/api.html#section/Versioning/API-Lifecycle-Policy)

    > **Note:** `get_ip_addresses` data source is available in **Preview** for early adopters. Preview features are introduced to gather customer feedback. This feature should be used only for evaluation and non-production testing purposes or to provide feedback to Confluent, particularly as it becomes more widely available in follow-on editions.\\
    **Preview** features are intended for evaluation use in development and testing environments only, and not for production use. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Preview features are considered to be a Proof of Concept as defined in the Confluent Cloud Terms of Service. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s sole discretion.

    `get_ip_addresses` describes IP Addresses data source.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_confluentcloud as confluentcloud

    main = confluentcloud.get_ip_addresses(filter={
        "clouds": ["AWS"],
        "regions": [
            "us-east-1",
            "us-east-2",
        ],
        "services": ["KAFKA"],
        "address_types": ["EGRESS"],
    })
    pulumi.export("ipAddresses", main.ip_addresses)
    ```
    """
    __args__ = dict()
    __args__['filter'] = filter
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('confluentcloud:index/getIpAddresses:getIpAddresses', __args__, opts=opts, typ=GetIpAddressesResult).value

    return AwaitableGetIpAddressesResult(
        filter=pulumi.get(__ret__, 'filter'),
        id=pulumi.get(__ret__, 'id'),
        ip_addresses=pulumi.get(__ret__, 'ip_addresses'))
def get_ip_addresses_output(filter: Optional[pulumi.Input[Optional[Union['GetIpAddressesFilterArgs', 'GetIpAddressesFilterArgsDict']]]] = None,
                            opts: Optional[Union[pulumi.InvokeOptions, pulumi.InvokeOutputOptions]] = None) -> pulumi.Output[GetIpAddressesResult]:
    """
    [![Preview](https://img.shields.io/badge/Lifecycle%20Stage-Preview-%2300afba)](https://docs.confluent.io/cloud/current/api.html#section/Versioning/API-Lifecycle-Policy)

    > **Note:** `get_ip_addresses` data source is available in **Preview** for early adopters. Preview features are introduced to gather customer feedback. This feature should be used only for evaluation and non-production testing purposes or to provide feedback to Confluent, particularly as it becomes more widely available in follow-on editions.\\
    **Preview** features are intended for evaluation use in development and testing environments only, and not for production use. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Preview features are considered to be a Proof of Concept as defined in the Confluent Cloud Terms of Service. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s sole discretion.

    `get_ip_addresses` describes IP Addresses data source.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_confluentcloud as confluentcloud

    main = confluentcloud.get_ip_addresses(filter={
        "clouds": ["AWS"],
        "regions": [
            "us-east-1",
            "us-east-2",
        ],
        "services": ["KAFKA"],
        "address_types": ["EGRESS"],
    })
    pulumi.export("ipAddresses", main.ip_addresses)
    ```
    """
    __args__ = dict()
    __args__['filter'] = filter
    opts = pulumi.InvokeOutputOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke_output('confluentcloud:index/getIpAddresses:getIpAddresses', __args__, opts=opts, typ=GetIpAddressesResult)
    return __ret__.apply(lambda __response__: GetIpAddressesResult(
        filter=pulumi.get(__response__, 'filter'),
        id=pulumi.get(__response__, 'id'),
        ip_addresses=pulumi.get(__response__, 'ip_addresses')))
