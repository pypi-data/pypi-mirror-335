r'''
# `cloudflare_zero_trust_gateway_logging`

Refer to the Terraform Registry for docs: [`cloudflare_zero_trust_gateway_logging`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging).
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

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class ZeroTrustGatewayLogging(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayLogging.ZeroTrustGatewayLogging",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging cloudflare_zero_trust_gateway_logging}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        redact_pii: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        settings_by_rule_type: typing.Optional[typing.Union["ZeroTrustGatewayLoggingSettingsByRuleType", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging cloudflare_zero_trust_gateway_logging} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#account_id ZeroTrustGatewayLogging#account_id}.
        :param redact_pii: Redact personally identifiable information from activity logging (PII fields are: source IP, user email, user ID, device ID, URL, referrer, user agent). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#redact_pii ZeroTrustGatewayLogging#redact_pii}
        :param settings_by_rule_type: Logging settings by rule type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#settings_by_rule_type ZeroTrustGatewayLogging#settings_by_rule_type}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4111a3ab13040823e45e546da4720cc6b056a52a0bf91aef196bd219e468e033)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ZeroTrustGatewayLoggingConfig(
            account_id=account_id,
            redact_pii=redact_pii,
            settings_by_rule_type=settings_by_rule_type,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a ZeroTrustGatewayLogging resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZeroTrustGatewayLogging to import.
        :param import_from_id: The id of the existing ZeroTrustGatewayLogging that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZeroTrustGatewayLogging to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd237025efe6be5c50c9b054761ed743c14ef3a344d2215505dfce23adf98cf9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putSettingsByRuleType")
    def put_settings_by_rule_type(
        self,
        *,
        dns: typing.Optional[builtins.str] = None,
        http: typing.Optional[builtins.str] = None,
        l4: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dns: Logging settings for DNS firewall. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#dns ZeroTrustGatewayLogging#dns}
        :param http: Logging settings for HTTP/HTTPS firewall. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#http ZeroTrustGatewayLogging#http}
        :param l4: Logging settings for Network firewall. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#l4 ZeroTrustGatewayLogging#l4}
        '''
        value = ZeroTrustGatewayLoggingSettingsByRuleType(dns=dns, http=http, l4=l4)

        return typing.cast(None, jsii.invoke(self, "putSettingsByRuleType", [value]))

    @jsii.member(jsii_name="resetRedactPii")
    def reset_redact_pii(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedactPii", []))

    @jsii.member(jsii_name="resetSettingsByRuleType")
    def reset_settings_by_rule_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSettingsByRuleType", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="settingsByRuleType")
    def settings_by_rule_type(
        self,
    ) -> "ZeroTrustGatewayLoggingSettingsByRuleTypeOutputReference":
        return typing.cast("ZeroTrustGatewayLoggingSettingsByRuleTypeOutputReference", jsii.get(self, "settingsByRuleType"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="redactPiiInput")
    def redact_pii_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "redactPiiInput"))

    @builtins.property
    @jsii.member(jsii_name="settingsByRuleTypeInput")
    def settings_by_rule_type_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayLoggingSettingsByRuleType"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayLoggingSettingsByRuleType"]], jsii.get(self, "settingsByRuleTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09feb5945f58cb14f6a70f2c074851d7014e0795bd12fb849bd6eca391b37c30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="redactPii")
    def redact_pii(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "redactPii"))

    @redact_pii.setter
    def redact_pii(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79e0eb2ab7ae61015667c238aa15605b1262a46bdf698e287bb7a70c3c137175)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redactPii", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayLogging.ZeroTrustGatewayLoggingConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "account_id": "accountId",
        "redact_pii": "redactPii",
        "settings_by_rule_type": "settingsByRuleType",
    },
)
class ZeroTrustGatewayLoggingConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        account_id: builtins.str,
        redact_pii: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        settings_by_rule_type: typing.Optional[typing.Union["ZeroTrustGatewayLoggingSettingsByRuleType", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#account_id ZeroTrustGatewayLogging#account_id}.
        :param redact_pii: Redact personally identifiable information from activity logging (PII fields are: source IP, user email, user ID, device ID, URL, referrer, user agent). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#redact_pii ZeroTrustGatewayLogging#redact_pii}
        :param settings_by_rule_type: Logging settings by rule type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#settings_by_rule_type ZeroTrustGatewayLogging#settings_by_rule_type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(settings_by_rule_type, dict):
            settings_by_rule_type = ZeroTrustGatewayLoggingSettingsByRuleType(**settings_by_rule_type)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ccbbc9aba220d1ffd5e65dfaa648190636c1747952f21c4c95d3032765c47e2)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument redact_pii", value=redact_pii, expected_type=type_hints["redact_pii"])
            check_type(argname="argument settings_by_rule_type", value=settings_by_rule_type, expected_type=type_hints["settings_by_rule_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if redact_pii is not None:
            self._values["redact_pii"] = redact_pii
        if settings_by_rule_type is not None:
            self._values["settings_by_rule_type"] = settings_by_rule_type

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def account_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#account_id ZeroTrustGatewayLogging#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def redact_pii(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Redact personally identifiable information from activity logging (PII fields are: source IP, user email, user ID, device ID, URL, referrer, user agent).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#redact_pii ZeroTrustGatewayLogging#redact_pii}
        '''
        result = self._values.get("redact_pii")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def settings_by_rule_type(
        self,
    ) -> typing.Optional["ZeroTrustGatewayLoggingSettingsByRuleType"]:
        '''Logging settings by rule type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#settings_by_rule_type ZeroTrustGatewayLogging#settings_by_rule_type}
        '''
        result = self._values.get("settings_by_rule_type")
        return typing.cast(typing.Optional["ZeroTrustGatewayLoggingSettingsByRuleType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayLoggingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayLogging.ZeroTrustGatewayLoggingSettingsByRuleType",
    jsii_struct_bases=[],
    name_mapping={"dns": "dns", "http": "http", "l4": "l4"},
)
class ZeroTrustGatewayLoggingSettingsByRuleType:
    def __init__(
        self,
        *,
        dns: typing.Optional[builtins.str] = None,
        http: typing.Optional[builtins.str] = None,
        l4: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dns: Logging settings for DNS firewall. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#dns ZeroTrustGatewayLogging#dns}
        :param http: Logging settings for HTTP/HTTPS firewall. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#http ZeroTrustGatewayLogging#http}
        :param l4: Logging settings for Network firewall. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#l4 ZeroTrustGatewayLogging#l4}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c6fade482da14d066030b1ef2dfca11c3537479d7029a168aca36df0590c97f)
            check_type(argname="argument dns", value=dns, expected_type=type_hints["dns"])
            check_type(argname="argument http", value=http, expected_type=type_hints["http"])
            check_type(argname="argument l4", value=l4, expected_type=type_hints["l4"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dns is not None:
            self._values["dns"] = dns
        if http is not None:
            self._values["http"] = http
        if l4 is not None:
            self._values["l4"] = l4

    @builtins.property
    def dns(self) -> typing.Optional[builtins.str]:
        '''Logging settings for DNS firewall.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#dns ZeroTrustGatewayLogging#dns}
        '''
        result = self._values.get("dns")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http(self) -> typing.Optional[builtins.str]:
        '''Logging settings for HTTP/HTTPS firewall.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#http ZeroTrustGatewayLogging#http}
        '''
        result = self._values.get("http")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def l4(self) -> typing.Optional[builtins.str]:
        '''Logging settings for Network firewall.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.2.0/docs/resources/zero_trust_gateway_logging#l4 ZeroTrustGatewayLogging#l4}
        '''
        result = self._values.get("l4")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayLoggingSettingsByRuleType(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayLoggingSettingsByRuleTypeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayLogging.ZeroTrustGatewayLoggingSettingsByRuleTypeOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80e12300635f1823c9da22ecc3387623c76df9132f31953e5d2198c2faea3cf8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDns")
    def reset_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDns", []))

    @jsii.member(jsii_name="resetHttp")
    def reset_http(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttp", []))

    @jsii.member(jsii_name="resetL4")
    def reset_l4(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetL4", []))

    @builtins.property
    @jsii.member(jsii_name="dnsInput")
    def dns_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dnsInput"))

    @builtins.property
    @jsii.member(jsii_name="httpInput")
    def http_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpInput"))

    @builtins.property
    @jsii.member(jsii_name="l4Input")
    def l4_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "l4Input"))

    @builtins.property
    @jsii.member(jsii_name="dns")
    def dns(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dns"))

    @dns.setter
    def dns(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__483a5b4daaa96b3da76f7b9d6399f17c5ef1926a5b90a831aa07a0f0e667abca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="http")
    def http(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "http"))

    @http.setter
    def http(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2b79bb5b759f617bb70f68f6ceac212f777f94854918906f85408cef4840d34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "http", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="l4")
    def l4(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "l4"))

    @l4.setter
    def l4(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__712a08d16c12466fd252817a8644b617712d18a7f79bb29ddd2ba085591d521a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "l4", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayLoggingSettingsByRuleType]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayLoggingSettingsByRuleType]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayLoggingSettingsByRuleType]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61147ca1a08200527143d06674a0d145d15bdd01b71c297bc32d366e3d889e55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZeroTrustGatewayLogging",
    "ZeroTrustGatewayLoggingConfig",
    "ZeroTrustGatewayLoggingSettingsByRuleType",
    "ZeroTrustGatewayLoggingSettingsByRuleTypeOutputReference",
]

publication.publish()

def _typecheckingstub__4111a3ab13040823e45e546da4720cc6b056a52a0bf91aef196bd219e468e033(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    redact_pii: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    settings_by_rule_type: typing.Optional[typing.Union[ZeroTrustGatewayLoggingSettingsByRuleType, typing.Dict[builtins.str, typing.Any]]] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd237025efe6be5c50c9b054761ed743c14ef3a344d2215505dfce23adf98cf9(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09feb5945f58cb14f6a70f2c074851d7014e0795bd12fb849bd6eca391b37c30(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79e0eb2ab7ae61015667c238aa15605b1262a46bdf698e287bb7a70c3c137175(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ccbbc9aba220d1ffd5e65dfaa648190636c1747952f21c4c95d3032765c47e2(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    redact_pii: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    settings_by_rule_type: typing.Optional[typing.Union[ZeroTrustGatewayLoggingSettingsByRuleType, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c6fade482da14d066030b1ef2dfca11c3537479d7029a168aca36df0590c97f(
    *,
    dns: typing.Optional[builtins.str] = None,
    http: typing.Optional[builtins.str] = None,
    l4: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80e12300635f1823c9da22ecc3387623c76df9132f31953e5d2198c2faea3cf8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__483a5b4daaa96b3da76f7b9d6399f17c5ef1926a5b90a831aa07a0f0e667abca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2b79bb5b759f617bb70f68f6ceac212f777f94854918906f85408cef4840d34(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__712a08d16c12466fd252817a8644b617712d18a7f79bb29ddd2ba085591d521a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61147ca1a08200527143d06674a0d145d15bdd01b71c297bc32d366e3d889e55(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayLoggingSettingsByRuleType]],
) -> None:
    """Type checking stubs"""
    pass
