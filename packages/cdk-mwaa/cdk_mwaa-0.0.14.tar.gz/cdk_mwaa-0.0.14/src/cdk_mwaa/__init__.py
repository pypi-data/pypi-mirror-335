r'''
# cdk-mwaa

This project provides an AWS CDK construct library for creating and managing Amazon Managed Workflows for Apache Airflow (MWAA) environments.

## Features

* Create and manage MWAA environments
* Configure environment properties such as webserver access mode, Airflow version, environment class, and more
* Validate and set default values for environment properties
* Automatically create and configure necessary AWS resources such as S3 buckets and VPCs

## Installation

To use this construct library in your AWS CDK project, add it as a dependency:

```sh
npm install cdk-mwaa
# or
yarn add cdk-mwaa
```

## Usage

Here is an example of how to use the `cdk-mwaa` construct library in your AWS CDK project:

```python
import * as path from 'node:path';
import * as cdk from 'aws-cdk-lib';
import * as mwaa from 'cdk-mwaa';

const app = new cdk.App();
const stack = new cdk.Stack(app, 'MwaaStack');

const dagStorage = new mwaa.DagStorage(stack, 'MyMwaaDagStorage', {
    bucketName: 'my-mwaa-dag-storage',
    dagsOptions: {
        localPath: path.join(__dirname, 'dags'),
        s3Path: 'dags/',
      },
    // additional configuration options...
});

new mwaa.Environment(stack, 'MyMwaaEnvironment', {
    name: 'my-mwaa-environment',
    dagStorage,
    airflowVersion: '2.10.3',
    sizing: mwaa.Sizing.mw1Micro(),
    // additional configuration options...
});

app.synth();
```

## Enabling Secrets Backend

To enable the secrets backend for your MWAA environment, you can use the `enableSecretsBackend` method. This allows you to securely manage secrets and environment variables.

Here is an example of how to enable the secrets backend in your MWAA environment:

```python
import * as cdk from 'aws-cdk-lib';
import * as mwaa from 'cdk-mwaa';

const app = new cdk.App();
const stack = new cdk.Stack(app, 'MwaaStack');

const dagStorage = new mwaa.DagStorage(stack, 'MyMwaaDagStorage', {
    bucketName: 'my-mwaa-dag-storage',
    // additional configuration options...
});

const environment = new mwaa.Environment(stack, 'MyMwaaEnvironment', {
    name: 'my-mwaa-environment',
    dagStorage,
    airflowVersion: '2.10.3',
    sizing: mwaa.Sizing.mw1Micro(),
    // additional configuration options...
});

// Enabling Secrets Backend
environment.enableSecretsBackend();

app.synth();
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="cdk-mwaa.AirflowPoolProps",
    jsii_struct_bases=[],
    name_mapping={
        "environment": "environment",
        "pool_name": "poolName",
        "pool_description": "poolDescription",
        "pool_slots": "poolSlots",
    },
)
class AirflowPoolProps:
    def __init__(
        self,
        *,
        environment: "Environment",
        pool_name: builtins.str,
        pool_description: typing.Optional[builtins.str] = None,
        pool_slots: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param environment: 
        :param pool_name: 
        :param pool_description: 
        :param pool_slots: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef40a9fd92922a66e131a522a984aec05eba98c0a668dd806969973bb688f73d)
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument pool_name", value=pool_name, expected_type=type_hints["pool_name"])
            check_type(argname="argument pool_description", value=pool_description, expected_type=type_hints["pool_description"])
            check_type(argname="argument pool_slots", value=pool_slots, expected_type=type_hints["pool_slots"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "environment": environment,
            "pool_name": pool_name,
        }
        if pool_description is not None:
            self._values["pool_description"] = pool_description
        if pool_slots is not None:
            self._values["pool_slots"] = pool_slots

    @builtins.property
    def environment(self) -> "Environment":
        result = self._values.get("environment")
        assert result is not None, "Required property 'environment' is missing"
        return typing.cast("Environment", result)

    @builtins.property
    def pool_name(self) -> builtins.str:
        result = self._values.get("pool_name")
        assert result is not None, "Required property 'pool_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pool_description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("pool_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pool_slots(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("pool_slots")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AirflowPoolProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AirflowResourceBase(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk-mwaa.AirflowResourceBase",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        environment: "Environment",
        properties: typing.Mapping[builtins.str, typing.Any],
        resource_type: builtins.str,
        airflow_role: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param environment: 
        :param properties: 
        :param resource_type: 
        :param airflow_role: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61b1e5b1838312720b9a40d8100bdb1ea7816afa18317e3c11c6c7b57fea60d9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AirflowResourceBaseProps(
            environment=environment,
            properties=properties,
            resource_type=resource_type,
            airflow_role=airflow_role,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class _AirflowResourceBaseProxy(AirflowResourceBase):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, AirflowResourceBase).__jsii_proxy_class__ = lambda : _AirflowResourceBaseProxy


@jsii.data_type(
    jsii_type="cdk-mwaa.AirflowResourceBaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "environment": "environment",
        "properties": "properties",
        "resource_type": "resourceType",
        "airflow_role": "airflowRole",
    },
)
class AirflowResourceBaseProps:
    def __init__(
        self,
        *,
        environment: "Environment",
        properties: typing.Mapping[builtins.str, typing.Any],
        resource_type: builtins.str,
        airflow_role: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param environment: 
        :param properties: 
        :param resource_type: 
        :param airflow_role: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a8f1fd388b3f30715d7f1ec120097450271a8e8e30b8f0b682d0b5169eb2bca)
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
            check_type(argname="argument resource_type", value=resource_type, expected_type=type_hints["resource_type"])
            check_type(argname="argument airflow_role", value=airflow_role, expected_type=type_hints["airflow_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "environment": environment,
            "properties": properties,
            "resource_type": resource_type,
        }
        if airflow_role is not None:
            self._values["airflow_role"] = airflow_role

    @builtins.property
    def environment(self) -> "Environment":
        result = self._values.get("environment")
        assert result is not None, "Required property 'environment' is missing"
        return typing.cast("Environment", result)

    @builtins.property
    def properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        result = self._values.get("properties")
        assert result is not None, "Required property 'properties' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def resource_type(self) -> builtins.str:
        result = self._values.get("resource_type")
        assert result is not None, "Required property 'resource_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def airflow_role(self) -> typing.Optional[builtins.str]:
        result = self._values.get("airflow_role")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AirflowResourceBaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BaseVpc(
    _aws_cdk_aws_ec2_ceddda9d.Vpc,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk-mwaa.BaseVpc",
):
    '''Abstract base class for creating a VPC with common configurations.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        create_internet_gateway: builtins.bool,
        subnet_configuration: typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]],
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        vpc_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param create_internet_gateway: Whether to create an Internet Gateway for public access.
        :param subnet_configuration: Subnet configuration for the VPC.
        :param ip_addresses: IP address allocation strategy for the VPC.
        :param nat_gateways: Number of NAT gateways to create.
        :param vpc_name: Optional name for the VPC.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36432c6d2bb93b3d16e7983780304847c92cd402d8b9d4a0d6f29506aa732ff5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BaseVpcProps(
            create_internet_gateway=create_internet_gateway,
            subnet_configuration=subnet_configuration,
            ip_addresses=ip_addresses,
            nat_gateways=nat_gateways,
            vpc_name=vpc_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="s3VpcEndpoint")
    def s3_vpc_endpoint(self) -> _aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpoint:
        '''S3 Gateway VPC Endpoint.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpoint, jsii.get(self, "s3VpcEndpoint"))


class _BaseVpcProxy(BaseVpc):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseVpc).__jsii_proxy_class__ = lambda : _BaseVpcProxy


@jsii.data_type(
    jsii_type="cdk-mwaa.CommonVpcProps",
    jsii_struct_bases=[],
    name_mapping={
        "ip_addresses": "ipAddresses",
        "nat_gateways": "natGateways",
        "vpc_name": "vpcName",
    },
)
class CommonVpcProps:
    def __init__(
        self,
        *,
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        vpc_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Common properties shared across different VPC constructs.

        :param ip_addresses: IP address allocation strategy for the VPC.
        :param nat_gateways: Number of NAT gateways to create.
        :param vpc_name: Optional name for the VPC.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60109e2a88eeebcaea010b7e40b7c342ff04bb32117665b005b7c01620dafa51)
            check_type(argname="argument ip_addresses", value=ip_addresses, expected_type=type_hints["ip_addresses"])
            check_type(argname="argument nat_gateways", value=nat_gateways, expected_type=type_hints["nat_gateways"])
            check_type(argname="argument vpc_name", value=vpc_name, expected_type=type_hints["vpc_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if nat_gateways is not None:
            self._values["nat_gateways"] = nat_gateways
        if vpc_name is not None:
            self._values["vpc_name"] = vpc_name

    @builtins.property
    def ip_addresses(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses]:
        '''IP address allocation strategy for the VPC.'''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses], result)

    @builtins.property
    def nat_gateways(self) -> typing.Optional[jsii.Number]:
        '''Number of NAT gateways to create.'''
        result = self._values.get("nat_gateways")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc_name(self) -> typing.Optional[builtins.str]:
        '''Optional name for the VPC.'''
        result = self._values.get("vpc_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonVpcProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-mwaa.ConfigFile",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "version": "version"},
)
class ConfigFile:
    def __init__(
        self,
        *,
        name: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Represents a configuration file stored in S3.

        :param name: The name of the configuration file.
        :param version: Optional S3 object version identifier.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18fc569fcf933a2b3ce7fe86ffe34609735a142137b7878008714403e6813a46)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the configuration file.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Optional S3 object version identifier.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigFile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-mwaa.ConfigsOptions",
    jsii_struct_bases=[],
    name_mapping={
        "deploy_options": "deployOptions",
        "local_path": "localPath",
        "plugins": "plugins",
        "requirements": "requirements",
        "s3_prefix": "s3Prefix",
        "startup_script": "startupScript",
    },
)
class ConfigsOptions:
    def __init__(
        self,
        *,
        deploy_options: typing.Optional[typing.Union["DeployOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        local_path: typing.Optional[builtins.str] = None,
        plugins: typing.Optional[typing.Union[ConfigFile, typing.Dict[builtins.str, typing.Any]]] = None,
        requirements: typing.Optional[typing.Union[ConfigFile, typing.Dict[builtins.str, typing.Any]]] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        startup_script: typing.Optional[typing.Union[ConfigFile, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Configuration options for storing configuration files in S3.

        :param deploy_options: Deployment options for configuration storage.
        :param local_path: Optional local path for the configuration files.
        :param plugins: Optional plugins file configuration.
        :param requirements: Optional requirements file configuration.
        :param s3_prefix: The S3 prefix where configuration files are stored.
        :param startup_script: Optional startup script file configuration.
        '''
        if isinstance(deploy_options, dict):
            deploy_options = DeployOptions(**deploy_options)
        if isinstance(plugins, dict):
            plugins = ConfigFile(**plugins)
        if isinstance(requirements, dict):
            requirements = ConfigFile(**requirements)
        if isinstance(startup_script, dict):
            startup_script = ConfigFile(**startup_script)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21e969a6710fc7238d65620a64ca6e99674b344908eb39331069a48b8b9f6f37)
            check_type(argname="argument deploy_options", value=deploy_options, expected_type=type_hints["deploy_options"])
            check_type(argname="argument local_path", value=local_path, expected_type=type_hints["local_path"])
            check_type(argname="argument plugins", value=plugins, expected_type=type_hints["plugins"])
            check_type(argname="argument requirements", value=requirements, expected_type=type_hints["requirements"])
            check_type(argname="argument s3_prefix", value=s3_prefix, expected_type=type_hints["s3_prefix"])
            check_type(argname="argument startup_script", value=startup_script, expected_type=type_hints["startup_script"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if deploy_options is not None:
            self._values["deploy_options"] = deploy_options
        if local_path is not None:
            self._values["local_path"] = local_path
        if plugins is not None:
            self._values["plugins"] = plugins
        if requirements is not None:
            self._values["requirements"] = requirements
        if s3_prefix is not None:
            self._values["s3_prefix"] = s3_prefix
        if startup_script is not None:
            self._values["startup_script"] = startup_script

    @builtins.property
    def deploy_options(self) -> typing.Optional["DeployOptions"]:
        '''Deployment options for configuration storage.'''
        result = self._values.get("deploy_options")
        return typing.cast(typing.Optional["DeployOptions"], result)

    @builtins.property
    def local_path(self) -> typing.Optional[builtins.str]:
        '''Optional local path for the configuration files.'''
        result = self._values.get("local_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def plugins(self) -> typing.Optional[ConfigFile]:
        '''Optional plugins file configuration.'''
        result = self._values.get("plugins")
        return typing.cast(typing.Optional[ConfigFile], result)

    @builtins.property
    def requirements(self) -> typing.Optional[ConfigFile]:
        '''Optional requirements file configuration.'''
        result = self._values.get("requirements")
        return typing.cast(typing.Optional[ConfigFile], result)

    @builtins.property
    def s3_prefix(self) -> typing.Optional[builtins.str]:
        '''The S3 prefix where configuration files are stored.'''
        result = self._values.get("s3_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def startup_script(self) -> typing.Optional[ConfigFile]:
        '''Optional startup script file configuration.'''
        result = self._values.get("startup_script")
        return typing.cast(typing.Optional[ConfigFile], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DagStorage(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-mwaa.DagStorage",
):
    '''Represents an S3 storage solution for MWAA DAGs and dependencies.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        configs_options: typing.Optional[typing.Union[ConfigsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        dags_options: typing.Optional[typing.Union["DagsOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        noncurrent_version_expiration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        versioned: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_name: Optional custom bucket name.
        :param configs_options: Configuration for additional configuration files.
        :param dags_options: Configuration for DAG storage.
        :param noncurrent_version_expiration: Lifecycle rule for expiring non-current object versions.
        :param removal_policy: Policy to determine bucket removal behavior.
        :param versioned: Whether to enable versioning for the bucket.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95a166027e8ebcfead2708b1c3388e60862a4fb6d86763bf56854f275bdd2390)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DagStorageProps(
            bucket_name=bucket_name,
            configs_options=configs_options,
            dags_options=dags_options,
            noncurrent_version_expiration=noncurrent_version_expiration,
            removal_policy=removal_policy,
            versioned=versioned,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''The S3 bucket storing DAGs, plugins, requirements, and startup scripts.'''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.get(self, "bucket"))

    @builtins.property
    @jsii.member(jsii_name="dagS3Path")
    def dag_s3_path(self) -> typing.Optional[builtins.str]:
        '''S3 path for DAGs.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dagS3Path"))

    @builtins.property
    @jsii.member(jsii_name="pluginsS3ObjectVersion")
    def plugins_s3_object_version(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pluginsS3ObjectVersion"))

    @builtins.property
    @jsii.member(jsii_name="pluginsS3Path")
    def plugins_s3_path(self) -> typing.Optional[builtins.str]:
        '''S3 paths and object versions for configuration files.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pluginsS3Path"))

    @builtins.property
    @jsii.member(jsii_name="requirementsS3ObjectVersion")
    def requirements_s3_object_version(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requirementsS3ObjectVersion"))

    @builtins.property
    @jsii.member(jsii_name="requirementsS3Path")
    def requirements_s3_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requirementsS3Path"))

    @builtins.property
    @jsii.member(jsii_name="startupScriptS3ObjectVersion")
    def startup_script_s3_object_version(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startupScriptS3ObjectVersion"))

    @builtins.property
    @jsii.member(jsii_name="startupScriptS3Path")
    def startup_script_s3_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startupScriptS3Path"))


@jsii.data_type(
    jsii_type="cdk-mwaa.DagStorageProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "configs_options": "configsOptions",
        "dags_options": "dagsOptions",
        "noncurrent_version_expiration": "noncurrentVersionExpiration",
        "removal_policy": "removalPolicy",
        "versioned": "versioned",
    },
)
class DagStorageProps:
    def __init__(
        self,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        configs_options: typing.Optional[typing.Union[ConfigsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        dags_options: typing.Optional[typing.Union["DagsOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        noncurrent_version_expiration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        versioned: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties for configuring the DAG storage bucket.

        :param bucket_name: Optional custom bucket name.
        :param configs_options: Configuration for additional configuration files.
        :param dags_options: Configuration for DAG storage.
        :param noncurrent_version_expiration: Lifecycle rule for expiring non-current object versions.
        :param removal_policy: Policy to determine bucket removal behavior.
        :param versioned: Whether to enable versioning for the bucket.
        '''
        if isinstance(configs_options, dict):
            configs_options = ConfigsOptions(**configs_options)
        if isinstance(dags_options, dict):
            dags_options = DagsOptions(**dags_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a4bace9647a9566f3af4198e17ef015306e92a6d5f673b579ba6fdfcb5231da)
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument configs_options", value=configs_options, expected_type=type_hints["configs_options"])
            check_type(argname="argument dags_options", value=dags_options, expected_type=type_hints["dags_options"])
            check_type(argname="argument noncurrent_version_expiration", value=noncurrent_version_expiration, expected_type=type_hints["noncurrent_version_expiration"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument versioned", value=versioned, expected_type=type_hints["versioned"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if configs_options is not None:
            self._values["configs_options"] = configs_options
        if dags_options is not None:
            self._values["dags_options"] = dags_options
        if noncurrent_version_expiration is not None:
            self._values["noncurrent_version_expiration"] = noncurrent_version_expiration
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if versioned is not None:
            self._values["versioned"] = versioned

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Optional custom bucket name.'''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def configs_options(self) -> typing.Optional[ConfigsOptions]:
        '''Configuration for additional configuration files.'''
        result = self._values.get("configs_options")
        return typing.cast(typing.Optional[ConfigsOptions], result)

    @builtins.property
    def dags_options(self) -> typing.Optional["DagsOptions"]:
        '''Configuration for DAG storage.'''
        result = self._values.get("dags_options")
        return typing.cast(typing.Optional["DagsOptions"], result)

    @builtins.property
    def noncurrent_version_expiration(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Lifecycle rule for expiring non-current object versions.'''
        result = self._values.get("noncurrent_version_expiration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Policy to determine bucket removal behavior.'''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def versioned(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable versioning for the bucket.'''
        result = self._values.get("versioned")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DagStorageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-mwaa.DagsOptions",
    jsii_struct_bases=[],
    name_mapping={
        "deploy_options": "deployOptions",
        "local_path": "localPath",
        "s3_path": "s3Path",
    },
)
class DagsOptions:
    def __init__(
        self,
        *,
        deploy_options: typing.Optional[typing.Union["DeployOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        local_path: typing.Optional[builtins.str] = None,
        s3_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Configuration options for DAG storage.

        :param deploy_options: Deployment options for DAG storage.
        :param local_path: Optional local path for DAGs before deployment.
        :param s3_path: The S3 path where the DAGs are stored.
        '''
        if isinstance(deploy_options, dict):
            deploy_options = DeployOptions(**deploy_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__098c6089073cc202551294a55936ecb95864b4c571722f34012f6a90ac91ac1d)
            check_type(argname="argument deploy_options", value=deploy_options, expected_type=type_hints["deploy_options"])
            check_type(argname="argument local_path", value=local_path, expected_type=type_hints["local_path"])
            check_type(argname="argument s3_path", value=s3_path, expected_type=type_hints["s3_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if deploy_options is not None:
            self._values["deploy_options"] = deploy_options
        if local_path is not None:
            self._values["local_path"] = local_path
        if s3_path is not None:
            self._values["s3_path"] = s3_path

    @builtins.property
    def deploy_options(self) -> typing.Optional["DeployOptions"]:
        '''Deployment options for DAG storage.'''
        result = self._values.get("deploy_options")
        return typing.cast(typing.Optional["DeployOptions"], result)

    @builtins.property
    def local_path(self) -> typing.Optional[builtins.str]:
        '''Optional local path for DAGs before deployment.'''
        result = self._values.get("local_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_path(self) -> typing.Optional[builtins.str]:
        '''The S3 path where the DAGs are stored.'''
        result = self._values.get("s3_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DagsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-mwaa.DeployOptions",
    jsii_struct_bases=[],
    name_mapping={
        "exclude": "exclude",
        "prune": "prune",
        "retain_on_delete": "retainOnDelete",
    },
)
class DeployOptions:
    def __init__(
        self,
        *,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        prune: typing.Optional[builtins.bool] = None,
        retain_on_delete: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Options for deploying files to the DAG storage bucket.

        :param exclude: Patterns to exclude from deployment.
        :param prune: Whether to remove outdated file versions.
        :param retain_on_delete: Whether to retain files upon stack deletion.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48a44035944b9df12f94158952c1f3535c44b8ea35ed316dfb479569f4286bb0)
            check_type(argname="argument exclude", value=exclude, expected_type=type_hints["exclude"])
            check_type(argname="argument prune", value=prune, expected_type=type_hints["prune"])
            check_type(argname="argument retain_on_delete", value=retain_on_delete, expected_type=type_hints["retain_on_delete"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exclude is not None:
            self._values["exclude"] = exclude
        if prune is not None:
            self._values["prune"] = prune
        if retain_on_delete is not None:
            self._values["retain_on_delete"] = retain_on_delete

    @builtins.property
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Patterns to exclude from deployment.'''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def prune(self) -> typing.Optional[builtins.bool]:
        '''Whether to remove outdated file versions.'''
        result = self._values.get("prune")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def retain_on_delete(self) -> typing.Optional[builtins.bool]:
        '''Whether to retain files upon stack deletion.'''
        result = self._values.get("retain_on_delete")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeployOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-mwaa.EmailBackendOptions",
    jsii_struct_bases=[],
    name_mapping={"from_email": "fromEmail", "conn_id": "connId"},
)
class EmailBackendOptions:
    def __init__(
        self,
        *,
        from_email: builtins.str,
        conn_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Options for configuring the Email backend.

        :param from_email: 
        :param conn_id: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73e90f0cf9b9873d2646653b49d16d81a04d7e328760c253beb412d5e74258d3)
            check_type(argname="argument from_email", value=from_email, expected_type=type_hints["from_email"])
            check_type(argname="argument conn_id", value=conn_id, expected_type=type_hints["conn_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "from_email": from_email,
        }
        if conn_id is not None:
            self._values["conn_id"] = conn_id

    @builtins.property
    def from_email(self) -> builtins.str:
        result = self._values.get("from_email")
        assert result is not None, "Required property 'from_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def conn_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("conn_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmailBackendOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-mwaa.EndpointManagement")
class EndpointManagement(enum.Enum):
    '''Enum for the endpoint management type for the MWAA environment.'''

    CUSTOMER = "CUSTOMER"
    SERVICE = "SERVICE"


class Environment(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-mwaa.Environment",
):
    '''Represents an MWAA environment.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        airflow_version: builtins.str,
        dag_storage: DagStorage,
        name: builtins.str,
        sizing: "Sizing",
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        airflow_configuration_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        endpoint_management: typing.Optional[EndpointManagement] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        logging_configuration: typing.Optional[typing.Union["LoggingConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        webserver_access_mode: typing.Optional["WebserverAccessMode"] = None,
        weekly_maintenance_window_start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates an MWAA environment.

        :param scope: - The scope of the construct.
        :param id: - The unique ID of the construct.
        :param airflow_version: 
        :param dag_storage: 
        :param name: 
        :param sizing: 
        :param vpc: 
        :param airflow_configuration_options: 
        :param endpoint_management: 
        :param kms_key: 
        :param logging_configuration: 
        :param security_groups: 
        :param tags: 
        :param webserver_access_mode: 
        :param weekly_maintenance_window_start: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebc587b767dfc724460675574ff2adf5d781edef0bcce6da7e68d76012bd53c2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EnvironmentProps(
            airflow_version=airflow_version,
            dag_storage=dag_storage,
            name=name,
            sizing=sizing,
            vpc=vpc,
            airflow_configuration_options=airflow_configuration_options,
            endpoint_management=endpoint_management,
            kms_key=kms_key,
            logging_configuration=logging_configuration,
            security_groups=security_groups,
            tags=tags,
            webserver_access_mode=webserver_access_mode,
            weekly_maintenance_window_start=weekly_maintenance_window_start,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> None:
        '''Adds a policy statement to the execution role's policy.

        :param statement: - The IAM policy statement to add to the role's policy.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0979be1ca1dd29bc506f750b97db2634a5864c9d6ab41e834a41ad36343c373)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(None, jsii.invoke(self, "addToRolePolicy", [statement]))

    @jsii.member(jsii_name="enableEmailBackend")
    def enable_email_backend(
        self,
        *,
        from_email: builtins.str,
        conn_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Enables the email backend for Airflow to send email notifications.

        :param from_email: 
        :param conn_id: 
        '''
        options = EmailBackendOptions(from_email=from_email, conn_id=conn_id)

        return typing.cast(None, jsii.invoke(self, "enableEmailBackend", [options]))

    @jsii.member(jsii_name="enableSecretsBackend")
    def enable_secrets_backend(
        self,
        *,
        connections_lookup_pattern: typing.Optional[builtins.str] = None,
        connections_prefix: typing.Optional[builtins.str] = None,
        variables_lookup_pattern: typing.Optional[builtins.str] = None,
        variables_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Enables the use of AWS Secrets Manager as a backend for storing Airflow connections and variables.

        :param connections_lookup_pattern: 
        :param connections_prefix: 
        :param variables_lookup_pattern: 
        :param variables_prefix: 
        '''
        options = SecretsBackendOptions(
            connections_lookup_pattern=connections_lookup_pattern,
            connections_prefix=connections_prefix,
            variables_lookup_pattern=variables_lookup_pattern,
            variables_prefix=variables_prefix,
        )

        return typing.cast(None, jsii.invoke(self, "enableSecretsBackend", [options]))

    @jsii.member(jsii_name="setAirflowConfigurationOption")
    def set_airflow_configuration_option(
        self,
        key: builtins.str,
        value: typing.Any,
    ) -> None:
        '''Sets an Airflow configuration option.

        :param key: - The configuration option key.
        :param value: - The configuration option value.

        :return: void
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b9f30a55d827570e6513bf50541c7cfa225d4591c531a693874230f8932899e)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "setAirflowConfigurationOption", [key, value]))

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="celeryExecutorQueue")
    def celery_executor_queue(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "celeryExecutorQueue"))

    @builtins.property
    @jsii.member(jsii_name="dagProcessingLogsGroup")
    def dag_processing_logs_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "dagProcessingLogsGroup"))

    @builtins.property
    @jsii.member(jsii_name="databaseVpcEndpointService")
    def database_vpc_endpoint_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseVpcEndpointService"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="schedulerLogsGroup")
    def scheduler_logs_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "schedulerLogsGroup"))

    @builtins.property
    @jsii.member(jsii_name="taskLogsGroup")
    def task_logs_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "taskLogsGroup"))

    @builtins.property
    @jsii.member(jsii_name="webserverLogsGroup")
    def webserver_logs_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "webserverLogsGroup"))

    @builtins.property
    @jsii.member(jsii_name="webserverUrl")
    def webserver_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webserverUrl"))

    @builtins.property
    @jsii.member(jsii_name="webserverVpcEndpointService")
    def webserver_vpc_endpoint_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webserverVpcEndpointService"))

    @builtins.property
    @jsii.member(jsii_name="workerLogsGroup")
    def worker_logs_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "workerLogsGroup"))


@jsii.enum(jsii_type="cdk-mwaa.EnvironmentClass")
class EnvironmentClass(enum.Enum):
    '''Represents the available environment classes for MWAA (Managed Workflows for Apache Airflow).'''

    MW1_MICRO = "MW1_MICRO"
    MW1_SMALL = "MW1_SMALL"
    MW1_MEDIUM = "MW1_MEDIUM"
    MW1_LARGE = "MW1_LARGE"


@jsii.data_type(
    jsii_type="cdk-mwaa.EnvironmentProps",
    jsii_struct_bases=[],
    name_mapping={
        "airflow_version": "airflowVersion",
        "dag_storage": "dagStorage",
        "name": "name",
        "sizing": "sizing",
        "vpc": "vpc",
        "airflow_configuration_options": "airflowConfigurationOptions",
        "endpoint_management": "endpointManagement",
        "kms_key": "kmsKey",
        "logging_configuration": "loggingConfiguration",
        "security_groups": "securityGroups",
        "tags": "tags",
        "webserver_access_mode": "webserverAccessMode",
        "weekly_maintenance_window_start": "weeklyMaintenanceWindowStart",
    },
)
class EnvironmentProps:
    def __init__(
        self,
        *,
        airflow_version: builtins.str,
        dag_storage: DagStorage,
        name: builtins.str,
        sizing: "Sizing",
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        airflow_configuration_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        endpoint_management: typing.Optional[EndpointManagement] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        logging_configuration: typing.Optional[typing.Union["LoggingConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        webserver_access_mode: typing.Optional["WebserverAccessMode"] = None,
        weekly_maintenance_window_start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for creating an MWAA environment.

        :param airflow_version: 
        :param dag_storage: 
        :param name: 
        :param sizing: 
        :param vpc: 
        :param airflow_configuration_options: 
        :param endpoint_management: 
        :param kms_key: 
        :param logging_configuration: 
        :param security_groups: 
        :param tags: 
        :param webserver_access_mode: 
        :param weekly_maintenance_window_start: 
        '''
        if isinstance(logging_configuration, dict):
            logging_configuration = LoggingConfiguration(**logging_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d58cfc6f1183850b5b51999d54a17bf62c6f7b5c3c75133b721818d02e12a9b8)
            check_type(argname="argument airflow_version", value=airflow_version, expected_type=type_hints["airflow_version"])
            check_type(argname="argument dag_storage", value=dag_storage, expected_type=type_hints["dag_storage"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument sizing", value=sizing, expected_type=type_hints["sizing"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument airflow_configuration_options", value=airflow_configuration_options, expected_type=type_hints["airflow_configuration_options"])
            check_type(argname="argument endpoint_management", value=endpoint_management, expected_type=type_hints["endpoint_management"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument logging_configuration", value=logging_configuration, expected_type=type_hints["logging_configuration"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument webserver_access_mode", value=webserver_access_mode, expected_type=type_hints["webserver_access_mode"])
            check_type(argname="argument weekly_maintenance_window_start", value=weekly_maintenance_window_start, expected_type=type_hints["weekly_maintenance_window_start"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "airflow_version": airflow_version,
            "dag_storage": dag_storage,
            "name": name,
            "sizing": sizing,
            "vpc": vpc,
        }
        if airflow_configuration_options is not None:
            self._values["airflow_configuration_options"] = airflow_configuration_options
        if endpoint_management is not None:
            self._values["endpoint_management"] = endpoint_management
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if logging_configuration is not None:
            self._values["logging_configuration"] = logging_configuration
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if tags is not None:
            self._values["tags"] = tags
        if webserver_access_mode is not None:
            self._values["webserver_access_mode"] = webserver_access_mode
        if weekly_maintenance_window_start is not None:
            self._values["weekly_maintenance_window_start"] = weekly_maintenance_window_start

    @builtins.property
    def airflow_version(self) -> builtins.str:
        result = self._values.get("airflow_version")
        assert result is not None, "Required property 'airflow_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dag_storage(self) -> DagStorage:
        result = self._values.get("dag_storage")
        assert result is not None, "Required property 'dag_storage' is missing"
        return typing.cast(DagStorage, result)

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sizing(self) -> "Sizing":
        result = self._values.get("sizing")
        assert result is not None, "Required property 'sizing' is missing"
        return typing.cast("Sizing", result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def airflow_configuration_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        result = self._values.get("airflow_configuration_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def endpoint_management(self) -> typing.Optional[EndpointManagement]:
        result = self._values.get("endpoint_management")
        return typing.cast(typing.Optional[EndpointManagement], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def logging_configuration(self) -> typing.Optional["LoggingConfiguration"]:
        result = self._values.get("logging_configuration")
        return typing.cast(typing.Optional["LoggingConfiguration"], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def webserver_access_mode(self) -> typing.Optional["WebserverAccessMode"]:
        result = self._values.get("webserver_access_mode")
        return typing.cast(typing.Optional["WebserverAccessMode"], result)

    @builtins.property
    def weekly_maintenance_window_start(self) -> typing.Optional[builtins.str]:
        result = self._values.get("weekly_maintenance_window_start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnvironmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-mwaa.LogLevel")
class LogLevel(enum.Enum):
    '''Enum for the log level for Apache Airflow.'''

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


@jsii.data_type(
    jsii_type="cdk-mwaa.LoggingConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "dag_processing_logs": "dagProcessingLogs",
        "scheduler_logs": "schedulerLogs",
        "task_logs": "taskLogs",
        "webserver_logs": "webserverLogs",
        "worker_logs": "workerLogs",
    },
)
class LoggingConfiguration:
    def __init__(
        self,
        *,
        dag_processing_logs: typing.Optional[typing.Union["LoggingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]] = None,
        scheduler_logs: typing.Optional[typing.Union["LoggingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]] = None,
        task_logs: typing.Optional[typing.Union["LoggingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]] = None,
        webserver_logs: typing.Optional[typing.Union["LoggingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]] = None,
        worker_logs: typing.Optional[typing.Union["LoggingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Logging configuration for the MWAA environment.

        :param dag_processing_logs: 
        :param scheduler_logs: 
        :param task_logs: 
        :param webserver_logs: 
        :param worker_logs: 
        '''
        if isinstance(dag_processing_logs, dict):
            dag_processing_logs = LoggingConfigurationProperty(**dag_processing_logs)
        if isinstance(scheduler_logs, dict):
            scheduler_logs = LoggingConfigurationProperty(**scheduler_logs)
        if isinstance(task_logs, dict):
            task_logs = LoggingConfigurationProperty(**task_logs)
        if isinstance(webserver_logs, dict):
            webserver_logs = LoggingConfigurationProperty(**webserver_logs)
        if isinstance(worker_logs, dict):
            worker_logs = LoggingConfigurationProperty(**worker_logs)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e2c2b7229af680332026a2523648e1c7f223df1a7e4c0c75768ae0221551c16)
            check_type(argname="argument dag_processing_logs", value=dag_processing_logs, expected_type=type_hints["dag_processing_logs"])
            check_type(argname="argument scheduler_logs", value=scheduler_logs, expected_type=type_hints["scheduler_logs"])
            check_type(argname="argument task_logs", value=task_logs, expected_type=type_hints["task_logs"])
            check_type(argname="argument webserver_logs", value=webserver_logs, expected_type=type_hints["webserver_logs"])
            check_type(argname="argument worker_logs", value=worker_logs, expected_type=type_hints["worker_logs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dag_processing_logs is not None:
            self._values["dag_processing_logs"] = dag_processing_logs
        if scheduler_logs is not None:
            self._values["scheduler_logs"] = scheduler_logs
        if task_logs is not None:
            self._values["task_logs"] = task_logs
        if webserver_logs is not None:
            self._values["webserver_logs"] = webserver_logs
        if worker_logs is not None:
            self._values["worker_logs"] = worker_logs

    @builtins.property
    def dag_processing_logs(self) -> typing.Optional["LoggingConfigurationProperty"]:
        result = self._values.get("dag_processing_logs")
        return typing.cast(typing.Optional["LoggingConfigurationProperty"], result)

    @builtins.property
    def scheduler_logs(self) -> typing.Optional["LoggingConfigurationProperty"]:
        result = self._values.get("scheduler_logs")
        return typing.cast(typing.Optional["LoggingConfigurationProperty"], result)

    @builtins.property
    def task_logs(self) -> typing.Optional["LoggingConfigurationProperty"]:
        result = self._values.get("task_logs")
        return typing.cast(typing.Optional["LoggingConfigurationProperty"], result)

    @builtins.property
    def webserver_logs(self) -> typing.Optional["LoggingConfigurationProperty"]:
        result = self._values.get("webserver_logs")
        return typing.cast(typing.Optional["LoggingConfigurationProperty"], result)

    @builtins.property
    def worker_logs(self) -> typing.Optional["LoggingConfigurationProperty"]:
        result = self._values.get("worker_logs")
        return typing.cast(typing.Optional["LoggingConfigurationProperty"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoggingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-mwaa.LoggingConfigurationProperty",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "log_level": "logLevel",
        "retention": "retention",
    },
)
class LoggingConfigurationProperty:
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        log_level: typing.Optional[LogLevel] = None,
        retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    ) -> None:
        '''Defines the logging configuration properties for various Airflow log types.

        :param enabled: Indicates whether to enable the Apache Airflow log type (e.g., DagProcessingLogs) in CloudWatch Logs.
        :param log_level: Defines the log level for the specified log type (e.g., DagProcessingLogs). Valid values: CRITICAL, ERROR, WARNING, INFO, DEBUG.
        :param retention: Specifies the retention period for the log group in Amazon CloudWatch Logs. Determines how long the logs should be kept before being automatically deleted.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36e478654aa87904502c267bca96d1a7c0ca8f8e5e749464cb92a7cd1fd2c4b0)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument log_level", value=log_level, expected_type=type_hints["log_level"])
            check_type(argname="argument retention", value=retention, expected_type=type_hints["retention"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if log_level is not None:
            self._values["log_level"] = log_level
        if retention is not None:
            self._values["retention"] = retention

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether to enable the Apache Airflow log type (e.g., DagProcessingLogs) in CloudWatch Logs.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def log_level(self) -> typing.Optional[LogLevel]:
        '''Defines the log level for the specified log type (e.g., DagProcessingLogs). Valid values: CRITICAL, ERROR, WARNING, INFO, DEBUG.'''
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[LogLevel], result)

    @builtins.property
    def retention(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''Specifies the retention period for the log group in Amazon CloudWatch Logs.

        Determines how long the logs should be kept before being automatically deleted.
        '''
        result = self._values.get("retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoggingConfigurationProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-mwaa.MWAAProps",
    jsii_struct_bases=[],
    name_mapping={
        "airflow_version": "airflowVersion",
        "environment_name": "environmentName",
        "airflow_configuration_options": "airflowConfigurationOptions",
        "bucket_name": "bucketName",
        "configs_options": "configsOptions",
        "dags_options": "dagsOptions",
        "removal_policy": "removalPolicy",
        "sizing": "sizing",
        "vpc": "vpc",
    },
)
class MWAAProps:
    def __init__(
        self,
        *,
        airflow_version: builtins.str,
        environment_name: builtins.str,
        airflow_configuration_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        configs_options: typing.Optional[typing.Union[ConfigsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        dags_options: typing.Optional[typing.Union[DagsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        sizing: typing.Optional["Sizing"] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Interface defining the properties for configuring MWAA (Managed Airflow).

        :param airflow_version: The version of Airflow to deploy.
        :param environment_name: The name of the Airflow environment.
        :param airflow_configuration_options: Airflow configuration options as key-value pairs. These configuration options are passed to the Airflow environment.
        :param bucket_name: The name of the S3 bucket used for storing DAGs. If not provided, a default bucket is created.
        :param configs_options: Configuration for plugins storage.
        :param dags_options: Configuration for DAG storage.
        :param removal_policy: The removal policy for the MWAA resources. Determines what happens to the resources when they are deleted. Defaults to 'RETAIN' if not specified.
        :param sizing: Optional sizing configuration for the MWAA environment. Defines the compute resources.
        :param vpc: The VPC in which to deploy the MWAA environment. If not provided, a default VPC will be created.
        '''
        if isinstance(configs_options, dict):
            configs_options = ConfigsOptions(**configs_options)
        if isinstance(dags_options, dict):
            dags_options = DagsOptions(**dags_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e73d818937427f32bb22179ff7d13eb6aa0201131959780924f6ec21b94dd128)
            check_type(argname="argument airflow_version", value=airflow_version, expected_type=type_hints["airflow_version"])
            check_type(argname="argument environment_name", value=environment_name, expected_type=type_hints["environment_name"])
            check_type(argname="argument airflow_configuration_options", value=airflow_configuration_options, expected_type=type_hints["airflow_configuration_options"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument configs_options", value=configs_options, expected_type=type_hints["configs_options"])
            check_type(argname="argument dags_options", value=dags_options, expected_type=type_hints["dags_options"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument sizing", value=sizing, expected_type=type_hints["sizing"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "airflow_version": airflow_version,
            "environment_name": environment_name,
        }
        if airflow_configuration_options is not None:
            self._values["airflow_configuration_options"] = airflow_configuration_options
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if configs_options is not None:
            self._values["configs_options"] = configs_options
        if dags_options is not None:
            self._values["dags_options"] = dags_options
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if sizing is not None:
            self._values["sizing"] = sizing
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def airflow_version(self) -> builtins.str:
        '''The version of Airflow to deploy.'''
        result = self._values.get("airflow_version")
        assert result is not None, "Required property 'airflow_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def environment_name(self) -> builtins.str:
        '''The name of the Airflow environment.'''
        result = self._values.get("environment_name")
        assert result is not None, "Required property 'environment_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def airflow_configuration_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Airflow configuration options as key-value pairs.

        These configuration options are passed to the Airflow environment.
        '''
        result = self._values.get("airflow_configuration_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''The name of the S3 bucket used for storing DAGs.

        If not provided, a default bucket is created.
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def configs_options(self) -> typing.Optional[ConfigsOptions]:
        '''Configuration for plugins storage.'''
        result = self._values.get("configs_options")
        return typing.cast(typing.Optional[ConfigsOptions], result)

    @builtins.property
    def dags_options(self) -> typing.Optional[DagsOptions]:
        '''Configuration for DAG storage.'''
        result = self._values.get("dags_options")
        return typing.cast(typing.Optional[DagsOptions], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy for the MWAA resources.

        Determines what happens to the resources when they are deleted.
        Defaults to 'RETAIN' if not specified.
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def sizing(self) -> typing.Optional["Sizing"]:
        '''Optional sizing configuration for the MWAA environment.

        Defines the compute resources.
        '''
        result = self._values.get("sizing")
        return typing.cast(typing.Optional["Sizing"], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC in which to deploy the MWAA environment.

        If not provided, a default VPC will be created.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MWAAProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PrivateRoutingVpc(
    BaseVpc,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-mwaa.PrivateRoutingVpc",
):
    '''A VPC with only private isolated subnets, intended for internal workloads.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        subnet_cidr_mask: typing.Optional[jsii.Number] = None,
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        vpc_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param subnet_cidr_mask: CIDR mask size for subnets.
        :param ip_addresses: IP address allocation strategy for the VPC.
        :param nat_gateways: Number of NAT gateways to create.
        :param vpc_name: Optional name for the VPC.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c73ed3944fc6b46a3f86d85ff5f840bb8271f57e5ac4500ccb58913c1f2a4fe5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PrivateRoutingVpcProps(
            subnet_cidr_mask=subnet_cidr_mask,
            ip_addresses=ip_addresses,
            nat_gateways=nat_gateways,
            vpc_name=vpc_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="kmsVpcEndpoint")
    def kms_vpc_endpoint(self) -> _aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpoint:
        '''Interface VPC Endpoint for KMS.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpoint, jsii.get(self, "kmsVpcEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="logsVpcEndpoint")
    def logs_vpc_endpoint(self) -> _aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpoint:
        '''Interface VPC Endpoint for CloudWatch Logs.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpoint, jsii.get(self, "logsVpcEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="monitoringVpcEndpoint")
    def monitoring_vpc_endpoint(self) -> _aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpoint:
        '''Interface VPC Endpoint for CloudWatch Monitoring.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpoint, jsii.get(self, "monitoringVpcEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="sqsVpcEndpoint")
    def sqs_vpc_endpoint(self) -> _aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpoint:
        '''Interface VPC Endpoint for SQS.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpoint, jsii.get(self, "sqsVpcEndpoint"))


@jsii.data_type(
    jsii_type="cdk-mwaa.PrivateRoutingVpcProps",
    jsii_struct_bases=[CommonVpcProps],
    name_mapping={
        "ip_addresses": "ipAddresses",
        "nat_gateways": "natGateways",
        "vpc_name": "vpcName",
        "subnet_cidr_mask": "subnetCidrMask",
    },
)
class PrivateRoutingVpcProps(CommonVpcProps):
    def __init__(
        self,
        *,
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        vpc_name: typing.Optional[builtins.str] = None,
        subnet_cidr_mask: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Properties for a private-routing VPC.

        :param ip_addresses: IP address allocation strategy for the VPC.
        :param nat_gateways: Number of NAT gateways to create.
        :param vpc_name: Optional name for the VPC.
        :param subnet_cidr_mask: CIDR mask size for subnets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abb7d9fedfeb8de5ea1c1fe17c4e16a596ae22d34807b9aebb1945cd6b11871e)
            check_type(argname="argument ip_addresses", value=ip_addresses, expected_type=type_hints["ip_addresses"])
            check_type(argname="argument nat_gateways", value=nat_gateways, expected_type=type_hints["nat_gateways"])
            check_type(argname="argument vpc_name", value=vpc_name, expected_type=type_hints["vpc_name"])
            check_type(argname="argument subnet_cidr_mask", value=subnet_cidr_mask, expected_type=type_hints["subnet_cidr_mask"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if nat_gateways is not None:
            self._values["nat_gateways"] = nat_gateways
        if vpc_name is not None:
            self._values["vpc_name"] = vpc_name
        if subnet_cidr_mask is not None:
            self._values["subnet_cidr_mask"] = subnet_cidr_mask

    @builtins.property
    def ip_addresses(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses]:
        '''IP address allocation strategy for the VPC.'''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses], result)

    @builtins.property
    def nat_gateways(self) -> typing.Optional[jsii.Number]:
        '''Number of NAT gateways to create.'''
        result = self._values.get("nat_gateways")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc_name(self) -> typing.Optional[builtins.str]:
        '''Optional name for the VPC.'''
        result = self._values.get("vpc_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet_cidr_mask(self) -> typing.Optional[jsii.Number]:
        '''CIDR mask size for subnets.'''
        result = self._values.get("subnet_cidr_mask")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrivateRoutingVpcProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PublicRoutingMWAA(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-mwaa.PublicRoutingMWAA",
):
    '''PublicRoutingMWAA constructs a Managed Airflow (MWAA) environment with public webserver access.

    It creates the necessary VPC, S3 storage for DAGs, and an Airflow environment.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        airflow_version: builtins.str,
        environment_name: builtins.str,
        airflow_configuration_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        configs_options: typing.Optional[typing.Union[ConfigsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        dags_options: typing.Optional[typing.Union[DagsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        sizing: typing.Optional["Sizing"] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param airflow_version: The version of Airflow to deploy.
        :param environment_name: The name of the Airflow environment.
        :param airflow_configuration_options: Airflow configuration options as key-value pairs. These configuration options are passed to the Airflow environment.
        :param bucket_name: The name of the S3 bucket used for storing DAGs. If not provided, a default bucket is created.
        :param configs_options: Configuration for plugins storage.
        :param dags_options: Configuration for DAG storage.
        :param removal_policy: The removal policy for the MWAA resources. Determines what happens to the resources when they are deleted. Defaults to 'RETAIN' if not specified.
        :param sizing: Optional sizing configuration for the MWAA environment. Defines the compute resources.
        :param vpc: The VPC in which to deploy the MWAA environment. If not provided, a default VPC will be created.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5715af45a5664383ddb469b7bffe2c8a7d75c3dfe608847aae4c9fd79f034c9e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MWAAProps(
            airflow_version=airflow_version,
            environment_name=environment_name,
            airflow_configuration_options=airflow_configuration_options,
            bucket_name=bucket_name,
            configs_options=configs_options,
            dags_options=dags_options,
            removal_policy=removal_policy,
            sizing=sizing,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class PublicRoutingVpc(
    BaseVpc,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-mwaa.PublicRoutingVpc",
):
    '''A VPC with public and private subnets, supporting internet access.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        subnet_cidr_mask: typing.Optional[jsii.Number] = None,
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        vpc_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param subnet_cidr_mask: CIDR mask size for subnets.
        :param ip_addresses: IP address allocation strategy for the VPC.
        :param nat_gateways: Number of NAT gateways to create.
        :param vpc_name: Optional name for the VPC.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1457f60cd9471b72ac15c6a135c3d32d6e6da4212ded7d4bab5ce7dbc54f545b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PublicRoutingVpcProps(
            subnet_cidr_mask=subnet_cidr_mask,
            ip_addresses=ip_addresses,
            nat_gateways=nat_gateways,
            vpc_name=vpc_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-mwaa.PublicRoutingVpcProps",
    jsii_struct_bases=[CommonVpcProps],
    name_mapping={
        "ip_addresses": "ipAddresses",
        "nat_gateways": "natGateways",
        "vpc_name": "vpcName",
        "subnet_cidr_mask": "subnetCidrMask",
    },
)
class PublicRoutingVpcProps(CommonVpcProps):
    def __init__(
        self,
        *,
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        vpc_name: typing.Optional[builtins.str] = None,
        subnet_cidr_mask: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Properties for a public-routing VPC.

        :param ip_addresses: IP address allocation strategy for the VPC.
        :param nat_gateways: Number of NAT gateways to create.
        :param vpc_name: Optional name for the VPC.
        :param subnet_cidr_mask: CIDR mask size for subnets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bad12722757576263840116af2af2fd609cfd2cf55cf7c60a41c0f39c43e9ca1)
            check_type(argname="argument ip_addresses", value=ip_addresses, expected_type=type_hints["ip_addresses"])
            check_type(argname="argument nat_gateways", value=nat_gateways, expected_type=type_hints["nat_gateways"])
            check_type(argname="argument vpc_name", value=vpc_name, expected_type=type_hints["vpc_name"])
            check_type(argname="argument subnet_cidr_mask", value=subnet_cidr_mask, expected_type=type_hints["subnet_cidr_mask"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if nat_gateways is not None:
            self._values["nat_gateways"] = nat_gateways
        if vpc_name is not None:
            self._values["vpc_name"] = vpc_name
        if subnet_cidr_mask is not None:
            self._values["subnet_cidr_mask"] = subnet_cidr_mask

    @builtins.property
    def ip_addresses(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses]:
        '''IP address allocation strategy for the VPC.'''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses], result)

    @builtins.property
    def nat_gateways(self) -> typing.Optional[jsii.Number]:
        '''Number of NAT gateways to create.'''
        result = self._values.get("nat_gateways")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc_name(self) -> typing.Optional[builtins.str]:
        '''Optional name for the VPC.'''
        result = self._values.get("vpc_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet_cidr_mask(self) -> typing.Optional[jsii.Number]:
        '''CIDR mask size for subnets.'''
        result = self._values.get("subnet_cidr_mask")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PublicRoutingVpcProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-mwaa.SecretsBackendOptions",
    jsii_struct_bases=[],
    name_mapping={
        "connections_lookup_pattern": "connectionsLookupPattern",
        "connections_prefix": "connectionsPrefix",
        "variables_lookup_pattern": "variablesLookupPattern",
        "variables_prefix": "variablesPrefix",
    },
)
class SecretsBackendOptions:
    def __init__(
        self,
        *,
        connections_lookup_pattern: typing.Optional[builtins.str] = None,
        connections_prefix: typing.Optional[builtins.str] = None,
        variables_lookup_pattern: typing.Optional[builtins.str] = None,
        variables_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Options for configuring the Secrets backend.

        :param connections_lookup_pattern: 
        :param connections_prefix: 
        :param variables_lookup_pattern: 
        :param variables_prefix: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4a26a4745b2f3c0bf73fea3716d2c2582a993bce95da0be81eb790bf091aa13)
            check_type(argname="argument connections_lookup_pattern", value=connections_lookup_pattern, expected_type=type_hints["connections_lookup_pattern"])
            check_type(argname="argument connections_prefix", value=connections_prefix, expected_type=type_hints["connections_prefix"])
            check_type(argname="argument variables_lookup_pattern", value=variables_lookup_pattern, expected_type=type_hints["variables_lookup_pattern"])
            check_type(argname="argument variables_prefix", value=variables_prefix, expected_type=type_hints["variables_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connections_lookup_pattern is not None:
            self._values["connections_lookup_pattern"] = connections_lookup_pattern
        if connections_prefix is not None:
            self._values["connections_prefix"] = connections_prefix
        if variables_lookup_pattern is not None:
            self._values["variables_lookup_pattern"] = variables_lookup_pattern
        if variables_prefix is not None:
            self._values["variables_prefix"] = variables_prefix

    @builtins.property
    def connections_lookup_pattern(self) -> typing.Optional[builtins.str]:
        result = self._values.get("connections_lookup_pattern")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connections_prefix(self) -> typing.Optional[builtins.str]:
        result = self._values.get("connections_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def variables_lookup_pattern(self) -> typing.Optional[builtins.str]:
        result = self._values.get("variables_lookup_pattern")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def variables_prefix(self) -> typing.Optional[builtins.str]:
        result = self._values.get("variables_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretsBackendOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityGroup(
    _aws_cdk_aws_ec2_ceddda9d.SecurityGroup,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-mwaa.SecurityGroup",
):
    '''A custom Security Group with a self-referencing ingress rule for MWAA.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        disable_inline_rules: typing.Optional[builtins.bool] = None,
        security_group_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates a new Security Group with self-referencing ingress rules.

        :param scope: The parent construct.
        :param id: The unique identifier for this construct.
        :param vpc: The VPC in which to create the security group.
        :param allow_all_ipv6_outbound: Whether to allow all outbound ipv6 traffic by default. If this is set to true, there will only be a single egress rule which allows all outbound ipv6 traffic. If this is set to false, no outbound traffic will be allowed by default and all egress ipv6 traffic must be explicitly authorized. To allow all ipv4 traffic use allowAllOutbound Default: false
        :param allow_all_outbound: Whether to allow all outbound traffic by default. If this is set to true, there will only be a single egress rule which allows all outbound traffic. If this is set to false, no outbound traffic will be allowed by default and all egress traffic must be explicitly authorized. To allow all ipv6 traffic use allowAllIpv6Outbound Default: true
        :param description: A description of the security group. Default: The default name will be the construct's CDK path.
        :param disable_inline_rules: Whether to disable inline ingress and egress rule optimization. If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements. Inlining rules is an optimization for producing smaller stack templates. Sometimes this is not desirable, for example when security group access is managed via tags. The default value can be overridden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'. Default: false
        :param security_group_name: The name of the security group. For valid values, see the GroupName parameter of the CreateSecurityGroup action in the Amazon EC2 API Reference. It is not recommended to use an explicit group name. Default: If you don't specify a GroupName, AWS CloudFormation generates a unique physical ID and uses that ID for the group name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0c0edc0cc9086762fba282b3b093245709fb50595ba3be1a94386b8ffc61a0b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SecurityGroupProps(
            vpc=vpc,
            allow_all_ipv6_outbound=allow_all_ipv6_outbound,
            allow_all_outbound=allow_all_outbound,
            description=description,
            disable_inline_rules=disable_inline_rules,
            security_group_name=security_group_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-mwaa.SecurityGroupProps",
    jsii_struct_bases=[_aws_cdk_aws_ec2_ceddda9d.SecurityGroupProps],
    name_mapping={
        "vpc": "vpc",
        "allow_all_ipv6_outbound": "allowAllIpv6Outbound",
        "allow_all_outbound": "allowAllOutbound",
        "description": "description",
        "disable_inline_rules": "disableInlineRules",
        "security_group_name": "securityGroupName",
    },
)
class SecurityGroupProps(_aws_cdk_aws_ec2_ceddda9d.SecurityGroupProps):
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        disable_inline_rules: typing.Optional[builtins.bool] = None,
        security_group_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a Security Group.

        :param vpc: The VPC in which to create the security group.
        :param allow_all_ipv6_outbound: Whether to allow all outbound ipv6 traffic by default. If this is set to true, there will only be a single egress rule which allows all outbound ipv6 traffic. If this is set to false, no outbound traffic will be allowed by default and all egress ipv6 traffic must be explicitly authorized. To allow all ipv4 traffic use allowAllOutbound Default: false
        :param allow_all_outbound: Whether to allow all outbound traffic by default. If this is set to true, there will only be a single egress rule which allows all outbound traffic. If this is set to false, no outbound traffic will be allowed by default and all egress traffic must be explicitly authorized. To allow all ipv6 traffic use allowAllIpv6Outbound Default: true
        :param description: A description of the security group. Default: The default name will be the construct's CDK path.
        :param disable_inline_rules: Whether to disable inline ingress and egress rule optimization. If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements. Inlining rules is an optimization for producing smaller stack templates. Sometimes this is not desirable, for example when security group access is managed via tags. The default value can be overridden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'. Default: false
        :param security_group_name: The name of the security group. For valid values, see the GroupName parameter of the CreateSecurityGroup action in the Amazon EC2 API Reference. It is not recommended to use an explicit group name. Default: If you don't specify a GroupName, AWS CloudFormation generates a unique physical ID and uses that ID for the group name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cc85564bef1cef94bed0ad8e10d0c4a5b9d253034b927359a0c50ae7fbafa03)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument allow_all_ipv6_outbound", value=allow_all_ipv6_outbound, expected_type=type_hints["allow_all_ipv6_outbound"])
            check_type(argname="argument allow_all_outbound", value=allow_all_outbound, expected_type=type_hints["allow_all_outbound"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disable_inline_rules", value=disable_inline_rules, expected_type=type_hints["disable_inline_rules"])
            check_type(argname="argument security_group_name", value=security_group_name, expected_type=type_hints["security_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }
        if allow_all_ipv6_outbound is not None:
            self._values["allow_all_ipv6_outbound"] = allow_all_ipv6_outbound
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if description is not None:
            self._values["description"] = description
        if disable_inline_rules is not None:
            self._values["disable_inline_rules"] = disable_inline_rules
        if security_group_name is not None:
            self._values["security_group_name"] = security_group_name

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC in which to create the security group.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def allow_all_ipv6_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow all outbound ipv6 traffic by default.

        If this is set to true, there will only be a single egress rule which allows all
        outbound ipv6 traffic. If this is set to false, no outbound traffic will be allowed by
        default and all egress ipv6 traffic must be explicitly authorized.

        To allow all ipv4 traffic use allowAllOutbound

        :default: false
        '''
        result = self._values.get("allow_all_ipv6_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow all outbound traffic by default.

        If this is set to true, there will only be a single egress rule which allows all
        outbound traffic. If this is set to false, no outbound traffic will be allowed by
        default and all egress traffic must be explicitly authorized.

        To allow all ipv6 traffic use allowAllIpv6Outbound

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the security group.

        :default: The default name will be the construct's CDK path.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_inline_rules(self) -> typing.Optional[builtins.bool]:
        '''Whether to disable inline ingress and egress rule optimization.

        If this is set to true, ingress and egress rules will not be declared under the
        SecurityGroup in cloudformation, but will be separate elements.

        Inlining rules is an optimization for producing smaller stack templates. Sometimes
        this is not desirable, for example when security group access is managed via tags.

        The default value can be overridden globally by setting the context variable
        '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'.

        :default: false
        '''
        result = self._values.get("disable_inline_rules")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_group_name(self) -> typing.Optional[builtins.str]:
        '''The name of the security group.

        For valid values, see the GroupName
        parameter of the CreateSecurityGroup action in the Amazon EC2 API
        Reference.

        It is not recommended to use an explicit group name.

        :default:

        If you don't specify a GroupName, AWS CloudFormation generates a
        unique physical ID and uses that ID for the group name.
        '''
        result = self._values.get("security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Sizing(metaclass=jsii.JSIIMeta, jsii_type="cdk-mwaa.Sizing"):
    '''Provides predefined and customizable sizing options for an MWAA environment.'''

    @jsii.member(jsii_name="custom")
    @builtins.classmethod
    def custom(
        cls,
        *,
        environment_class: EnvironmentClass,
        max_webservers: jsii.Number,
        max_workers: jsii.Number,
        min_webservers: jsii.Number,
        min_workers: jsii.Number,
        schedulers: jsii.Number,
    ) -> "Sizing":
        '''Creates a custom-sized MWAA environment based on user-defined configuration.

        :param environment_class: The environment class determining the available resources.
        :param max_webservers: Maximum number of webservers in the MWAA environment.
        :param max_workers: Maximum number of workers in the MWAA environment.
        :param min_webservers: Minimum number of webservers in the MWAA environment.
        :param min_workers: Minimum number of workers in the MWAA environment.
        :param schedulers: Number of schedulers in the MWAA environment.
        '''
        config = SizingProps(
            environment_class=environment_class,
            max_webservers=max_webservers,
            max_workers=max_workers,
            min_webservers=min_webservers,
            min_workers=min_workers,
            schedulers=schedulers,
        )

        return typing.cast("Sizing", jsii.sinvoke(cls, "custom", [config]))

    @jsii.member(jsii_name="mw1Large")
    @builtins.classmethod
    def mw1_large(cls) -> "Sizing":
        '''Creates an MW1_LARGE sized environment with a predefined range of workers and webservers.'''
        return typing.cast("Sizing", jsii.sinvoke(cls, "mw1Large", []))

    @jsii.member(jsii_name="mw1Medium")
    @builtins.classmethod
    def mw1_medium(cls) -> "Sizing":
        '''Creates an MW1_MEDIUM sized environment with a predefined range of workers and webservers.'''
        return typing.cast("Sizing", jsii.sinvoke(cls, "mw1Medium", []))

    @jsii.member(jsii_name="mw1Micro")
    @builtins.classmethod
    def mw1_micro(cls) -> "Sizing":
        '''Creates an MW1_MICRO sized environment with a single worker, webserver, and scheduler.'''
        return typing.cast("Sizing", jsii.sinvoke(cls, "mw1Micro", []))

    @jsii.member(jsii_name="mw1Small")
    @builtins.classmethod
    def mw1_small(cls) -> "Sizing":
        '''Creates an MW1_SMALL sized environment with a predefined range of workers and webservers.'''
        return typing.cast("Sizing", jsii.sinvoke(cls, "mw1Small", []))

    @builtins.property
    @jsii.member(jsii_name="environmentClass")
    def environment_class(self) -> EnvironmentClass:
        '''Returns the environment class.'''
        return typing.cast(EnvironmentClass, jsii.get(self, "environmentClass"))

    @builtins.property
    @jsii.member(jsii_name="maxWebservers")
    def max_webservers(self) -> jsii.Number:
        '''Returns the maximum number of webservers.'''
        return typing.cast(jsii.Number, jsii.get(self, "maxWebservers"))

    @builtins.property
    @jsii.member(jsii_name="maxWorkers")
    def max_workers(self) -> jsii.Number:
        '''Returns the maximum number of workers.'''
        return typing.cast(jsii.Number, jsii.get(self, "maxWorkers"))

    @builtins.property
    @jsii.member(jsii_name="minWebservers")
    def min_webservers(self) -> jsii.Number:
        '''Returns the minimum number of webservers.'''
        return typing.cast(jsii.Number, jsii.get(self, "minWebservers"))

    @builtins.property
    @jsii.member(jsii_name="minWorkers")
    def min_workers(self) -> jsii.Number:
        '''Returns the minimum number of workers.'''
        return typing.cast(jsii.Number, jsii.get(self, "minWorkers"))

    @builtins.property
    @jsii.member(jsii_name="schedulers")
    def schedulers(self) -> jsii.Number:
        '''Returns the number of schedulers.'''
        return typing.cast(jsii.Number, jsii.get(self, "schedulers"))


@jsii.data_type(
    jsii_type="cdk-mwaa.SizingProps",
    jsii_struct_bases=[],
    name_mapping={
        "environment_class": "environmentClass",
        "max_webservers": "maxWebservers",
        "max_workers": "maxWorkers",
        "min_webservers": "minWebservers",
        "min_workers": "minWorkers",
        "schedulers": "schedulers",
    },
)
class SizingProps:
    def __init__(
        self,
        *,
        environment_class: EnvironmentClass,
        max_webservers: jsii.Number,
        max_workers: jsii.Number,
        min_webservers: jsii.Number,
        min_workers: jsii.Number,
        schedulers: jsii.Number,
    ) -> None:
        '''Defines the configuration properties for sizing an MWAA environment.

        :param environment_class: The environment class determining the available resources.
        :param max_webservers: Maximum number of webservers in the MWAA environment.
        :param max_workers: Maximum number of workers in the MWAA environment.
        :param min_webservers: Minimum number of webservers in the MWAA environment.
        :param min_workers: Minimum number of workers in the MWAA environment.
        :param schedulers: Number of schedulers in the MWAA environment.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__379e3b2e8fe393bf82766c342457e207198846f531bd3cef817a10a9a171a08d)
            check_type(argname="argument environment_class", value=environment_class, expected_type=type_hints["environment_class"])
            check_type(argname="argument max_webservers", value=max_webservers, expected_type=type_hints["max_webservers"])
            check_type(argname="argument max_workers", value=max_workers, expected_type=type_hints["max_workers"])
            check_type(argname="argument min_webservers", value=min_webservers, expected_type=type_hints["min_webservers"])
            check_type(argname="argument min_workers", value=min_workers, expected_type=type_hints["min_workers"])
            check_type(argname="argument schedulers", value=schedulers, expected_type=type_hints["schedulers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "environment_class": environment_class,
            "max_webservers": max_webservers,
            "max_workers": max_workers,
            "min_webservers": min_webservers,
            "min_workers": min_workers,
            "schedulers": schedulers,
        }

    @builtins.property
    def environment_class(self) -> EnvironmentClass:
        '''The environment class determining the available resources.'''
        result = self._values.get("environment_class")
        assert result is not None, "Required property 'environment_class' is missing"
        return typing.cast(EnvironmentClass, result)

    @builtins.property
    def max_webservers(self) -> jsii.Number:
        '''Maximum number of webservers in the MWAA environment.'''
        result = self._values.get("max_webservers")
        assert result is not None, "Required property 'max_webservers' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def max_workers(self) -> jsii.Number:
        '''Maximum number of workers in the MWAA environment.'''
        result = self._values.get("max_workers")
        assert result is not None, "Required property 'max_workers' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_webservers(self) -> jsii.Number:
        '''Minimum number of webservers in the MWAA environment.'''
        result = self._values.get("min_webservers")
        assert result is not None, "Required property 'min_webservers' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_workers(self) -> jsii.Number:
        '''Minimum number of workers in the MWAA environment.'''
        result = self._values.get("min_workers")
        assert result is not None, "Required property 'min_workers' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def schedulers(self) -> jsii.Number:
        '''Number of schedulers in the MWAA environment.'''
        result = self._values.get("schedulers")
        assert result is not None, "Required property 'schedulers' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SizingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-mwaa.WebserverAccessMode")
class WebserverAccessMode(enum.Enum):
    '''Enum for the webserver access mode of the MWAA environment.'''

    PRIVATE_ONLY = "PRIVATE_ONLY"
    PUBLIC_ONLY = "PUBLIC_ONLY"


class AirflowPool(
    AirflowResourceBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-mwaa.AirflowPool",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        environment: Environment,
        pool_name: builtins.str,
        pool_description: typing.Optional[builtins.str] = None,
        pool_slots: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param environment: 
        :param pool_name: 
        :param pool_description: 
        :param pool_slots: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a87ff3b6f71f463c250df83cf9fd051ffc2d598fc9199d37ac367d525c389523)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AirflowPoolProps(
            environment=environment,
            pool_name=pool_name,
            pool_description=pool_description,
            pool_slots=pool_slots,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-mwaa.BaseVpcProps",
    jsii_struct_bases=[CommonVpcProps],
    name_mapping={
        "ip_addresses": "ipAddresses",
        "nat_gateways": "natGateways",
        "vpc_name": "vpcName",
        "create_internet_gateway": "createInternetGateway",
        "subnet_configuration": "subnetConfiguration",
    },
)
class BaseVpcProps(CommonVpcProps):
    def __init__(
        self,
        *,
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        vpc_name: typing.Optional[builtins.str] = None,
        create_internet_gateway: builtins.bool,
        subnet_configuration: typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''Properties for creating a base VPC.

        :param ip_addresses: IP address allocation strategy for the VPC.
        :param nat_gateways: Number of NAT gateways to create.
        :param vpc_name: Optional name for the VPC.
        :param create_internet_gateway: Whether to create an Internet Gateway for public access.
        :param subnet_configuration: Subnet configuration for the VPC.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37b318e855026c52b2d51a58b8910511f891b4cb049f49619d4309af57a3e4f4)
            check_type(argname="argument ip_addresses", value=ip_addresses, expected_type=type_hints["ip_addresses"])
            check_type(argname="argument nat_gateways", value=nat_gateways, expected_type=type_hints["nat_gateways"])
            check_type(argname="argument vpc_name", value=vpc_name, expected_type=type_hints["vpc_name"])
            check_type(argname="argument create_internet_gateway", value=create_internet_gateway, expected_type=type_hints["create_internet_gateway"])
            check_type(argname="argument subnet_configuration", value=subnet_configuration, expected_type=type_hints["subnet_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "create_internet_gateway": create_internet_gateway,
            "subnet_configuration": subnet_configuration,
        }
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if nat_gateways is not None:
            self._values["nat_gateways"] = nat_gateways
        if vpc_name is not None:
            self._values["vpc_name"] = vpc_name

    @builtins.property
    def ip_addresses(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses]:
        '''IP address allocation strategy for the VPC.'''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses], result)

    @builtins.property
    def nat_gateways(self) -> typing.Optional[jsii.Number]:
        '''Number of NAT gateways to create.'''
        result = self._values.get("nat_gateways")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc_name(self) -> typing.Optional[builtins.str]:
        '''Optional name for the VPC.'''
        result = self._values.get("vpc_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_internet_gateway(self) -> builtins.bool:
        '''Whether to create an Internet Gateway for public access.'''
        result = self._values.get("create_internet_gateway")
        assert result is not None, "Required property 'create_internet_gateway' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def subnet_configuration(
        self,
    ) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration]:
        '''Subnet configuration for the VPC.'''
        result = self._values.get("subnet_configuration")
        assert result is not None, "Required property 'subnet_configuration' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseVpcProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AirflowPool",
    "AirflowPoolProps",
    "AirflowResourceBase",
    "AirflowResourceBaseProps",
    "BaseVpc",
    "BaseVpcProps",
    "CommonVpcProps",
    "ConfigFile",
    "ConfigsOptions",
    "DagStorage",
    "DagStorageProps",
    "DagsOptions",
    "DeployOptions",
    "EmailBackendOptions",
    "EndpointManagement",
    "Environment",
    "EnvironmentClass",
    "EnvironmentProps",
    "LogLevel",
    "LoggingConfiguration",
    "LoggingConfigurationProperty",
    "MWAAProps",
    "PrivateRoutingVpc",
    "PrivateRoutingVpcProps",
    "PublicRoutingMWAA",
    "PublicRoutingVpc",
    "PublicRoutingVpcProps",
    "SecretsBackendOptions",
    "SecurityGroup",
    "SecurityGroupProps",
    "Sizing",
    "SizingProps",
    "WebserverAccessMode",
]

publication.publish()

def _typecheckingstub__ef40a9fd92922a66e131a522a984aec05eba98c0a668dd806969973bb688f73d(
    *,
    environment: Environment,
    pool_name: builtins.str,
    pool_description: typing.Optional[builtins.str] = None,
    pool_slots: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61b1e5b1838312720b9a40d8100bdb1ea7816afa18317e3c11c6c7b57fea60d9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    environment: Environment,
    properties: typing.Mapping[builtins.str, typing.Any],
    resource_type: builtins.str,
    airflow_role: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a8f1fd388b3f30715d7f1ec120097450271a8e8e30b8f0b682d0b5169eb2bca(
    *,
    environment: Environment,
    properties: typing.Mapping[builtins.str, typing.Any],
    resource_type: builtins.str,
    airflow_role: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36432c6d2bb93b3d16e7983780304847c92cd402d8b9d4a0d6f29506aa732ff5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    create_internet_gateway: builtins.bool,
    subnet_configuration: typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]],
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    vpc_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60109e2a88eeebcaea010b7e40b7c342ff04bb32117665b005b7c01620dafa51(
    *,
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    vpc_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18fc569fcf933a2b3ce7fe86ffe34609735a142137b7878008714403e6813a46(
    *,
    name: builtins.str,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21e969a6710fc7238d65620a64ca6e99674b344908eb39331069a48b8b9f6f37(
    *,
    deploy_options: typing.Optional[typing.Union[DeployOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    local_path: typing.Optional[builtins.str] = None,
    plugins: typing.Optional[typing.Union[ConfigFile, typing.Dict[builtins.str, typing.Any]]] = None,
    requirements: typing.Optional[typing.Union[ConfigFile, typing.Dict[builtins.str, typing.Any]]] = None,
    s3_prefix: typing.Optional[builtins.str] = None,
    startup_script: typing.Optional[typing.Union[ConfigFile, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95a166027e8ebcfead2708b1c3388e60862a4fb6d86763bf56854f275bdd2390(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket_name: typing.Optional[builtins.str] = None,
    configs_options: typing.Optional[typing.Union[ConfigsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    dags_options: typing.Optional[typing.Union[DagsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    noncurrent_version_expiration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    versioned: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a4bace9647a9566f3af4198e17ef015306e92a6d5f673b579ba6fdfcb5231da(
    *,
    bucket_name: typing.Optional[builtins.str] = None,
    configs_options: typing.Optional[typing.Union[ConfigsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    dags_options: typing.Optional[typing.Union[DagsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    noncurrent_version_expiration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    versioned: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__098c6089073cc202551294a55936ecb95864b4c571722f34012f6a90ac91ac1d(
    *,
    deploy_options: typing.Optional[typing.Union[DeployOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    local_path: typing.Optional[builtins.str] = None,
    s3_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48a44035944b9df12f94158952c1f3535c44b8ea35ed316dfb479569f4286bb0(
    *,
    exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
    prune: typing.Optional[builtins.bool] = None,
    retain_on_delete: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73e90f0cf9b9873d2646653b49d16d81a04d7e328760c253beb412d5e74258d3(
    *,
    from_email: builtins.str,
    conn_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebc587b767dfc724460675574ff2adf5d781edef0bcce6da7e68d76012bd53c2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    airflow_version: builtins.str,
    dag_storage: DagStorage,
    name: builtins.str,
    sizing: Sizing,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    airflow_configuration_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    endpoint_management: typing.Optional[EndpointManagement] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    logging_configuration: typing.Optional[typing.Union[LoggingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    webserver_access_mode: typing.Optional[WebserverAccessMode] = None,
    weekly_maintenance_window_start: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0979be1ca1dd29bc506f750b97db2634a5864c9d6ab41e834a41ad36343c373(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b9f30a55d827570e6513bf50541c7cfa225d4591c531a693874230f8932899e(
    key: builtins.str,
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d58cfc6f1183850b5b51999d54a17bf62c6f7b5c3c75133b721818d02e12a9b8(
    *,
    airflow_version: builtins.str,
    dag_storage: DagStorage,
    name: builtins.str,
    sizing: Sizing,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    airflow_configuration_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    endpoint_management: typing.Optional[EndpointManagement] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    logging_configuration: typing.Optional[typing.Union[LoggingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    webserver_access_mode: typing.Optional[WebserverAccessMode] = None,
    weekly_maintenance_window_start: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e2c2b7229af680332026a2523648e1c7f223df1a7e4c0c75768ae0221551c16(
    *,
    dag_processing_logs: typing.Optional[typing.Union[LoggingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    scheduler_logs: typing.Optional[typing.Union[LoggingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    task_logs: typing.Optional[typing.Union[LoggingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    webserver_logs: typing.Optional[typing.Union[LoggingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    worker_logs: typing.Optional[typing.Union[LoggingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36e478654aa87904502c267bca96d1a7c0ca8f8e5e749464cb92a7cd1fd2c4b0(
    *,
    enabled: typing.Optional[builtins.bool] = None,
    log_level: typing.Optional[LogLevel] = None,
    retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e73d818937427f32bb22179ff7d13eb6aa0201131959780924f6ec21b94dd128(
    *,
    airflow_version: builtins.str,
    environment_name: builtins.str,
    airflow_configuration_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    configs_options: typing.Optional[typing.Union[ConfigsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    dags_options: typing.Optional[typing.Union[DagsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    sizing: typing.Optional[Sizing] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c73ed3944fc6b46a3f86d85ff5f840bb8271f57e5ac4500ccb58913c1f2a4fe5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    subnet_cidr_mask: typing.Optional[jsii.Number] = None,
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    vpc_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abb7d9fedfeb8de5ea1c1fe17c4e16a596ae22d34807b9aebb1945cd6b11871e(
    *,
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    vpc_name: typing.Optional[builtins.str] = None,
    subnet_cidr_mask: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5715af45a5664383ddb469b7bffe2c8a7d75c3dfe608847aae4c9fd79f034c9e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    airflow_version: builtins.str,
    environment_name: builtins.str,
    airflow_configuration_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    configs_options: typing.Optional[typing.Union[ConfigsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    dags_options: typing.Optional[typing.Union[DagsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    sizing: typing.Optional[Sizing] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1457f60cd9471b72ac15c6a135c3d32d6e6da4212ded7d4bab5ce7dbc54f545b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    subnet_cidr_mask: typing.Optional[jsii.Number] = None,
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    vpc_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bad12722757576263840116af2af2fd609cfd2cf55cf7c60a41c0f39c43e9ca1(
    *,
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    vpc_name: typing.Optional[builtins.str] = None,
    subnet_cidr_mask: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4a26a4745b2f3c0bf73fea3716d2c2582a993bce95da0be81eb790bf091aa13(
    *,
    connections_lookup_pattern: typing.Optional[builtins.str] = None,
    connections_prefix: typing.Optional[builtins.str] = None,
    variables_lookup_pattern: typing.Optional[builtins.str] = None,
    variables_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0c0edc0cc9086762fba282b3b093245709fb50595ba3be1a94386b8ffc61a0b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    disable_inline_rules: typing.Optional[builtins.bool] = None,
    security_group_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cc85564bef1cef94bed0ad8e10d0c4a5b9d253034b927359a0c50ae7fbafa03(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    disable_inline_rules: typing.Optional[builtins.bool] = None,
    security_group_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__379e3b2e8fe393bf82766c342457e207198846f531bd3cef817a10a9a171a08d(
    *,
    environment_class: EnvironmentClass,
    max_webservers: jsii.Number,
    max_workers: jsii.Number,
    min_webservers: jsii.Number,
    min_workers: jsii.Number,
    schedulers: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a87ff3b6f71f463c250df83cf9fd051ffc2d598fc9199d37ac367d525c389523(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    environment: Environment,
    pool_name: builtins.str,
    pool_description: typing.Optional[builtins.str] = None,
    pool_slots: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37b318e855026c52b2d51a58b8910511f891b4cb049f49619d4309af57a3e4f4(
    *,
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    vpc_name: typing.Optional[builtins.str] = None,
    create_internet_gateway: builtins.bool,
    subnet_configuration: typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass
