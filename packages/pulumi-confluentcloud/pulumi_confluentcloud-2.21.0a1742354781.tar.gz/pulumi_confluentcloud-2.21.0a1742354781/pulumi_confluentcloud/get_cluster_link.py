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
    'GetClusterLinkResult',
    'AwaitableGetClusterLinkResult',
    'get_cluster_link',
    'get_cluster_link_output',
]

@pulumi.output_type
class GetClusterLinkResult:
    """
    A collection of values returned by getClusterLink.
    """
    def __init__(__self__, cluster_link_id=None, config=None, credentials=None, id=None, kafka_cluster=None, link_name=None, link_state=None, rest_endpoint=None):
        if cluster_link_id and not isinstance(cluster_link_id, str):
            raise TypeError("Expected argument 'cluster_link_id' to be a str")
        pulumi.set(__self__, "cluster_link_id", cluster_link_id)
        if config and not isinstance(config, dict):
            raise TypeError("Expected argument 'config' to be a dict")
        pulumi.set(__self__, "config", config)
        if credentials and not isinstance(credentials, dict):
            raise TypeError("Expected argument 'credentials' to be a dict")
        pulumi.set(__self__, "credentials", credentials)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if kafka_cluster and not isinstance(kafka_cluster, dict):
            raise TypeError("Expected argument 'kafka_cluster' to be a dict")
        pulumi.set(__self__, "kafka_cluster", kafka_cluster)
        if link_name and not isinstance(link_name, str):
            raise TypeError("Expected argument 'link_name' to be a str")
        pulumi.set(__self__, "link_name", link_name)
        if link_state and not isinstance(link_state, str):
            raise TypeError("Expected argument 'link_state' to be a str")
        pulumi.set(__self__, "link_state", link_state)
        if rest_endpoint and not isinstance(rest_endpoint, str):
            raise TypeError("Expected argument 'rest_endpoint' to be a str")
        pulumi.set(__self__, "rest_endpoint", rest_endpoint)

    @property
    @pulumi.getter(name="clusterLinkId")
    def cluster_link_id(self) -> str:
        """
        (Required String) The actual Cluster Link ID assigned from Confluent Cloud that uniquely represents a link between two Kafka clusters, for example, `qz0HDEV-Qz2B5aPFpcWQJQ`.
        """
        return pulumi.get(self, "cluster_link_id")

    @property
    @pulumi.getter
    def config(self) -> Mapping[str, str]:
        """
        (Optional Map) The custom cluster link settings retrieved:
        """
        return pulumi.get(self, "config")

    @property
    @pulumi.getter
    def credentials(self) -> Optional['outputs.GetClusterLinkCredentialsResult']:
        return pulumi.get(self, "credentials")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        (Required String) The composite ID of the Cluster Link data-source, in the format `<Kafka cluster ID>/<Cluster link name>`, for example, `lkc-abc123/my-cluster-link`.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="kafkaCluster")
    def kafka_cluster(self) -> Optional['outputs.GetClusterLinkKafkaClusterResult']:
        return pulumi.get(self, "kafka_cluster")

    @property
    @pulumi.getter(name="linkName")
    def link_name(self) -> str:
        return pulumi.get(self, "link_name")

    @property
    @pulumi.getter(name="linkState")
    def link_state(self) -> str:
        """
        (Required String) The current state of the Cluster Link.
        """
        return pulumi.get(self, "link_state")

    @property
    @pulumi.getter(name="restEndpoint")
    def rest_endpoint(self) -> Optional[str]:
        return pulumi.get(self, "rest_endpoint")


class AwaitableGetClusterLinkResult(GetClusterLinkResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetClusterLinkResult(
            cluster_link_id=self.cluster_link_id,
            config=self.config,
            credentials=self.credentials,
            id=self.id,
            kafka_cluster=self.kafka_cluster,
            link_name=self.link_name,
            link_state=self.link_state,
            rest_endpoint=self.rest_endpoint)


def get_cluster_link(credentials: Optional[Union['GetClusterLinkCredentialsArgs', 'GetClusterLinkCredentialsArgsDict']] = None,
                     kafka_cluster: Optional[Union['GetClusterLinkKafkaClusterArgs', 'GetClusterLinkKafkaClusterArgsDict']] = None,
                     link_name: Optional[str] = None,
                     rest_endpoint: Optional[str] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetClusterLinkResult:
    """
    [![General Availability](https://img.shields.io/badge/Lifecycle%20Stage-General%20Availability-%2345c6e8)](https://docs.confluent.io/cloud/current/api.html#section/Versioning/API-Lifecycle-Policy)

    `ClusterLink` describes a Cluster Link data source.

    ## Example Usage

    ### Option #1: Manage multiple Kafka clusters in the same Pulumi Stack

    ```python
    import pulumi
    import pulumi_confluentcloud as confluentcloud

    main = confluentcloud.get_cluster_link(link_name="main-link",
        rest_endpoint=west["restEndpoint"],
        kafka_cluster={
            "id": west["id"],
        },
        credentials={
            "key": app_manager_west_cluster_api_key["id"],
            "secret": app_manager_west_cluster_api_key["secret"],
        })
    pulumi.export("kafkaClusterLinkId", main.cluster_link_id)
    ```

    ### Option #2: Manage a single Kafka cluster in the same Pulumi Stack

    ```python
    import pulumi
    import pulumi_confluentcloud as confluentcloud

    main = confluentcloud.get_cluster_link(link_name="main-link")
    pulumi.export("kafkaClusterLinkId", main.cluster_link_id)
    ```


    :param str link_name: The name of the cluster link, for example, `my-cluster-link`.
    :param str rest_endpoint: The REST endpoint of the Kafka cluster, for example, `https://pkc-00000.us-central1.gcp.confluent.cloud:443`).
    """
    __args__ = dict()
    __args__['credentials'] = credentials
    __args__['kafkaCluster'] = kafka_cluster
    __args__['linkName'] = link_name
    __args__['restEndpoint'] = rest_endpoint
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('confluentcloud:index/getClusterLink:getClusterLink', __args__, opts=opts, typ=GetClusterLinkResult).value

    return AwaitableGetClusterLinkResult(
        cluster_link_id=pulumi.get(__ret__, 'cluster_link_id'),
        config=pulumi.get(__ret__, 'config'),
        credentials=pulumi.get(__ret__, 'credentials'),
        id=pulumi.get(__ret__, 'id'),
        kafka_cluster=pulumi.get(__ret__, 'kafka_cluster'),
        link_name=pulumi.get(__ret__, 'link_name'),
        link_state=pulumi.get(__ret__, 'link_state'),
        rest_endpoint=pulumi.get(__ret__, 'rest_endpoint'))
def get_cluster_link_output(credentials: Optional[pulumi.Input[Optional[Union['GetClusterLinkCredentialsArgs', 'GetClusterLinkCredentialsArgsDict']]]] = None,
                            kafka_cluster: Optional[pulumi.Input[Optional[Union['GetClusterLinkKafkaClusterArgs', 'GetClusterLinkKafkaClusterArgsDict']]]] = None,
                            link_name: Optional[pulumi.Input[str]] = None,
                            rest_endpoint: Optional[pulumi.Input[Optional[str]]] = None,
                            opts: Optional[Union[pulumi.InvokeOptions, pulumi.InvokeOutputOptions]] = None) -> pulumi.Output[GetClusterLinkResult]:
    """
    [![General Availability](https://img.shields.io/badge/Lifecycle%20Stage-General%20Availability-%2345c6e8)](https://docs.confluent.io/cloud/current/api.html#section/Versioning/API-Lifecycle-Policy)

    `ClusterLink` describes a Cluster Link data source.

    ## Example Usage

    ### Option #1: Manage multiple Kafka clusters in the same Pulumi Stack

    ```python
    import pulumi
    import pulumi_confluentcloud as confluentcloud

    main = confluentcloud.get_cluster_link(link_name="main-link",
        rest_endpoint=west["restEndpoint"],
        kafka_cluster={
            "id": west["id"],
        },
        credentials={
            "key": app_manager_west_cluster_api_key["id"],
            "secret": app_manager_west_cluster_api_key["secret"],
        })
    pulumi.export("kafkaClusterLinkId", main.cluster_link_id)
    ```

    ### Option #2: Manage a single Kafka cluster in the same Pulumi Stack

    ```python
    import pulumi
    import pulumi_confluentcloud as confluentcloud

    main = confluentcloud.get_cluster_link(link_name="main-link")
    pulumi.export("kafkaClusterLinkId", main.cluster_link_id)
    ```


    :param str link_name: The name of the cluster link, for example, `my-cluster-link`.
    :param str rest_endpoint: The REST endpoint of the Kafka cluster, for example, `https://pkc-00000.us-central1.gcp.confluent.cloud:443`).
    """
    __args__ = dict()
    __args__['credentials'] = credentials
    __args__['kafkaCluster'] = kafka_cluster
    __args__['linkName'] = link_name
    __args__['restEndpoint'] = rest_endpoint
    opts = pulumi.InvokeOutputOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke_output('confluentcloud:index/getClusterLink:getClusterLink', __args__, opts=opts, typ=GetClusterLinkResult)
    return __ret__.apply(lambda __response__: GetClusterLinkResult(
        cluster_link_id=pulumi.get(__response__, 'cluster_link_id'),
        config=pulumi.get(__response__, 'config'),
        credentials=pulumi.get(__response__, 'credentials'),
        id=pulumi.get(__response__, 'id'),
        kafka_cluster=pulumi.get(__response__, 'kafka_cluster'),
        link_name=pulumi.get(__response__, 'link_name'),
        link_state=pulumi.get(__response__, 'link_state'),
        rest_endpoint=pulumi.get(__response__, 'rest_endpoint')))
