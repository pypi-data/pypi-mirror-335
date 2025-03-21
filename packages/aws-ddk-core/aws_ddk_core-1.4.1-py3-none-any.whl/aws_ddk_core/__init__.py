r'''
# AWS DataOps Development Kit (DDK)

![Actions Status](https://github.com/awslabs/aws-ddk/actions/workflows/build.yml/badge.svg)
[![npm version](https://badge.fury.io/js/aws-ddk-core.svg)](https://badge.fury.io/js/aws-ddk-core)
[![PyPi version](https://badge.fury.io/py/aws-ddk-core.svg)](https://badge.fury.io/py/aws-ddk-core)
![NPM Downloads](https://img.shields.io/npm/dt/aws-ddk-core?label=npm%20downloads&color=blue)
[![PyPi Downloads](https://static.pepy.tech/personalized-badge/aws-ddk-core?period=total&units=international_system&left_text=pypi%20downloads&left_color=gray&right_color=blue)](https://pepy.tech/project/aws-ddk-core)

##### Packages 🗳️

* [NPM](https://www.npmjs.com/package/aws-ddk-core/)
* [Pypi](https://pypi.org/project/aws-ddk-core/)

---


The AWS DataOps Development Kit is an open source development framework for customers that build data workflows and modern data architecture on AWS.

Based on the [AWS CDK](https://github.com/aws/aws-cdk), it offers high-level abstractions allowing you to build pipelines that manage data flows on AWS, driven by DevOps best practices.  The framework is extensible, you can add abstractions for your own data processing infrastructure or replace our best practices with your own standards. It's easy to share templates, so everyone in your organisation can concentrate on the business logic of dealing with their data, rather than boilerplate logic.

---


The **DDK Core** is a library of CDK constructs that you can use to build data workflows and modern data architecture on AWS, following our best practice. The DDK Core is modular and extensible, if our best practice doesn't work for you, then you can update and share your own version with the rest of your organisation by leveraging a private **AWS Code Artifact** repository.

You can compose constructs from the DDK Core into a **DDK App**.  Your DDK App can also add contain constructs from the CDK Framework or the [AWS Construct Library](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-construct-library.html).

## Overview

For a detailed walk-through, check out our [Workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/3644b48b-1d7c-43ef-a353-6edcd96385af/en-US) or
take a look at [examples](https://github.com/aws-samples/aws-ddk-examples).

### Build Data Pipelines

One of the core features of DDK is ability to create Data Pipelines. A DDK [DataPipeline](https://awslabs.github.io/aws-ddk/release/stable/api/core/stubs/aws_ddk_core.pipelines.DataPipeline.html)
is a chained series of stages. It automatically “wires” the stages together using
[AWS EventBridge Rules](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rules.html) .

DDK comes with a library of stages, however users can also create their own based on their use cases,
and are encouraged to share them with the community.

Let's take a look at an example below:

```python
...

firehose_s3_stage = FirehoseToS3Stage(
    self,
    "ddk-firehose-s3",
    bucket=ddk_bucket,
    data_output_prefix="raw/",
)
sqs_lambda_stage = SqsToLambdaStage(
    scope=self,
    id="ddk-sqs-lambda",
    code=Code.from_asset("./lambda"),
    handler="index.lambda_handler",
    layers=[
        LayerVersion.from_layer_version_arn(
            self,
            "ddk-lambda-layer-wrangler",
            f"arn:aws:lambda:{self.region}:336392948345:layer:AWSSDKPandas-Python39:1",
        )
    ]
)

(
    DataPipeline(scope=self, id="ddk-pipeline")
    .add_stage(firehose_s3_stage)
    .add_stage(sqs_lambda_stage)
)
...
```

First, we import the required resources from the aws_ddk_core library, including the two stage constructs:
[FirehoseToS3Stage()](https://constructs.dev/packages/aws-ddk-core/v/1.0.1/api/FirehoseToS3Stage) and
[SqsToLambdaStage()](https://constructs.dev/packages/aws-ddk-core/v/1.0.1/api/SqsToLambdaStage).
These two classes are then instantiated and the delivery stream is configured with the S3 prefix (raw/).
Finally, the DDK DataPipeline construct is used to chain these two stages together into a data pipeline.

Complete source code of the data pipeline above can be found in
[AWS DDK Examples - Basic Data Pipeline](https://github.com/aws-samples/aws-ddk-examples/tree/main/basic-data-pipeline)

### Official Resources

* [Workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/3644b48b-1d7c-43ef-a353-6edcd96385af/en-US)
* [Documentation](https://awslabs.github.io/aws-ddk/)
* [API Reference](https://awslabs.github.io/aws-ddk/release/stable/api/index)
* [Examples](https://github.com/aws-samples/aws-ddk-examples/)

## Getting Help

The best way to interact with our team is through GitHub.  You can open an issue and choose from one of our templates for bug reports, feature requests, or documentation issues.  If you have a feature request, don't forget you can search existing issues and upvote or comment on existing issues before creating a new one.

## Contributing

We welcome community contributions and pull requests.  Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details on how to set up a development
environment and submit code.

## Other Ways to Support

One way you can support our project is by letting others know that your organisation uses the DDK.  If you would like us to include your company's name and/or logo in this README file, please raise a 'Support the DDK' issue.  Note that by raising a this issue (and related pull request), you are granting AWS permission to use your company’s name (and logo) for the limited purpose described here and you are confirming that you have authority to grant such permission.

## License

This project is licensed under the Apache-2.0 License.
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
import aws_cdk.aws_appflow as _aws_cdk_aws_appflow_ceddda9d
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_codeguruprofiler as _aws_cdk_aws_codeguruprofiler_ceddda9d
import aws_cdk.aws_codepipeline as _aws_cdk_aws_codepipeline_ceddda9d
import aws_cdk.aws_codestarnotifications as _aws_cdk_aws_codestarnotifications_ceddda9d
import aws_cdk.aws_databrew as _aws_cdk_aws_databrew_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_emrserverless as _aws_cdk_aws_emrserverless_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_glue as _aws_cdk_aws_glue_ceddda9d
import aws_cdk.aws_glue_alpha as _aws_cdk_aws_glue_alpha_ce674d29
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kinesis as _aws_cdk_aws_kinesis_ceddda9d
import aws_cdk.aws_kinesisfirehose_alpha as _aws_cdk_aws_kinesisfirehose_alpha_30daaf29
import aws_cdk.aws_kinesisfirehose_destinations_alpha as _aws_cdk_aws_kinesisfirehose_destinations_alpha_8ee8dbdc
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_mwaa as _aws_cdk_aws_mwaa_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_s3_deployment as _aws_cdk_aws_s3_deployment_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d
import aws_cdk.aws_stepfunctions as _aws_cdk_aws_stepfunctions_ceddda9d
import aws_cdk.aws_stepfunctions_tasks as _aws_cdk_aws_stepfunctions_tasks_ceddda9d
import aws_cdk.pipelines as _aws_cdk_pipelines_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="aws-ddk-core.AddApplicationStageProps",
    jsii_struct_bases=[],
    name_mapping={
        "stage": "stage",
        "stage_id": "stageId",
        "manual_approvals": "manualApprovals",
    },
)
class AddApplicationStageProps:
    def __init__(
        self,
        *,
        stage: _aws_cdk_ceddda9d.Stage,
        stage_id: builtins.str,
        manual_approvals: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties for adding an application stage.

        :param stage: Application stage instance.
        :param stage_id: Identifier of the stage.
        :param manual_approvals: Configure manual approvals. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b76c36dbcfdd4e997564efc9be54eb407b35cd3e027b00901b31d379e392170e)
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
            check_type(argname="argument stage_id", value=stage_id, expected_type=type_hints["stage_id"])
            check_type(argname="argument manual_approvals", value=manual_approvals, expected_type=type_hints["manual_approvals"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stage": stage,
            "stage_id": stage_id,
        }
        if manual_approvals is not None:
            self._values["manual_approvals"] = manual_approvals

    @builtins.property
    def stage(self) -> _aws_cdk_ceddda9d.Stage:
        '''Application stage instance.'''
        result = self._values.get("stage")
        assert result is not None, "Required property 'stage' is missing"
        return typing.cast(_aws_cdk_ceddda9d.Stage, result)

    @builtins.property
    def stage_id(self) -> builtins.str:
        '''Identifier of the stage.'''
        result = self._values.get("stage_id")
        assert result is not None, "Required property 'stage_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def manual_approvals(self) -> typing.Optional[builtins.bool]:
        '''Configure manual approvals.

        :default: false
        '''
        result = self._values.get("manual_approvals")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddApplicationStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.AddApplicationWaveProps",
    jsii_struct_bases=[],
    name_mapping={
        "stage_id": "stageId",
        "stages": "stages",
        "manual_approvals": "manualApprovals",
    },
)
class AddApplicationWaveProps:
    def __init__(
        self,
        *,
        stage_id: builtins.str,
        stages: typing.Sequence[_aws_cdk_ceddda9d.Stage],
        manual_approvals: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties for adding an application wave.

        :param stage_id: Identifier of the wave.
        :param stages: Application stage instance.
        :param manual_approvals: Configure manual approvals. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c5ca54834b066a96cdaae8f32086d4638af32527e6bdd7356e96d6b16db8c0d)
            check_type(argname="argument stage_id", value=stage_id, expected_type=type_hints["stage_id"])
            check_type(argname="argument stages", value=stages, expected_type=type_hints["stages"])
            check_type(argname="argument manual_approvals", value=manual_approvals, expected_type=type_hints["manual_approvals"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stage_id": stage_id,
            "stages": stages,
        }
        if manual_approvals is not None:
            self._values["manual_approvals"] = manual_approvals

    @builtins.property
    def stage_id(self) -> builtins.str:
        '''Identifier of the wave.'''
        result = self._values.get("stage_id")
        assert result is not None, "Required property 'stage_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stages(self) -> typing.List[_aws_cdk_ceddda9d.Stage]:
        '''Application stage instance.'''
        result = self._values.get("stages")
        assert result is not None, "Required property 'stages' is missing"
        return typing.cast(typing.List[_aws_cdk_ceddda9d.Stage], result)

    @builtins.property
    def manual_approvals(self) -> typing.Optional[builtins.bool]:
        '''Configure manual approvals.

        :default: false
        '''
        result = self._values.get("manual_approvals")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddApplicationWaveProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.AddCustomStageProps",
    jsii_struct_bases=[],
    name_mapping={"stage_name": "stageName", "steps": "steps"},
)
class AddCustomStageProps:
    def __init__(
        self,
        *,
        stage_name: builtins.str,
        steps: typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step],
    ) -> None:
        '''Properties for adding a custom stage.

        :param stage_name: Name of the stage.
        :param steps: Steps to add to this stage. List of Step objects. See `Documentation on aws_cdk.pipelines.Step <https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines/Step.html>`_ for more detail.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8660c7ffe37e5e521438a6f05e109d7d73960491ec724c71005fa435cb1ba0cb)
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument steps", value=steps, expected_type=type_hints["steps"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stage_name": stage_name,
            "steps": steps,
        }

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''Name of the stage.'''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def steps(self) -> typing.List[_aws_cdk_pipelines_ceddda9d.Step]:
        '''Steps to add to this stage. List of Step objects.

        See `Documentation on aws_cdk.pipelines.Step <https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines/Step.html>`_
        for more detail.
        '''
        result = self._values.get("steps")
        assert result is not None, "Required property 'steps' is missing"
        return typing.cast(typing.List[_aws_cdk_pipelines_ceddda9d.Step], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddCustomStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.AddNotificationsProps",
    jsii_struct_bases=[],
    name_mapping={"notification_rule": "notificationRule"},
)
class AddNotificationsProps:
    def __init__(
        self,
        *,
        notification_rule: typing.Optional[_aws_cdk_aws_codestarnotifications_ceddda9d.NotificationRule] = None,
    ) -> None:
        '''Properties for adding notifications.

        :param notification_rule: Override notification rule.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6b36a0552668c2be6f5870fa1fc235676fcd1d8e1633ffdcd8fe2ab50a5eb9c)
            check_type(argname="argument notification_rule", value=notification_rule, expected_type=type_hints["notification_rule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if notification_rule is not None:
            self._values["notification_rule"] = notification_rule

    @builtins.property
    def notification_rule(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codestarnotifications_ceddda9d.NotificationRule]:
        '''Override notification rule.'''
        result = self._values.get("notification_rule")
        return typing.cast(typing.Optional[_aws_cdk_aws_codestarnotifications_ceddda9d.NotificationRule], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddNotificationsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.AddRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "event_pattern": "eventPattern",
        "event_targets": "eventTargets",
        "id": "id",
        "override_rule": "overrideRule",
        "rule_name": "ruleName",
        "schedule": "schedule",
    },
)
class AddRuleProps:
    def __init__(
        self,
        *,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        event_targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
        id: typing.Optional[builtins.str] = None,
        override_rule: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ) -> None:
        '''
        :param event_pattern: 
        :param event_targets: 
        :param id: 
        :param override_rule: 
        :param rule_name: 
        :param schedule: 
        '''
        if isinstance(event_pattern, dict):
            event_pattern = _aws_cdk_aws_events_ceddda9d.EventPattern(**event_pattern)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc4d3cd99b8129cd1e9e86879e1aa4a9e7d0340f69bb169e136c78c563e397f5)
            check_type(argname="argument event_pattern", value=event_pattern, expected_type=type_hints["event_pattern"])
            check_type(argname="argument event_targets", value=event_targets, expected_type=type_hints["event_targets"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument override_rule", value=override_rule, expected_type=type_hints["override_rule"])
            check_type(argname="argument rule_name", value=rule_name, expected_type=type_hints["rule_name"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if event_pattern is not None:
            self._values["event_pattern"] = event_pattern
        if event_targets is not None:
            self._values["event_targets"] = event_targets
        if id is not None:
            self._values["id"] = id
        if override_rule is not None:
            self._values["override_rule"] = override_rule
        if rule_name is not None:
            self._values["rule_name"] = rule_name
        if schedule is not None:
            self._values["schedule"] = schedule

    @builtins.property
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        result = self._values.get("event_pattern")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern], result)

    @builtins.property
    def event_targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        result = self._values.get("event_targets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def override_rule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule]:
        result = self._values.get("override_rule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule], result)

    @builtins.property
    def rule_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("rule_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.AddSecurityLintStageProps",
    jsii_struct_bases=[],
    name_mapping={
        "cfn_nag_fail_build": "cfnNagFailBuild",
        "cloud_assembly_file_set": "cloudAssemblyFileSet",
        "stage_name": "stageName",
    },
)
class AddSecurityLintStageProps:
    def __init__(
        self,
        *,
        cfn_nag_fail_build: typing.Optional[builtins.bool] = None,
        cloud_assembly_file_set: typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for adding a security lint stage.

        :param cfn_nag_fail_build: Fail Codepipeline Build Action on failed results from CfnNag scan.
        :param cloud_assembly_file_set: Cloud assembly file set producer.
        :param stage_name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5c6a426f2b47035ddfb61265fb0fc5f914c183c57db8be19fd6917fe3755000)
            check_type(argname="argument cfn_nag_fail_build", value=cfn_nag_fail_build, expected_type=type_hints["cfn_nag_fail_build"])
            check_type(argname="argument cloud_assembly_file_set", value=cloud_assembly_file_set, expected_type=type_hints["cloud_assembly_file_set"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cfn_nag_fail_build is not None:
            self._values["cfn_nag_fail_build"] = cfn_nag_fail_build
        if cloud_assembly_file_set is not None:
            self._values["cloud_assembly_file_set"] = cloud_assembly_file_set
        if stage_name is not None:
            self._values["stage_name"] = stage_name

    @builtins.property
    def cfn_nag_fail_build(self) -> typing.Optional[builtins.bool]:
        '''Fail Codepipeline Build Action on failed results from CfnNag scan.'''
        result = self._values.get("cfn_nag_fail_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cloud_assembly_file_set(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer]:
        '''Cloud assembly file set producer.'''
        result = self._values.get("cloud_assembly_file_set")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddSecurityLintStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.AddStageProps",
    jsii_struct_bases=[],
    name_mapping={
        "stage": "stage",
        "override_rule": "overrideRule",
        "rule_name": "ruleName",
        "schedule": "schedule",
        "skip_rule": "skipRule",
    },
)
class AddStageProps:
    def __init__(
        self,
        *,
        stage: "Stage",
        override_rule: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        skip_rule: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param stage: 
        :param override_rule: 
        :param rule_name: 
        :param schedule: 
        :param skip_rule: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c40909713474fb0ac5879649d02b6b9b99cca8e07cc03cfb0ee3a2161cabd53f)
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
            check_type(argname="argument override_rule", value=override_rule, expected_type=type_hints["override_rule"])
            check_type(argname="argument rule_name", value=rule_name, expected_type=type_hints["rule_name"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument skip_rule", value=skip_rule, expected_type=type_hints["skip_rule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stage": stage,
        }
        if override_rule is not None:
            self._values["override_rule"] = override_rule
        if rule_name is not None:
            self._values["rule_name"] = rule_name
        if schedule is not None:
            self._values["schedule"] = schedule
        if skip_rule is not None:
            self._values["skip_rule"] = skip_rule

    @builtins.property
    def stage(self) -> "Stage":
        result = self._values.get("stage")
        assert result is not None, "Required property 'stage' is missing"
        return typing.cast("Stage", result)

    @builtins.property
    def override_rule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule]:
        result = self._values.get("override_rule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule], result)

    @builtins.property
    def rule_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("rule_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    @builtins.property
    def skip_rule(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("skip_rule")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.AddTestStageProps",
    jsii_struct_bases=[],
    name_mapping={
        "cloud_assembly_file_set": "cloudAssemblyFileSet",
        "commands": "commands",
        "stage_name": "stageName",
    },
)
class AddTestStageProps:
    def __init__(
        self,
        *,
        cloud_assembly_file_set: typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer] = None,
        commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for adding a test stage.

        :param cloud_assembly_file_set: Cloud assembly file set.
        :param commands: Additional commands to run in the test. Default: "./test.sh"
        :param stage_name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0efd164879f28724d26fec5d40738d32540d827f1e7d46271d569f72a3a0a21f)
            check_type(argname="argument cloud_assembly_file_set", value=cloud_assembly_file_set, expected_type=type_hints["cloud_assembly_file_set"])
            check_type(argname="argument commands", value=commands, expected_type=type_hints["commands"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cloud_assembly_file_set is not None:
            self._values["cloud_assembly_file_set"] = cloud_assembly_file_set
        if commands is not None:
            self._values["commands"] = commands
        if stage_name is not None:
            self._values["stage_name"] = stage_name

    @builtins.property
    def cloud_assembly_file_set(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer]:
        '''Cloud assembly file set.'''
        result = self._values.get("cloud_assembly_file_set")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer], result)

    @builtins.property
    def commands(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional commands to run in the test.

        :default: "./test.sh"
        '''
        result = self._values.get("commands")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddTestStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.AdditionalPipelineProps",
    jsii_struct_bases=[],
    name_mapping={
        "asset_publishing_code_build_defaults": "assetPublishingCodeBuildDefaults",
        "cli_version": "cliVersion",
        "code_build_defaults": "codeBuildDefaults",
        "code_pipeline": "codePipeline",
        "docker_credentials": "dockerCredentials",
        "docker_enabled_for_self_mutation": "dockerEnabledForSelfMutation",
        "docker_enabled_for_synth": "dockerEnabledForSynth",
        "publish_assets_in_parallel": "publishAssetsInParallel",
        "reuse_cross_region_support_stacks": "reuseCrossRegionSupportStacks",
        "self_mutation": "selfMutation",
        "self_mutation_code_build_defaults": "selfMutationCodeBuildDefaults",
        "synth_code_build_defaults": "synthCodeBuildDefaults",
    },
)
class AdditionalPipelineProps:
    def __init__(
        self,
        *,
        asset_publishing_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cli_version: typing.Optional[builtins.str] = None,
        code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_pipeline: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Pipeline] = None,
        docker_credentials: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.DockerCredential]] = None,
        docker_enabled_for_self_mutation: typing.Optional[builtins.bool] = None,
        docker_enabled_for_synth: typing.Optional[builtins.bool] = None,
        publish_assets_in_parallel: typing.Optional[builtins.bool] = None,
        reuse_cross_region_support_stacks: typing.Optional[builtins.bool] = None,
        self_mutation: typing.Optional[builtins.bool] = None,
        self_mutation_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        synth_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Additional properties for building the CodePipeline.

        :param asset_publishing_code_build_defaults: Additional customizations to apply to the asset publishing CodeBuild projects. Default: - Only ``codeBuildDefaults`` are applied
        :param cli_version: CDK CLI version to use in self-mutation and asset publishing steps. Default: latest version
        :param code_build_defaults: Customize the CodeBuild projects created for this pipeline. Default: - All projects run non-privileged build, SMALL instance, LinuxBuildImage.STANDARD_6_0
        :param code_pipeline: An existing Pipeline to be reused and built upon. Default: - a new underlying pipeline is created.
        :param docker_credentials: A list of credentials used to authenticate to Docker registries. Specify any credentials necessary within the pipeline to build, synth, update, or publish assets. Default: []
        :param docker_enabled_for_self_mutation: Enable Docker for the self-mutate step. Default: false
        :param docker_enabled_for_synth: Enable Docker for the 'synth' step. Default: false
        :param publish_assets_in_parallel: Publish assets in multiple CodeBuild projects. Default: true
        :param reuse_cross_region_support_stacks: Reuse the same cross region support stack for all pipelines in the App. Default: - true (Use the same support stack for all pipelines in App)
        :param self_mutation: Whether the pipeline will update itself. This needs to be set to ``true`` to allow the pipeline to reconfigure itself when assets or stages are being added to it, and ``true`` is the recommended setting. You can temporarily set this to ``false`` while you are iterating on the pipeline itself and prefer to deploy changes using ``cdk deploy``. Default: true
        :param self_mutation_code_build_defaults: Additional customizations to apply to the self mutation CodeBuild projects. Default: - Only ``codeBuildDefaults`` are applied
        :param synth_code_build_defaults: Additional customizations to apply to the synthesize CodeBuild projects. Default: - Only ``codeBuildDefaults`` are applied
        '''
        if isinstance(asset_publishing_code_build_defaults, dict):
            asset_publishing_code_build_defaults = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**asset_publishing_code_build_defaults)
        if isinstance(code_build_defaults, dict):
            code_build_defaults = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**code_build_defaults)
        if isinstance(self_mutation_code_build_defaults, dict):
            self_mutation_code_build_defaults = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**self_mutation_code_build_defaults)
        if isinstance(synth_code_build_defaults, dict):
            synth_code_build_defaults = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**synth_code_build_defaults)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34c4dbaccc767dfa14746a2df4a90bdbf9d6318afb10cc0e8809c95f4447414b)
            check_type(argname="argument asset_publishing_code_build_defaults", value=asset_publishing_code_build_defaults, expected_type=type_hints["asset_publishing_code_build_defaults"])
            check_type(argname="argument cli_version", value=cli_version, expected_type=type_hints["cli_version"])
            check_type(argname="argument code_build_defaults", value=code_build_defaults, expected_type=type_hints["code_build_defaults"])
            check_type(argname="argument code_pipeline", value=code_pipeline, expected_type=type_hints["code_pipeline"])
            check_type(argname="argument docker_credentials", value=docker_credentials, expected_type=type_hints["docker_credentials"])
            check_type(argname="argument docker_enabled_for_self_mutation", value=docker_enabled_for_self_mutation, expected_type=type_hints["docker_enabled_for_self_mutation"])
            check_type(argname="argument docker_enabled_for_synth", value=docker_enabled_for_synth, expected_type=type_hints["docker_enabled_for_synth"])
            check_type(argname="argument publish_assets_in_parallel", value=publish_assets_in_parallel, expected_type=type_hints["publish_assets_in_parallel"])
            check_type(argname="argument reuse_cross_region_support_stacks", value=reuse_cross_region_support_stacks, expected_type=type_hints["reuse_cross_region_support_stacks"])
            check_type(argname="argument self_mutation", value=self_mutation, expected_type=type_hints["self_mutation"])
            check_type(argname="argument self_mutation_code_build_defaults", value=self_mutation_code_build_defaults, expected_type=type_hints["self_mutation_code_build_defaults"])
            check_type(argname="argument synth_code_build_defaults", value=synth_code_build_defaults, expected_type=type_hints["synth_code_build_defaults"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if asset_publishing_code_build_defaults is not None:
            self._values["asset_publishing_code_build_defaults"] = asset_publishing_code_build_defaults
        if cli_version is not None:
            self._values["cli_version"] = cli_version
        if code_build_defaults is not None:
            self._values["code_build_defaults"] = code_build_defaults
        if code_pipeline is not None:
            self._values["code_pipeline"] = code_pipeline
        if docker_credentials is not None:
            self._values["docker_credentials"] = docker_credentials
        if docker_enabled_for_self_mutation is not None:
            self._values["docker_enabled_for_self_mutation"] = docker_enabled_for_self_mutation
        if docker_enabled_for_synth is not None:
            self._values["docker_enabled_for_synth"] = docker_enabled_for_synth
        if publish_assets_in_parallel is not None:
            self._values["publish_assets_in_parallel"] = publish_assets_in_parallel
        if reuse_cross_region_support_stacks is not None:
            self._values["reuse_cross_region_support_stacks"] = reuse_cross_region_support_stacks
        if self_mutation is not None:
            self._values["self_mutation"] = self_mutation
        if self_mutation_code_build_defaults is not None:
            self._values["self_mutation_code_build_defaults"] = self_mutation_code_build_defaults
        if synth_code_build_defaults is not None:
            self._values["synth_code_build_defaults"] = synth_code_build_defaults

    @builtins.property
    def asset_publishing_code_build_defaults(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions]:
        '''Additional customizations to apply to the asset publishing CodeBuild projects.

        :default: - Only ``codeBuildDefaults`` are applied
        '''
        result = self._values.get("asset_publishing_code_build_defaults")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions], result)

    @builtins.property
    def cli_version(self) -> typing.Optional[builtins.str]:
        '''CDK CLI version to use in self-mutation and asset publishing steps.

        :default: latest version
        '''
        result = self._values.get("cli_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_build_defaults(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions]:
        '''Customize the CodeBuild projects created for this pipeline.

        :default: - All projects run non-privileged build, SMALL instance, LinuxBuildImage.STANDARD_6_0
        '''
        result = self._values.get("code_build_defaults")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions], result)

    @builtins.property
    def code_pipeline(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Pipeline]:
        '''An existing Pipeline to be reused and built upon.

        :default: - a new underlying pipeline is created.
        '''
        result = self._values.get("code_pipeline")
        return typing.cast(typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Pipeline], result)

    @builtins.property
    def docker_credentials(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.DockerCredential]]:
        '''A list of credentials used to authenticate to Docker registries.

        Specify any credentials necessary within the pipeline to build, synth, update, or publish assets.

        :default: []
        '''
        result = self._values.get("docker_credentials")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.DockerCredential]], result)

    @builtins.property
    def docker_enabled_for_self_mutation(self) -> typing.Optional[builtins.bool]:
        '''Enable Docker for the self-mutate step.

        :default: false
        '''
        result = self._values.get("docker_enabled_for_self_mutation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docker_enabled_for_synth(self) -> typing.Optional[builtins.bool]:
        '''Enable Docker for the 'synth' step.

        :default: false
        '''
        result = self._values.get("docker_enabled_for_synth")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_assets_in_parallel(self) -> typing.Optional[builtins.bool]:
        '''Publish assets in multiple CodeBuild projects.

        :default: true
        '''
        result = self._values.get("publish_assets_in_parallel")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def reuse_cross_region_support_stacks(self) -> typing.Optional[builtins.bool]:
        '''Reuse the same cross region support stack for all pipelines in the App.

        :default: - true (Use the same support stack for all pipelines in App)
        '''
        result = self._values.get("reuse_cross_region_support_stacks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def self_mutation(self) -> typing.Optional[builtins.bool]:
        '''Whether the pipeline will update itself.

        This needs to be set to ``true`` to allow the pipeline to reconfigure
        itself when assets or stages are being added to it, and ``true`` is the
        recommended setting.

        You can temporarily set this to ``false`` while you are iterating
        on the pipeline itself and prefer to deploy changes using ``cdk deploy``.

        :default: true
        '''
        result = self._values.get("self_mutation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def self_mutation_code_build_defaults(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions]:
        '''Additional customizations to apply to the self mutation CodeBuild projects.

        :default: - Only ``codeBuildDefaults`` are applied
        '''
        result = self._values.get("self_mutation_code_build_defaults")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions], result)

    @builtins.property
    def synth_code_build_defaults(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions]:
        '''Additional customizations to apply to the synthesize CodeBuild projects.

        :default: - Only ``codeBuildDefaults`` are applied
        '''
        result = self._values.get("synth_code_build_defaults")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AdditionalPipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.AlarmProps",
    jsii_struct_bases=[],
    name_mapping={
        "metric": "metric",
        "comparison_operator": "comparisonOperator",
        "evaluation_periods": "evaluationPeriods",
        "threshold": "threshold",
    },
)
class AlarmProps:
    def __init__(
        self,
        *,
        metric: _aws_cdk_aws_cloudwatch_ceddda9d.IMetric,
        comparison_operator: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Properties for the alarm being added to the DataStage.

        :param metric: Metric to use for creating the stage's CloudWatch Alarm.
        :param comparison_operator: Comparison operator to use for alarm. Default: GREATER_THAN_THRESHOLD
        :param evaluation_periods: The value against which the specified alarm statistic is compared. Default: 5
        :param threshold: The number of periods over which data is compared to the specified threshold. Default: 1
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9739513f93590856f8f02851ab5bfe24bf3c845f3e37410565b3668ac8406da2)
            check_type(argname="argument metric", value=metric, expected_type=type_hints["metric"])
            check_type(argname="argument comparison_operator", value=comparison_operator, expected_type=type_hints["comparison_operator"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metric": metric,
        }
        if comparison_operator is not None:
            self._values["comparison_operator"] = comparison_operator
        if evaluation_periods is not None:
            self._values["evaluation_periods"] = evaluation_periods
        if threshold is not None:
            self._values["threshold"] = threshold

    @builtins.property
    def metric(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IMetric:
        '''Metric to use for creating the stage's CloudWatch Alarm.'''
        result = self._values.get("metric")
        assert result is not None, "Required property 'metric' is missing"
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IMetric, result)

    @builtins.property
    def comparison_operator(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator]:
        '''Comparison operator to use for alarm.

        :default: GREATER_THAN_THRESHOLD
        '''
        result = self._values.get("comparison_operator")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''The value against which the specified alarm statistic is compared.

        :default: 5
        '''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def threshold(self) -> typing.Optional[jsii.Number]:
        '''The number of periods over which data is compared to the specified threshold.

        :default: 1
        '''
        result = self._values.get("threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlarmProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BaseStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.BaseStack",
):
    '''Base Stack to inherit from.

    Includes configurable termination protection, synthesizer, permissions boundary and tags.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        config: typing.Optional[typing.Union[builtins.str, typing.Union["Configuration", typing.Dict[builtins.str, typing.Any]]]] = None,
        environment_id: typing.Optional[builtins.str] = None,
        permissions_boundary_arn: typing.Optional[builtins.str] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Create a stack.

        Includes termination protection settings, multi-level (application, environment,
        and stack-level) tags, and permissions boundary.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stack.
        :param config: Configuration or path to file which contains the configuration.
        :param environment_id: Identifier of the environment. Default: "dev"
        :param permissions_boundary_arn: ARN of the permissions boundary managed policy.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__403bc1fd4d529dd1acdcfdf6824076a7e78329d131f442981f447f8f5298a7cc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BaseStackProps(
            config=config,
            environment_id=environment_id,
            permissions_boundary_arn=permissions_boundary_arn,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            notification_arns=notification_arns,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createDefaultPermissionsBoundary")
    @builtins.classmethod
    def create_default_permissions_boundary(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        environment_id: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        qualifier: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.IManagedPolicy:
        '''
        :param scope: -
        :param id: -
        :param environment_id: 
        :param prefix: 
        :param qualifier: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c52c78b6e97cce4b370cb75d9552fff81495ba02218c70f1c8947488c2c0604a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PermissionsBoundaryProps(
            environment_id=environment_id, prefix=prefix, qualifier=qualifier
        )

        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IManagedPolicy, jsii.sinvoke(cls, "createDefaultPermissionsBoundary", [scope, id, props]))

    @jsii.member(jsii_name="exportValue")
    def export_value(
        self,
        exported_value: typing.Any,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''Create a CloudFormation Export for a string value.

        Returns a string representing the corresponding ``Fn.importValue()``
        expression for this Export. You can control the name for the export by
        passing the ``name`` option.

        If you don't supply a value for ``name``, the value you're exporting must be
        a Resource attribute (for example: ``bucket.bucketName``) and it will be
        given the same name as the automatic cross-stack reference that would be created
        if you used the attribute in another Stack.

        One of the uses for this method is to *remove* the relationship between
        two Stacks established by automatic cross-stack references. It will
        temporarily ensure that the CloudFormation Export still exists while you
        remove the reference from the consuming stack. After that, you can remove
        the resource and the manual export.

        :param exported_value: -
        :param description: The description of the outputs. Default: - No description
        :param name: The name of the export to create. Default: - A name is automatically chosen
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2efe5dde2538acae1f48243a64a4ddfc2bc79e8400b2883ddf4986fbd5984c8)
            check_type(argname="argument exported_value", value=exported_value, expected_type=type_hints["exported_value"])
        options = _aws_cdk_ceddda9d.ExportValueOptions(
            description=description, name=name
        )

        return typing.cast(builtins.str, jsii.invoke(self, "exportValue", [exported_value, options]))


@jsii.data_type(
    jsii_type="aws-ddk-core.BaseStackProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "notification_arns": "notificationArns",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "config": "config",
        "environment_id": "environmentId",
        "permissions_boundary_arn": "permissionsBoundaryArn",
    },
)
class BaseStackProps(_aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        config: typing.Optional[typing.Union[builtins.str, typing.Union["Configuration", typing.Dict[builtins.str, typing.Any]]]] = None,
        environment_id: typing.Optional[builtins.str] = None,
        permissions_boundary_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties of ``BaseStack``.

        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param config: Configuration or path to file which contains the configuration.
        :param environment_id: Identifier of the environment. Default: "dev"
        :param permissions_boundary_arn: ARN of the permissions boundary managed policy.
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a429ca722d1fec889b8120d065d6c339e922faac9a9e70454e565500ff82514c)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument notification_arns", value=notification_arns, expected_type=type_hints["notification_arns"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument environment_id", value=environment_id, expected_type=type_hints["environment_id"])
            check_type(argname="argument permissions_boundary_arn", value=permissions_boundary_arn, expected_type=type_hints["permissions_boundary_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if notification_arns is not None:
            self._values["notification_arns"] = notification_arns
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if config is not None:
            self._values["config"] = config
        if environment_id is not None:
            self._values["environment_id"] = environment_id
        if permissions_boundary_arn is not None:
            self._values["permissions_boundary_arn"] = permissions_boundary_arn

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def notification_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''SNS Topic ARNs that will receive stack events.

        :default: - no notfication arns.
        '''
        result = self._values.get("notification_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def config(self) -> typing.Optional[typing.Union[builtins.str, "Configuration"]]:
        '''Configuration or path to file which contains the configuration.'''
        result = self._values.get("config")
        return typing.cast(typing.Optional[typing.Union[builtins.str, "Configuration"]], result)

    @builtins.property
    def environment_id(self) -> typing.Optional[builtins.str]:
        '''Identifier of the environment.

        :default: "dev"
        '''
        result = self._values.get("environment_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions_boundary_arn(self) -> typing.Optional[builtins.str]:
        '''ARN of the permissions boundary managed policy.'''
        result = self._values.get("permissions_boundary_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CICDActions(metaclass=jsii.JSIIMeta, jsii_type="aws-ddk-core.CICDActions"):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="getBanditAction")
    @builtins.classmethod
    def get_bandit_action(
        cls,
        code_pipeline_source: _aws_cdk_pipelines_ceddda9d.CodePipelineSource,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_pipelines_ceddda9d.ShellStep:
        '''
        :param code_pipeline_source: -
        :param stage_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fab9ea5d8746e6c137eb1d92124b75da65dab030241ebf0002427b6ad8676aa2)
            check_type(argname="argument code_pipeline_source", value=code_pipeline_source, expected_type=type_hints["code_pipeline_source"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
        return typing.cast(_aws_cdk_pipelines_ceddda9d.ShellStep, jsii.sinvoke(cls, "getBanditAction", [code_pipeline_source, stage_name]))

    @jsii.member(jsii_name="getCfnNagAction")
    @builtins.classmethod
    def get_cfn_nag_action(
        cls,
        file_set_producer: _aws_cdk_pipelines_ceddda9d.IFileSetProducer,
        stage_name: typing.Optional[builtins.str] = None,
        fail_build: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_pipelines_ceddda9d.ShellStep:
        '''
        :param file_set_producer: -
        :param stage_name: -
        :param fail_build: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebe600cfab48179494151cd33416082a904aa73df681b93f5266545008838275)
            check_type(argname="argument file_set_producer", value=file_set_producer, expected_type=type_hints["file_set_producer"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument fail_build", value=fail_build, expected_type=type_hints["fail_build"])
        return typing.cast(_aws_cdk_pipelines_ceddda9d.ShellStep, jsii.sinvoke(cls, "getCfnNagAction", [file_set_producer, stage_name, fail_build]))

    @jsii.member(jsii_name="getCodeArtifactPublishAction")
    @builtins.classmethod
    def get_code_artifact_publish_action(
        cls,
        partition: builtins.str,
        region: builtins.str,
        account: builtins.str,
        codeartifact_repository: builtins.str,
        codeartifact_domain: builtins.str,
        codeartifact_domain_owner: builtins.str,
        code_pipeline_source: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource] = None,
        role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    ) -> _aws_cdk_pipelines_ceddda9d.CodeBuildStep:
        '''
        :param partition: -
        :param region: -
        :param account: -
        :param codeartifact_repository: -
        :param codeartifact_domain: -
        :param codeartifact_domain_owner: -
        :param code_pipeline_source: -
        :param role_policy_statements: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__203dfc08c6a839aacb072ea162bb03ae398d33f465cc8723ee83f36c65bf9fc8)
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument codeartifact_repository", value=codeartifact_repository, expected_type=type_hints["codeartifact_repository"])
            check_type(argname="argument codeartifact_domain", value=codeartifact_domain, expected_type=type_hints["codeartifact_domain"])
            check_type(argname="argument codeartifact_domain_owner", value=codeartifact_domain_owner, expected_type=type_hints["codeartifact_domain_owner"])
            check_type(argname="argument code_pipeline_source", value=code_pipeline_source, expected_type=type_hints["code_pipeline_source"])
            check_type(argname="argument role_policy_statements", value=role_policy_statements, expected_type=type_hints["role_policy_statements"])
        return typing.cast(_aws_cdk_pipelines_ceddda9d.CodeBuildStep, jsii.sinvoke(cls, "getCodeArtifactPublishAction", [partition, region, account, codeartifact_repository, codeartifact_domain, codeartifact_domain_owner, code_pipeline_source, role_policy_statements]))

    @jsii.member(jsii_name="getCodeCommitSourceAction")
    @builtins.classmethod
    def get_code_commit_source_action(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        *,
        branch: builtins.str,
        repository_name: builtins.str,
        props: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.ConnectionSourceOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> _aws_cdk_pipelines_ceddda9d.CodePipelineSource:
        '''
        :param scope: -
        :param branch: 
        :param repository_name: 
        :param props: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__299e24a53c04aec79676a22aae09e979fe6ffa8af8ec8306445500237732a145)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        props_ = CodeCommitSourceActionProps(
            branch=branch, repository_name=repository_name, props=props
        )

        return typing.cast(_aws_cdk_pipelines_ceddda9d.CodePipelineSource, jsii.sinvoke(cls, "getCodeCommitSourceAction", [scope, props_]))

    @jsii.member(jsii_name="getSynthAction")
    @builtins.classmethod
    def get_synth_action(
        cls,
        *,
        account: typing.Optional[builtins.str] = None,
        additional_install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_version: typing.Optional[builtins.str] = None,
        codeartifact_domain: typing.Optional[builtins.str] = None,
        codeartifact_domain_owner: typing.Optional[builtins.str] = None,
        codeartifact_repository: typing.Optional[builtins.str] = None,
        code_pipeline_source: typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        partition: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    ) -> _aws_cdk_pipelines_ceddda9d.CodeBuildStep:
        '''
        :param account: 
        :param additional_install_commands: 
        :param cdk_version: 
        :param codeartifact_domain: 
        :param codeartifact_domain_owner: 
        :param codeartifact_repository: 
        :param code_pipeline_source: 
        :param env: 
        :param partition: 
        :param region: 
        :param role_policy_statements: 
        '''
        props = GetSynthActionProps(
            account=account,
            additional_install_commands=additional_install_commands,
            cdk_version=cdk_version,
            codeartifact_domain=codeartifact_domain,
            codeartifact_domain_owner=codeartifact_domain_owner,
            codeartifact_repository=codeartifact_repository,
            code_pipeline_source=code_pipeline_source,
            env=env,
            partition=partition,
            region=region,
            role_policy_statements=role_policy_statements,
        )

        return typing.cast(_aws_cdk_pipelines_ceddda9d.CodeBuildStep, jsii.sinvoke(cls, "getSynthAction", [props]))

    @jsii.member(jsii_name="getTestsAction")
    @builtins.classmethod
    def get_tests_action(
        cls,
        file_set_producer: _aws_cdk_pipelines_ceddda9d.IFileSetProducer,
        commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_pipelines_ceddda9d.ShellStep:
        '''
        :param file_set_producer: -
        :param commands: -
        :param install_commands: -
        :param stage_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__906b3057114921fd5b8c18404d27778ac3f64ce364e27565682c6ab1bac71b7b)
            check_type(argname="argument file_set_producer", value=file_set_producer, expected_type=type_hints["file_set_producer"])
            check_type(argname="argument commands", value=commands, expected_type=type_hints["commands"])
            check_type(argname="argument install_commands", value=install_commands, expected_type=type_hints["install_commands"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
        return typing.cast(_aws_cdk_pipelines_ceddda9d.ShellStep, jsii.sinvoke(cls, "getTestsAction", [file_set_producer, commands, install_commands, stage_name]))


class CICDPipelineStack(
    BaseStack,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.CICDPipelineStack",
):
    '''Create a stack that contains DDK Continuous Integration and Delivery (CI/CD) pipeline.

    The pipeline is based on
    `CDK self-mutating pipeline <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.pipelines-readme.html>`_
    but includes several DDK-specific features, including:

    - Ability to configure some properties via JSON config e.g. manual approvals for application stages
    - Defaults for source/synth - CodeCommit & cdk synth, with ability to override them
    - Ability to connect to private artifactory to pull artifacts from at synth
    - Security best practices - ensures pipeline buckets block non-SSL, and are KMS-encrypted with rotated keys
    - Builder interface to avoid chunky constructor methods

    The user should be able to reuse the pipeline in multiple DDK applications hoping to save LOC.

    Example::

        const stack = new CICDPipelineStack(app, "dummy-pipeline", { environmentId: "dev", pipelineName: "dummy-pipeline" })
          .addSourceAction({ repositoryName: "dummy-repository" })
          .addSynthAction()
          .buildPipeline()
          .add_checks()
          .addStage({ stageId: "dev", stage: devStage, manualApprovals: true })
          .synth()
          .add_notifications();
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cdk_language: typing.Optional[builtins.str] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
        config: typing.Optional[typing.Union[builtins.str, typing.Union["Configuration", typing.Dict[builtins.str, typing.Any]]]] = None,
        environment_id: typing.Optional[builtins.str] = None,
        permissions_boundary_arn: typing.Optional[builtins.str] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Creates a new CICD Pipeline stack.

        :param scope: Parent of this stack, usually an ``App`` or a ``Stage``, but could be any construct.
        :param id: The construct ID of this stack. If ``stackName`` is not explicitly defined, this id (and any parent IDs) will be used to determine the physical ID of the stack.
        :param cdk_language: Language of the CDK construct definitions. Default: "typescript"
        :param pipeline_name: Name of the pipeline.
        :param config: Configuration or path to file which contains the configuration.
        :param environment_id: Identifier of the environment. Default: "dev"
        :param permissions_boundary_arn: ARN of the permissions boundary managed policy.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a4f7374970c6409060af558e7802348870a4c4a3b9f9232e789f1488d18fb90)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CICDPipelineStackProps(
            cdk_language=cdk_language,
            pipeline_name=pipeline_name,
            config=config,
            environment_id=environment_id,
            permissions_boundary_arn=permissions_boundary_arn,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            notification_arns=notification_arns,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addChecks")
    def add_checks(self) -> "CICDPipelineStack":
        '''Add checks to the pipeline (e.g. linting, security, tests...).

        :return: reference to this pipeline.
        '''
        return typing.cast("CICDPipelineStack", jsii.invoke(self, "addChecks", []))

    @jsii.member(jsii_name="addCustomStage")
    def add_custom_stage(
        self,
        *,
        stage_name: builtins.str,
        steps: typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step],
    ) -> "CICDPipelineStack":
        '''Add custom stage to the pipeline.

        :param stage_name: Name of the stage.
        :param steps: Steps to add to this stage. List of Step objects. See `Documentation on aws_cdk.pipelines.Step <https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines/Step.html>`_ for more detail.

        :return: reference to this pipeline.
        '''
        props = AddCustomStageProps(stage_name=stage_name, steps=steps)

        return typing.cast("CICDPipelineStack", jsii.invoke(self, "addCustomStage", [props]))

    @jsii.member(jsii_name="addNotifications")
    def add_notifications(
        self,
        *,
        notification_rule: typing.Optional[_aws_cdk_aws_codestarnotifications_ceddda9d.NotificationRule] = None,
    ) -> "CICDPipelineStack":
        '''Add pipeline notifications.

        Create notification rule that sends events to the specified SNS topic.

        :param notification_rule: Override notification rule.

        :return: reference to this pipeline.
        '''
        props = AddNotificationsProps(notification_rule=notification_rule)

        return typing.cast("CICDPipelineStack", jsii.invoke(self, "addNotifications", [props]))

    @jsii.member(jsii_name="addSecurityLintStage")
    def add_security_lint_stage(
        self,
        *,
        cfn_nag_fail_build: typing.Optional[builtins.bool] = None,
        cloud_assembly_file_set: typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> "CICDPipelineStack":
        '''Add linting - cfn-nag, and bandit.

        :param cfn_nag_fail_build: Fail Codepipeline Build Action on failed results from CfnNag scan.
        :param cloud_assembly_file_set: Cloud assembly file set producer.
        :param stage_name: Name of the stage.

        :return: reference to this pipeline.
        '''
        props = AddSecurityLintStageProps(
            cfn_nag_fail_build=cfn_nag_fail_build,
            cloud_assembly_file_set=cloud_assembly_file_set,
            stage_name=stage_name,
        )

        return typing.cast("CICDPipelineStack", jsii.invoke(self, "addSecurityLintStage", [props]))

    @jsii.member(jsii_name="addSourceAction")
    def add_source_action(
        self,
        *,
        repository_name: builtins.str,
        branch: typing.Optional[builtins.str] = None,
        source_action: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource] = None,
    ) -> "CICDPipelineStack":
        '''Add source action.

        :param repository_name: Name of the SCM repository.
        :param branch: Branch of the SCM repository.
        :param source_action: Override source action.

        :return: reference to this pipeline.
        '''
        props = SourceActionProps(
            repository_name=repository_name, branch=branch, source_action=source_action
        )

        return typing.cast("CICDPipelineStack", jsii.invoke(self, "addSourceAction", [props]))

    @jsii.member(jsii_name="addStage")
    def add_stage(
        self,
        *,
        stage: _aws_cdk_ceddda9d.Stage,
        stage_id: builtins.str,
        manual_approvals: typing.Optional[builtins.bool] = None,
    ) -> "CICDPipelineStack":
        '''Add application stage to the CICD pipeline.

        This stage deploys your application infrastructure.

        :param stage: Application stage instance.
        :param stage_id: Identifier of the stage.
        :param manual_approvals: Configure manual approvals. Default: false

        :return: reference to this pipeline.
        '''
        props = AddApplicationStageProps(
            stage=stage, stage_id=stage_id, manual_approvals=manual_approvals
        )

        return typing.cast("CICDPipelineStack", jsii.invoke(self, "addStage", [props]))

    @jsii.member(jsii_name="addSynthAction")
    def add_synth_action(
        self,
        *,
        additional_install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_language_command_line_arguments: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        cdk_version: typing.Optional[builtins.str] = None,
        codeartifact_domain: typing.Optional[builtins.str] = None,
        codeartifact_domain_owner: typing.Optional[builtins.str] = None,
        codeartifact_repository: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        synth_action: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildStep] = None,
    ) -> "CICDPipelineStack":
        '''Add synth action.

        During synth can connect and pull artifacts from a private artifactory.

        :param additional_install_commands: Additional install commands.
        :param cdk_language_command_line_arguments: Additional command line arguements to append to the install command of the ``cdk_langauge`` that is specified. Default: - No command line arguments are appended
        :param cdk_version: CDK versio to use during the synth action. Default: "latest"
        :param codeartifact_domain: Name of the CodeArtifact domain.
        :param codeartifact_domain_owner: CodeArtifact domain owner account.
        :param codeartifact_repository: Name of the CodeArtifact repository to pull artifacts from.
        :param env: Environment variables to set.
        :param role_policy_statements: Additional policies to add to the synth action role.
        :param synth_action: Override synth action.

        :return: reference to this pipeline.
        '''
        props = SynthActionProps(
            additional_install_commands=additional_install_commands,
            cdk_language_command_line_arguments=cdk_language_command_line_arguments,
            cdk_version=cdk_version,
            codeartifact_domain=codeartifact_domain,
            codeartifact_domain_owner=codeartifact_domain_owner,
            codeartifact_repository=codeartifact_repository,
            env=env,
            role_policy_statements=role_policy_statements,
            synth_action=synth_action,
        )

        return typing.cast("CICDPipelineStack", jsii.invoke(self, "addSynthAction", [props]))

    @jsii.member(jsii_name="addTestStage")
    def add_test_stage(
        self,
        *,
        cloud_assembly_file_set: typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer] = None,
        commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> "CICDPipelineStack":
        '''Add test - e.g. pytest.

        :param cloud_assembly_file_set: Cloud assembly file set.
        :param commands: Additional commands to run in the test. Default: "./test.sh"
        :param stage_name: Name of the stage.

        :return: reference to this pipeline.
        '''
        props = AddTestStageProps(
            cloud_assembly_file_set=cloud_assembly_file_set,
            commands=commands,
            stage_name=stage_name,
        )

        return typing.cast("CICDPipelineStack", jsii.invoke(self, "addTestStage", [props]))

    @jsii.member(jsii_name="addWave")
    def add_wave(
        self,
        *,
        stage_id: builtins.str,
        stages: typing.Sequence[_aws_cdk_ceddda9d.Stage],
        manual_approvals: typing.Optional[builtins.bool] = None,
    ) -> "CICDPipelineStack":
        '''Add multiple application stages in parallel to the CICD pipeline.

        :param stage_id: Identifier of the wave.
        :param stages: Application stage instance.
        :param manual_approvals: Configure manual approvals. Default: false

        :return: reference to this pipeline.
        '''
        props = AddApplicationWaveProps(
            stage_id=stage_id, stages=stages, manual_approvals=manual_approvals
        )

        return typing.cast("CICDPipelineStack", jsii.invoke(self, "addWave", [props]))

    @jsii.member(jsii_name="buildPipeline")
    def build_pipeline(
        self,
        *,
        asset_publishing_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cli_version: typing.Optional[builtins.str] = None,
        code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_pipeline: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Pipeline] = None,
        docker_credentials: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.DockerCredential]] = None,
        docker_enabled_for_self_mutation: typing.Optional[builtins.bool] = None,
        docker_enabled_for_synth: typing.Optional[builtins.bool] = None,
        publish_assets_in_parallel: typing.Optional[builtins.bool] = None,
        reuse_cross_region_support_stacks: typing.Optional[builtins.bool] = None,
        self_mutation: typing.Optional[builtins.bool] = None,
        self_mutation_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        synth_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "CICDPipelineStack":
        '''Build the pipeline structure.

        :param asset_publishing_code_build_defaults: Additional customizations to apply to the asset publishing CodeBuild projects. Default: - Only ``codeBuildDefaults`` are applied
        :param cli_version: CDK CLI version to use in self-mutation and asset publishing steps. Default: latest version
        :param code_build_defaults: Customize the CodeBuild projects created for this pipeline. Default: - All projects run non-privileged build, SMALL instance, LinuxBuildImage.STANDARD_6_0
        :param code_pipeline: An existing Pipeline to be reused and built upon. Default: - a new underlying pipeline is created.
        :param docker_credentials: A list of credentials used to authenticate to Docker registries. Specify any credentials necessary within the pipeline to build, synth, update, or publish assets. Default: []
        :param docker_enabled_for_self_mutation: Enable Docker for the self-mutate step. Default: false
        :param docker_enabled_for_synth: Enable Docker for the 'synth' step. Default: false
        :param publish_assets_in_parallel: Publish assets in multiple CodeBuild projects. Default: true
        :param reuse_cross_region_support_stacks: Reuse the same cross region support stack for all pipelines in the App. Default: - true (Use the same support stack for all pipelines in App)
        :param self_mutation: Whether the pipeline will update itself. This needs to be set to ``true`` to allow the pipeline to reconfigure itself when assets or stages are being added to it, and ``true`` is the recommended setting. You can temporarily set this to ``false`` while you are iterating on the pipeline itself and prefer to deploy changes using ``cdk deploy``. Default: true
        :param self_mutation_code_build_defaults: Additional customizations to apply to the self mutation CodeBuild projects. Default: - Only ``codeBuildDefaults`` are applied
        :param synth_code_build_defaults: Additional customizations to apply to the synthesize CodeBuild projects. Default: - Only ``codeBuildDefaults`` are applied

        :return: reference to this pipeline.
        '''
        props = AdditionalPipelineProps(
            asset_publishing_code_build_defaults=asset_publishing_code_build_defaults,
            cli_version=cli_version,
            code_build_defaults=code_build_defaults,
            code_pipeline=code_pipeline,
            docker_credentials=docker_credentials,
            docker_enabled_for_self_mutation=docker_enabled_for_self_mutation,
            docker_enabled_for_synth=docker_enabled_for_synth,
            publish_assets_in_parallel=publish_assets_in_parallel,
            reuse_cross_region_support_stacks=reuse_cross_region_support_stacks,
            self_mutation=self_mutation,
            self_mutation_code_build_defaults=self_mutation_code_build_defaults,
            synth_code_build_defaults=synth_code_build_defaults,
        )

        return typing.cast("CICDPipelineStack", jsii.invoke(self, "buildPipeline", [props]))

    @jsii.member(jsii_name="synth")
    def synth(self) -> "CICDPipelineStack":
        '''Synthesize the pipeline.

        :return: reference to this pipeline.
        '''
        return typing.cast("CICDPipelineStack", jsii.invoke(self, "synth", []))

    @builtins.property
    @jsii.member(jsii_name="cdkLanguage")
    def cdk_language(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cdkLanguage"))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "Configurator":
        return typing.cast("Configurator", jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="environmentId")
    def environment_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "environmentId"))

    @builtins.property
    @jsii.member(jsii_name="pipelineId")
    def pipeline_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pipelineId"))

    @builtins.property
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pipelineName"))

    @builtins.property
    @jsii.member(jsii_name="notificationRule")
    def notification_rule(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codestarnotifications_ceddda9d.NotificationRule]:
        return typing.cast(typing.Optional[_aws_cdk_aws_codestarnotifications_ceddda9d.NotificationRule], jsii.get(self, "notificationRule"))

    @notification_rule.setter
    def notification_rule(
        self,
        value: typing.Optional[_aws_cdk_aws_codestarnotifications_ceddda9d.NotificationRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0068433bd751f33d982df797ea7caafaf7cffac6096fcfa31b631eb939dd331b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notificationRule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipeline]:
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipeline], jsii.get(self, "pipeline"))

    @pipeline.setter
    def pipeline(
        self,
        value: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipeline],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e242ec0edda32ab650513e5c858717f596009d201ebe6c35d192b13bb37b46e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pipeline", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pipelineKey")
    def pipeline_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.CfnKey]:
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.CfnKey], jsii.get(self, "pipelineKey"))

    @pipeline_key.setter
    def pipeline_key(
        self,
        value: typing.Optional[_aws_cdk_aws_kms_ceddda9d.CfnKey],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdd6e87a9d4eea532d3b53339bd619a881413d8b48bab8ceb6116633e65f946d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pipelineKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceAction")
    def source_action(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource]:
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource], jsii.get(self, "sourceAction"))

    @source_action.setter
    def source_action(
        self,
        value: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19397f9a8bd0b90a5f185ea4729b0b19930bbfb902f228f2537c616170569bf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceAction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="synthAction")
    def synth_action(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildStep]:
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildStep], jsii.get(self, "synthAction"))

    @synth_action.setter
    def synth_action(
        self,
        value: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildStep],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae2239ce5199560ebc5f2e8f3ab6392af34c4678da2fdeb67265c0f37277507b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "synthAction", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="aws-ddk-core.CICDPipelineStackProps",
    jsii_struct_bases=[BaseStackProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "notification_arns": "notificationArns",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "config": "config",
        "environment_id": "environmentId",
        "permissions_boundary_arn": "permissionsBoundaryArn",
        "cdk_language": "cdkLanguage",
        "pipeline_name": "pipelineName",
    },
)
class CICDPipelineStackProps(BaseStackProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        config: typing.Optional[typing.Union[builtins.str, typing.Union["Configuration", typing.Dict[builtins.str, typing.Any]]]] = None,
        environment_id: typing.Optional[builtins.str] = None,
        permissions_boundary_arn: typing.Optional[builtins.str] = None,
        cdk_language: typing.Optional[builtins.str] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''CICD Pipeline Stack properties.

        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param config: Configuration or path to file which contains the configuration.
        :param environment_id: Identifier of the environment. Default: "dev"
        :param permissions_boundary_arn: ARN of the permissions boundary managed policy.
        :param cdk_language: Language of the CDK construct definitions. Default: "typescript"
        :param pipeline_name: Name of the pipeline.
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a92abb1f3b57ec36ef721160ab799be2851ede5d3e872162fc75be713f4d3293)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument notification_arns", value=notification_arns, expected_type=type_hints["notification_arns"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument environment_id", value=environment_id, expected_type=type_hints["environment_id"])
            check_type(argname="argument permissions_boundary_arn", value=permissions_boundary_arn, expected_type=type_hints["permissions_boundary_arn"])
            check_type(argname="argument cdk_language", value=cdk_language, expected_type=type_hints["cdk_language"])
            check_type(argname="argument pipeline_name", value=pipeline_name, expected_type=type_hints["pipeline_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if notification_arns is not None:
            self._values["notification_arns"] = notification_arns
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if config is not None:
            self._values["config"] = config
        if environment_id is not None:
            self._values["environment_id"] = environment_id
        if permissions_boundary_arn is not None:
            self._values["permissions_boundary_arn"] = permissions_boundary_arn
        if cdk_language is not None:
            self._values["cdk_language"] = cdk_language
        if pipeline_name is not None:
            self._values["pipeline_name"] = pipeline_name

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def notification_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''SNS Topic ARNs that will receive stack events.

        :default: - no notfication arns.
        '''
        result = self._values.get("notification_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def config(self) -> typing.Optional[typing.Union[builtins.str, "Configuration"]]:
        '''Configuration or path to file which contains the configuration.'''
        result = self._values.get("config")
        return typing.cast(typing.Optional[typing.Union[builtins.str, "Configuration"]], result)

    @builtins.property
    def environment_id(self) -> typing.Optional[builtins.str]:
        '''Identifier of the environment.

        :default: "dev"
        '''
        result = self._values.get("environment_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions_boundary_arn(self) -> typing.Optional[builtins.str]:
        '''ARN of the permissions boundary managed policy.'''
        result = self._values.get("permissions_boundary_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cdk_language(self) -> typing.Optional[builtins.str]:
        '''Language of the CDK construct definitions.

        :default: "typescript"
        '''
        result = self._values.get("cdk_language")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pipeline_name(self) -> typing.Optional[builtins.str]:
        '''Name of the pipeline.'''
        result = self._values.get("pipeline_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CICDPipelineStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.CodeArtifactPublishActionProps",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "codeartifact_domain": "codeartifactDomain",
        "codeartifact_domain_owner": "codeartifactDomainOwner",
        "codeartifact_repository": "codeartifactRepository",
        "partition": "partition",
        "region": "region",
        "code_pipeline_source": "codePipelineSource",
        "role_policy_statements": "rolePolicyStatements",
    },
)
class CodeArtifactPublishActionProps:
    def __init__(
        self,
        *,
        account: builtins.str,
        codeartifact_domain: builtins.str,
        codeartifact_domain_owner: builtins.str,
        codeartifact_repository: builtins.str,
        partition: builtins.str,
        region: builtins.str,
        code_pipeline_source: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource] = None,
        role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    ) -> None:
        '''
        :param account: 
        :param codeartifact_domain: 
        :param codeartifact_domain_owner: 
        :param codeartifact_repository: 
        :param partition: 
        :param region: 
        :param code_pipeline_source: 
        :param role_policy_statements: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c35f21eb6e1a4595459d5a4102a340db464f6d6da23770e16d40eca5d3e00623)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument codeartifact_domain", value=codeartifact_domain, expected_type=type_hints["codeartifact_domain"])
            check_type(argname="argument codeartifact_domain_owner", value=codeartifact_domain_owner, expected_type=type_hints["codeartifact_domain_owner"])
            check_type(argname="argument codeartifact_repository", value=codeartifact_repository, expected_type=type_hints["codeartifact_repository"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument code_pipeline_source", value=code_pipeline_source, expected_type=type_hints["code_pipeline_source"])
            check_type(argname="argument role_policy_statements", value=role_policy_statements, expected_type=type_hints["role_policy_statements"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account": account,
            "codeartifact_domain": codeartifact_domain,
            "codeartifact_domain_owner": codeartifact_domain_owner,
            "codeartifact_repository": codeartifact_repository,
            "partition": partition,
            "region": region,
        }
        if code_pipeline_source is not None:
            self._values["code_pipeline_source"] = code_pipeline_source
        if role_policy_statements is not None:
            self._values["role_policy_statements"] = role_policy_statements

    @builtins.property
    def account(self) -> builtins.str:
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def codeartifact_domain(self) -> builtins.str:
        result = self._values.get("codeartifact_domain")
        assert result is not None, "Required property 'codeartifact_domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def codeartifact_domain_owner(self) -> builtins.str:
        result = self._values.get("codeartifact_domain_owner")
        assert result is not None, "Required property 'codeartifact_domain_owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def codeartifact_repository(self) -> builtins.str:
        result = self._values.get("codeartifact_repository")
        assert result is not None, "Required property 'codeartifact_repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def partition(self) -> builtins.str:
        result = self._values.get("partition")
        assert result is not None, "Required property 'partition' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code_pipeline_source(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource]:
        result = self._values.get("code_pipeline_source")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource], result)

    @builtins.property
    def role_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        result = self._values.get("role_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeArtifactPublishActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.CodeCommitSourceActionProps",
    jsii_struct_bases=[],
    name_mapping={
        "branch": "branch",
        "repository_name": "repositoryName",
        "props": "props",
    },
)
class CodeCommitSourceActionProps:
    def __init__(
        self,
        *,
        branch: builtins.str,
        repository_name: builtins.str,
        props: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.ConnectionSourceOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param branch: 
        :param repository_name: 
        :param props: 
        '''
        if isinstance(props, dict):
            props = _aws_cdk_pipelines_ceddda9d.ConnectionSourceOptions(**props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8379be0808b59cd840396438fecd2826772ffc3dbcfeaf5175ccf01b988d69b)
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "branch": branch,
            "repository_name": repository_name,
        }
        if props is not None:
            self._values["props"] = props

    @builtins.property
    def branch(self) -> builtins.str:
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_name(self) -> builtins.str:
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def props(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.ConnectionSourceOptions]:
        result = self._values.get("props")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.ConnectionSourceOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeCommitSourceActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.Configuration",
    jsii_struct_bases=[],
    name_mapping={
        "environments": "environments",
        "account": "account",
        "bootstrap": "bootstrap",
        "ddk_bootstrap_config_key": "ddkBootstrapConfigKey",
        "props": "props",
        "region": "region",
        "tags": "tags",
    },
)
class Configuration:
    def __init__(
        self,
        *,
        environments: typing.Mapping[builtins.str, typing.Union["EnvironmentConfiguration", typing.Dict[builtins.str, typing.Any]]],
        account: typing.Optional[builtins.str] = None,
        bootstrap: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        ddk_bootstrap_config_key: typing.Optional[builtins.str] = None,
        props: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        region: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param environments: 
        :param account: 
        :param bootstrap: 
        :param ddk_bootstrap_config_key: 
        :param props: 
        :param region: 
        :param tags: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__daeed9e6cb5e50c39b922933d297c173f25183423bf700dfd9f8b0fe3765c923)
            check_type(argname="argument environments", value=environments, expected_type=type_hints["environments"])
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument bootstrap", value=bootstrap, expected_type=type_hints["bootstrap"])
            check_type(argname="argument ddk_bootstrap_config_key", value=ddk_bootstrap_config_key, expected_type=type_hints["ddk_bootstrap_config_key"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "environments": environments,
        }
        if account is not None:
            self._values["account"] = account
        if bootstrap is not None:
            self._values["bootstrap"] = bootstrap
        if ddk_bootstrap_config_key is not None:
            self._values["ddk_bootstrap_config_key"] = ddk_bootstrap_config_key
        if props is not None:
            self._values["props"] = props
        if region is not None:
            self._values["region"] = region
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def environments(self) -> typing.Mapping[builtins.str, "EnvironmentConfiguration"]:
        result = self._values.get("environments")
        assert result is not None, "Required property 'environments' is missing"
        return typing.cast(typing.Mapping[builtins.str, "EnvironmentConfiguration"], result)

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bootstrap(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("bootstrap")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def ddk_bootstrap_config_key(self) -> typing.Optional[builtins.str]:
        result = self._values.get("ddk_bootstrap_config_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def props(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        result = self._values.get("props")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Configuration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Configurator(metaclass=jsii.JSIIMeta, jsii_type="aws-ddk-core.Configurator"):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        config: typing.Union[builtins.str, typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]],
        environment_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param config: -
        :param environment_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83dd06108e5a02547d07299060f92123340b3d7ec7e9e6f36a8e28ce02b22a22)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument environment_id", value=environment_id, expected_type=type_hints["environment_id"])
        jsii.create(self.__class__, self, [scope, config, environment_id])

    @jsii.member(jsii_name="getConfig")
    @builtins.classmethod
    def get_config(
        cls,
        *,
        config: typing.Optional[typing.Union[builtins.str, typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> typing.Optional[Configuration]:
        '''
        :param config: 
        '''
        props = GetConfigProps(config=config)

        return typing.cast(typing.Optional[Configuration], jsii.sinvoke(cls, "getConfig", [props]))

    @jsii.member(jsii_name="getEnvConfig")
    @builtins.classmethod
    def get_env_config(
        cls,
        *,
        environment_id: builtins.str,
        config_path: typing.Optional[builtins.str] = None,
    ) -> "EnvironmentConfiguration":
        '''
        :param environment_id: Environment identifier.
        :param config_path: Relative path to config file. Defaults to './ddk.json'
        '''
        props = GetEnvConfigProps(
            environment_id=environment_id, config_path=config_path
        )

        return typing.cast("EnvironmentConfiguration", jsii.sinvoke(cls, "getEnvConfig", [props]))

    @jsii.member(jsii_name="getEnvironment")
    @builtins.classmethod
    def get_environment(
        cls,
        *,
        config_path: typing.Optional[builtins.str] = None,
        environment_id: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_ceddda9d.Environment:
        '''
        :param config_path: Relative path to config file. Defaults to './ddk.json'
        :param environment_id: Environment identifier.
        '''
        props = GetEnvironmentProps(
            config_path=config_path, environment_id=environment_id
        )

        return typing.cast(_aws_cdk_ceddda9d.Environment, jsii.sinvoke(cls, "getEnvironment", [props]))

    @jsii.member(jsii_name="getTags")
    @builtins.classmethod
    def get_tags(
        cls,
        *,
        config_path: typing.Optional[builtins.str] = None,
        environment_id: typing.Optional[builtins.str] = None,
    ) -> typing.Mapping[builtins.str, builtins.str]:
        '''
        :param config_path: Relative path to config file. Defaults to './ddk.json'
        :param environment_id: Environment identifier.
        '''
        props = GetTagsProps(config_path=config_path, environment_id=environment_id)

        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.sinvoke(cls, "getTags", [props]))

    @jsii.member(jsii_name="getConfigAttribute")
    def get_config_attribute(self, attribute: builtins.str) -> typing.Any:
        '''
        :param attribute: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce369044fa737e8a329b15db41cbef0ecf3e52cea663d9bd55b6edfe486a7705)
            check_type(argname="argument attribute", value=attribute, expected_type=type_hints["attribute"])
        return typing.cast(typing.Any, jsii.invoke(self, "getConfigAttribute", [attribute]))

    @jsii.member(jsii_name="tagConstruct")
    def tag_construct(
        self,
        scope: _constructs_77d1e7e8.Construct,
        tags: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        '''
        :param scope: -
        :param tags: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ebebaeeabeb2e14afe10bb65476a72e653389f44163949f819c5b260fc48e7c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        return typing.cast(None, jsii.invoke(self, "tagConstruct", [scope, tags]))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> Configuration:
        return typing.cast(Configuration, jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="environmentId")
    def environment_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "environmentId"))


@jsii.data_type(
    jsii_type="aws-ddk-core.CreateStateMachineResult",
    jsii_struct_bases=[],
    name_mapping={
        "event_pattern": "eventPattern",
        "state_machine": "stateMachine",
        "targets": "targets",
    },
)
class CreateStateMachineResult:
    def __init__(
        self,
        *,
        event_pattern: typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]],
        state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
        targets: typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget],
    ) -> None:
        '''
        :param event_pattern: 
        :param state_machine: 
        :param targets: 
        '''
        if isinstance(event_pattern, dict):
            event_pattern = _aws_cdk_aws_events_ceddda9d.EventPattern(**event_pattern)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a42d01fb82a6fe17fa9b9b89a21fb52b88b8267a8d48f866ab150cb834952324)
            check_type(argname="argument event_pattern", value=event_pattern, expected_type=type_hints["event_pattern"])
            check_type(argname="argument state_machine", value=state_machine, expected_type=type_hints["state_machine"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "event_pattern": event_pattern,
            "state_machine": state_machine,
            "targets": targets,
        }

    @builtins.property
    def event_pattern(self) -> _aws_cdk_aws_events_ceddda9d.EventPattern:
        result = self._values.get("event_pattern")
        assert result is not None, "Required property 'event_pattern' is missing"
        return typing.cast(_aws_cdk_aws_events_ceddda9d.EventPattern, result)

    @builtins.property
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        result = self._values.get("state_machine")
        assert result is not None, "Required property 'state_machine' is missing"
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, result)

    @builtins.property
    def targets(self) -> typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]:
        result = self._values.get("targets")
        assert result is not None, "Required property 'targets' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CreateStateMachineResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataPipeline(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.DataPipeline",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: 
        :param name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__020d69ac62c8be050bbf68165b37eefae84c4185726ff175a8444e0c59df78df)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataPipelineProps(description=description, name=name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addNotifications")
    def add_notifications(
        self,
        notifications_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    ) -> "DataPipeline":
        '''
        :param notifications_topic: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0261b3bfb9d75b19f131b94fdac46b066b26e0543adf83caf2f9ff8436e7fc80)
            check_type(argname="argument notifications_topic", value=notifications_topic, expected_type=type_hints["notifications_topic"])
        return typing.cast("DataPipeline", jsii.invoke(self, "addNotifications", [notifications_topic]))

    @jsii.member(jsii_name="addRule")
    def add_rule(
        self,
        *,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        event_targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
        id: typing.Optional[builtins.str] = None,
        override_rule: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ) -> "DataPipeline":
        '''
        :param event_pattern: 
        :param event_targets: 
        :param id: 
        :param override_rule: 
        :param rule_name: 
        :param schedule: 
        '''
        props = AddRuleProps(
            event_pattern=event_pattern,
            event_targets=event_targets,
            id=id,
            override_rule=override_rule,
            rule_name=rule_name,
            schedule=schedule,
        )

        return typing.cast("DataPipeline", jsii.invoke(self, "addRule", [props]))

    @jsii.member(jsii_name="addStage")
    def add_stage(
        self,
        *,
        stage: "Stage",
        override_rule: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        skip_rule: typing.Optional[builtins.bool] = None,
    ) -> "DataPipeline":
        '''
        :param stage: 
        :param override_rule: 
        :param rule_name: 
        :param schedule: 
        :param skip_rule: 
        '''
        props = AddStageProps(
            stage=stage,
            override_rule=override_rule,
            rule_name=rule_name,
            schedule=schedule,
            skip_rule=skip_rule,
        )

        return typing.cast("DataPipeline", jsii.invoke(self, "addStage", [props]))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))


@jsii.data_type(
    jsii_type="aws-ddk-core.DataPipelineProps",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "name": "name"},
)
class DataPipelineProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: 
        :param name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__946287dcda6fcab40d64fc9e8f72a5917de6ace9c417f850f53a1418c864067d)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.DeliveryStreamProps",
    jsii_struct_bases=[],
    name_mapping={
        "delivery_stream_name": "deliveryStreamName",
        "destinations": "destinations",
        "encryption": "encryption",
        "encryption_key": "encryptionKey",
        "role": "role",
        "source_stream": "sourceStream",
    },
)
class DeliveryStreamProps:
    def __init__(
        self,
        *,
        delivery_stream_name: typing.Optional[builtins.str] = None,
        destinations: typing.Optional[typing.Sequence[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.IDestination]] = None,
        encryption: typing.Optional[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.StreamEncryption] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        source_stream: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.IStream] = None,
    ) -> None:
        '''Properties of the Firehose Delivery stream to be created.

        :param delivery_stream_name: A name for the delivery stream. Default: - a name is generated by CloudFormation.
        :param destinations: The destinations that this delivery stream will deliver data to. Only a singleton array is supported at this time.
        :param encryption: Indicates the type of customer master key (CMK) to use for server-side encryption, if any. Default: StreamEncryption.UNENCRYPTED - unless ``encryptionKey`` is provided, in which case this will be implicitly set to ``StreamEncryption.CUSTOMER_MANAGED``
        :param encryption_key: Customer managed key to server-side encrypt data in the stream. Default: - no KMS key will be used; if ``encryption`` is set to ``CUSTOMER_MANAGED``, a KMS key will be created for you
        :param role: The IAM role associated with this delivery stream. Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side. Default: - a role will be created with default permissions.
        :param source_stream: The Kinesis data stream to use as a source for this delivery stream. Default: - data must be written to the delivery stream via a direct put.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef7997fe1d9215e0814459fdbbb95740e62a7f0437cd0df0dcd43ac255b163e4)
            check_type(argname="argument delivery_stream_name", value=delivery_stream_name, expected_type=type_hints["delivery_stream_name"])
            check_type(argname="argument destinations", value=destinations, expected_type=type_hints["destinations"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument source_stream", value=source_stream, expected_type=type_hints["source_stream"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if delivery_stream_name is not None:
            self._values["delivery_stream_name"] = delivery_stream_name
        if destinations is not None:
            self._values["destinations"] = destinations
        if encryption is not None:
            self._values["encryption"] = encryption
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if role is not None:
            self._values["role"] = role
        if source_stream is not None:
            self._values["source_stream"] = source_stream

    @builtins.property
    def delivery_stream_name(self) -> typing.Optional[builtins.str]:
        '''A name for the delivery stream.

        :default: - a name is generated by CloudFormation.
        '''
        result = self._values.get("delivery_stream_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destinations(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.IDestination]]:
        '''The destinations that this delivery stream will deliver data to.

        Only a singleton array is supported at this time.
        '''
        result = self._values.get("destinations")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.IDestination]], result)

    @builtins.property
    def encryption(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.StreamEncryption]:
        '''Indicates the type of customer master key (CMK) to use for server-side encryption, if any.

        :default: StreamEncryption.UNENCRYPTED - unless ``encryptionKey`` is provided, in which case this will be implicitly set to ``StreamEncryption.CUSTOMER_MANAGED``
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.StreamEncryption], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''Customer managed key to server-side encrypt data in the stream.

        :default: - no KMS key will be used; if ``encryption`` is set to ``CUSTOMER_MANAGED``, a KMS key will be created for you
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role associated with this delivery stream.

        Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side.

        :default: - a role will be created with default permissions.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def source_stream(self) -> typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.IStream]:
        '''The Kinesis data stream to use as a source for this delivery stream.

        :default: - data must be written to the delivery stream via a direct put.
        '''
        result = self._values.get("source_stream")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.IStream], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeliveryStreamProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EMRServerlessCluster(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.EMRServerlessCluster",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        additional_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
        vpc_cidr: typing.Optional[builtins.str] = None,
        vpc_id: typing.Optional[builtins.str] = None,
        release_label: builtins.str,
        type: builtins.str,
        architecture: typing.Optional[builtins.str] = None,
        auto_start_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStartConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        auto_stop_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStopConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        image_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ImageConfigurationInputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        initial_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InitialCapacityConfigKeyValuePairProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        interactive_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InteractiveConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        maximum_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MaximumAllowedResourcesProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        monitoring_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MonitoringConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        name: typing.Optional[builtins.str] = None,
        network_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        runtime_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ConfigurationObjectProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        scheduler_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.SchedulerConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        worker_type_specifications: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Mapping[builtins.str, typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.WorkerTypeSpecificationInputProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param additional_policy_statements: Additional policy statements to add to the emr role.
        :param s3_bucket: S3 Bucket.
        :param security_group: Security Group.
        :param vpc_cidr: The IP range (CIDR notation) for this VPC.
        :param vpc_id: Existing vpc id.
        :param release_label: The EMR release associated with the application.
        :param type: The type of application, such as Spark or Hive.
        :param architecture: The CPU architecture of an application.
        :param auto_start_configuration: The configuration for an application to automatically start on job submission.
        :param auto_stop_configuration: The configuration for an application to automatically stop after a certain amount of time being idle.
        :param image_configuration: The image configuration applied to all worker types.
        :param initial_capacity: The initial capacity of the application.
        :param interactive_configuration: The interactive configuration object that enables the interactive use cases for an application.
        :param maximum_capacity: The maximum capacity of the application. This is cumulative across all workers at any given point in time during the lifespan of the application is created. No new resources will be created once any one of the defined limits is hit.
        :param monitoring_configuration: A configuration specification to be used when provisioning an application. A configuration consists of a classification, properties, and optional nested configurations. A classification refers to an application-specific configuration file. Properties are the settings you want to change in that file.
        :param name: The name of the application.
        :param network_configuration: The network configuration for customer VPC connectivity for the application.
        :param runtime_configuration: The `Configuration <https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_Configuration.html>`_ specifications of an application. Each configuration consists of a classification and properties. You use this parameter when creating or updating an application. To see the runtimeConfiguration object of an application, run the `GetApplication <https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_GetApplication.html>`_ API operation.
        :param scheduler_configuration: The scheduler configuration for batch and streaming jobs running on this application. Supported with release labels emr-7.0.0 and above.
        :param tags: The tags assigned to the application.
        :param worker_type_specifications: The specification applied to each worker type.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83d66a5f4ea6335b061a6877ac3664b7458c10cb62db78fcee7fdf475a19fee5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EMRServerlessClusterProps(
            additional_policy_statements=additional_policy_statements,
            s3_bucket=s3_bucket,
            security_group=security_group,
            vpc_cidr=vpc_cidr,
            vpc_id=vpc_id,
            release_label=release_label,
            type=type,
            architecture=architecture,
            auto_start_configuration=auto_start_configuration,
            auto_stop_configuration=auto_stop_configuration,
            image_configuration=image_configuration,
            initial_capacity=initial_capacity,
            interactive_configuration=interactive_configuration,
            maximum_capacity=maximum_capacity,
            monitoring_configuration=monitoring_configuration,
            name=name,
            network_configuration=network_configuration,
            runtime_configuration=runtime_configuration,
            scheduler_configuration=scheduler_configuration,
            tags=tags,
            worker_type_specifications=worker_type_specifications,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createVpc")
    def create_vpc(
        self,
        scope: _constructs_77d1e7e8.Construct,
        resource_name: builtins.str,
        vpc_cidr: builtins.str,
    ) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''
        :param scope: -
        :param resource_name: -
        :param vpc_cidr: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__864be4d07f911163bb991815f5a8c0561cfd97d707e687ef07552b1d38bb82d2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument resource_name", value=resource_name, expected_type=type_hints["resource_name"])
            check_type(argname="argument vpc_cidr", value=vpc_cidr, expected_type=type_hints["vpc_cidr"])
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.invoke(self, "createVpc", [scope, resource_name, vpc_cidr]))

    @builtins.property
    @jsii.member(jsii_name="emrServerlessApplication")
    def emr_serverless_application(
        self,
    ) -> _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication:
        return typing.cast(_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication, jsii.get(self, "emrServerlessApplication"))

    @builtins.property
    @jsii.member(jsii_name="networkConfiguration")
    def network_configuration(
        self,
    ) -> _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty:
        return typing.cast(_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty, jsii.get(self, "networkConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "s3Bucket"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup], jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="aws-ddk-core.EMRServerlessClusterProps",
    jsii_struct_bases=[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplicationProps],
    name_mapping={
        "release_label": "releaseLabel",
        "type": "type",
        "architecture": "architecture",
        "auto_start_configuration": "autoStartConfiguration",
        "auto_stop_configuration": "autoStopConfiguration",
        "image_configuration": "imageConfiguration",
        "initial_capacity": "initialCapacity",
        "interactive_configuration": "interactiveConfiguration",
        "maximum_capacity": "maximumCapacity",
        "monitoring_configuration": "monitoringConfiguration",
        "name": "name",
        "network_configuration": "networkConfiguration",
        "runtime_configuration": "runtimeConfiguration",
        "scheduler_configuration": "schedulerConfiguration",
        "tags": "tags",
        "worker_type_specifications": "workerTypeSpecifications",
        "additional_policy_statements": "additionalPolicyStatements",
        "s3_bucket": "s3Bucket",
        "security_group": "securityGroup",
        "vpc_cidr": "vpcCidr",
        "vpc_id": "vpcId",
    },
)
class EMRServerlessClusterProps(
    _aws_cdk_aws_emrserverless_ceddda9d.CfnApplicationProps,
):
    def __init__(
        self,
        *,
        release_label: builtins.str,
        type: builtins.str,
        architecture: typing.Optional[builtins.str] = None,
        auto_start_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStartConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        auto_stop_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStopConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        image_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ImageConfigurationInputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        initial_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InitialCapacityConfigKeyValuePairProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        interactive_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InteractiveConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        maximum_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MaximumAllowedResourcesProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        monitoring_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MonitoringConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        name: typing.Optional[builtins.str] = None,
        network_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        runtime_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ConfigurationObjectProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        scheduler_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.SchedulerConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        worker_type_specifications: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Mapping[builtins.str, typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.WorkerTypeSpecificationInputProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        additional_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
        vpc_cidr: typing.Optional[builtins.str] = None,
        vpc_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param release_label: The EMR release associated with the application.
        :param type: The type of application, such as Spark or Hive.
        :param architecture: The CPU architecture of an application.
        :param auto_start_configuration: The configuration for an application to automatically start on job submission.
        :param auto_stop_configuration: The configuration for an application to automatically stop after a certain amount of time being idle.
        :param image_configuration: The image configuration applied to all worker types.
        :param initial_capacity: The initial capacity of the application.
        :param interactive_configuration: The interactive configuration object that enables the interactive use cases for an application.
        :param maximum_capacity: The maximum capacity of the application. This is cumulative across all workers at any given point in time during the lifespan of the application is created. No new resources will be created once any one of the defined limits is hit.
        :param monitoring_configuration: A configuration specification to be used when provisioning an application. A configuration consists of a classification, properties, and optional nested configurations. A classification refers to an application-specific configuration file. Properties are the settings you want to change in that file.
        :param name: The name of the application.
        :param network_configuration: The network configuration for customer VPC connectivity for the application.
        :param runtime_configuration: The `Configuration <https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_Configuration.html>`_ specifications of an application. Each configuration consists of a classification and properties. You use this parameter when creating or updating an application. To see the runtimeConfiguration object of an application, run the `GetApplication <https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_GetApplication.html>`_ API operation.
        :param scheduler_configuration: The scheduler configuration for batch and streaming jobs running on this application. Supported with release labels emr-7.0.0 and above.
        :param tags: The tags assigned to the application.
        :param worker_type_specifications: The specification applied to each worker type.
        :param additional_policy_statements: Additional policy statements to add to the emr role.
        :param s3_bucket: S3 Bucket.
        :param security_group: Security Group.
        :param vpc_cidr: The IP range (CIDR notation) for this VPC.
        :param vpc_id: Existing vpc id.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dff46b98beafa0af6fc125923b2225092c53114f275e10e2732de3f4d3cd2573)
            check_type(argname="argument release_label", value=release_label, expected_type=type_hints["release_label"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument architecture", value=architecture, expected_type=type_hints["architecture"])
            check_type(argname="argument auto_start_configuration", value=auto_start_configuration, expected_type=type_hints["auto_start_configuration"])
            check_type(argname="argument auto_stop_configuration", value=auto_stop_configuration, expected_type=type_hints["auto_stop_configuration"])
            check_type(argname="argument image_configuration", value=image_configuration, expected_type=type_hints["image_configuration"])
            check_type(argname="argument initial_capacity", value=initial_capacity, expected_type=type_hints["initial_capacity"])
            check_type(argname="argument interactive_configuration", value=interactive_configuration, expected_type=type_hints["interactive_configuration"])
            check_type(argname="argument maximum_capacity", value=maximum_capacity, expected_type=type_hints["maximum_capacity"])
            check_type(argname="argument monitoring_configuration", value=monitoring_configuration, expected_type=type_hints["monitoring_configuration"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument network_configuration", value=network_configuration, expected_type=type_hints["network_configuration"])
            check_type(argname="argument runtime_configuration", value=runtime_configuration, expected_type=type_hints["runtime_configuration"])
            check_type(argname="argument scheduler_configuration", value=scheduler_configuration, expected_type=type_hints["scheduler_configuration"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument worker_type_specifications", value=worker_type_specifications, expected_type=type_hints["worker_type_specifications"])
            check_type(argname="argument additional_policy_statements", value=additional_policy_statements, expected_type=type_hints["additional_policy_statements"])
            check_type(argname="argument s3_bucket", value=s3_bucket, expected_type=type_hints["s3_bucket"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument vpc_cidr", value=vpc_cidr, expected_type=type_hints["vpc_cidr"])
            check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "release_label": release_label,
            "type": type,
        }
        if architecture is not None:
            self._values["architecture"] = architecture
        if auto_start_configuration is not None:
            self._values["auto_start_configuration"] = auto_start_configuration
        if auto_stop_configuration is not None:
            self._values["auto_stop_configuration"] = auto_stop_configuration
        if image_configuration is not None:
            self._values["image_configuration"] = image_configuration
        if initial_capacity is not None:
            self._values["initial_capacity"] = initial_capacity
        if interactive_configuration is not None:
            self._values["interactive_configuration"] = interactive_configuration
        if maximum_capacity is not None:
            self._values["maximum_capacity"] = maximum_capacity
        if monitoring_configuration is not None:
            self._values["monitoring_configuration"] = monitoring_configuration
        if name is not None:
            self._values["name"] = name
        if network_configuration is not None:
            self._values["network_configuration"] = network_configuration
        if runtime_configuration is not None:
            self._values["runtime_configuration"] = runtime_configuration
        if scheduler_configuration is not None:
            self._values["scheduler_configuration"] = scheduler_configuration
        if tags is not None:
            self._values["tags"] = tags
        if worker_type_specifications is not None:
            self._values["worker_type_specifications"] = worker_type_specifications
        if additional_policy_statements is not None:
            self._values["additional_policy_statements"] = additional_policy_statements
        if s3_bucket is not None:
            self._values["s3_bucket"] = s3_bucket
        if security_group is not None:
            self._values["security_group"] = security_group
        if vpc_cidr is not None:
            self._values["vpc_cidr"] = vpc_cidr
        if vpc_id is not None:
            self._values["vpc_id"] = vpc_id

    @builtins.property
    def release_label(self) -> builtins.str:
        '''The EMR release associated with the application.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-releaselabel
        '''
        result = self._values.get("release_label")
        assert result is not None, "Required property 'release_label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of application, such as Spark or Hive.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-type
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def architecture(self) -> typing.Optional[builtins.str]:
        '''The CPU architecture of an application.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-architecture
        '''
        result = self._values.get("architecture")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_start_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStartConfigurationProperty]]:
        '''The configuration for an application to automatically start on job submission.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-autostartconfiguration
        '''
        result = self._values.get("auto_start_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStartConfigurationProperty]], result)

    @builtins.property
    def auto_stop_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStopConfigurationProperty]]:
        '''The configuration for an application to automatically stop after a certain amount of time being idle.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-autostopconfiguration
        '''
        result = self._values.get("auto_stop_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStopConfigurationProperty]], result)

    @builtins.property
    def image_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ImageConfigurationInputProperty]]:
        '''The image configuration applied to all worker types.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-imageconfiguration
        '''
        result = self._values.get("image_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ImageConfigurationInputProperty]], result)

    @builtins.property
    def initial_capacity(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InitialCapacityConfigKeyValuePairProperty]]]]:
        '''The initial capacity of the application.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-initialcapacity
        '''
        result = self._values.get("initial_capacity")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InitialCapacityConfigKeyValuePairProperty]]]], result)

    @builtins.property
    def interactive_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InteractiveConfigurationProperty]]:
        '''The interactive configuration object that enables the interactive use cases for an application.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-interactiveconfiguration
        '''
        result = self._values.get("interactive_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InteractiveConfigurationProperty]], result)

    @builtins.property
    def maximum_capacity(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MaximumAllowedResourcesProperty]]:
        '''The maximum capacity of the application.

        This is cumulative across all workers at any given point in time during the lifespan of the application is created. No new resources will be created once any one of the defined limits is hit.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-maximumcapacity
        '''
        result = self._values.get("maximum_capacity")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MaximumAllowedResourcesProperty]], result)

    @builtins.property
    def monitoring_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MonitoringConfigurationProperty]]:
        '''A configuration specification to be used when provisioning an application.

        A configuration consists of a classification, properties, and optional nested configurations. A classification refers to an application-specific configuration file. Properties are the settings you want to change in that file.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-monitoringconfiguration
        '''
        result = self._values.get("monitoring_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MonitoringConfigurationProperty]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the application.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty]]:
        '''The network configuration for customer VPC connectivity for the application.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-networkconfiguration
        '''
        result = self._values.get("network_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty]], result)

    @builtins.property
    def runtime_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ConfigurationObjectProperty]]]]:
        '''The `Configuration <https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_Configuration.html>`_ specifications of an application. Each configuration consists of a classification and properties. You use this parameter when creating or updating an application. To see the runtimeConfiguration object of an application, run the `GetApplication <https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_GetApplication.html>`_ API operation.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-runtimeconfiguration
        '''
        result = self._values.get("runtime_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ConfigurationObjectProperty]]]], result)

    @builtins.property
    def scheduler_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.SchedulerConfigurationProperty]]:
        '''The scheduler configuration for batch and streaming jobs running on this application.

        Supported with release labels emr-7.0.0 and above.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-schedulerconfiguration
        '''
        result = self._values.get("scheduler_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.SchedulerConfigurationProperty]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''The tags assigned to the application.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]], result)

    @builtins.property
    def worker_type_specifications(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Mapping[builtins.str, typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.WorkerTypeSpecificationInputProperty]]]]:
        '''The specification applied to each worker type.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emrserverless-application.html#cfn-emrserverless-application-workertypespecifications
        '''
        result = self._values.get("worker_type_specifications")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Mapping[builtins.str, typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.WorkerTypeSpecificationInputProperty]]]], result)

    @builtins.property
    def additional_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Additional policy statements to add to the emr role.'''
        result = self._values.get("additional_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def s3_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''S3 Bucket.'''
        result = self._values.get("s3_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]:
        '''Security Group.'''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup], result)

    @builtins.property
    def vpc_cidr(self) -> typing.Optional[builtins.str]:
        '''The IP range (CIDR notation) for this VPC.'''
        result = self._values.get("vpc_cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_id(self) -> typing.Optional[builtins.str]:
        '''Existing vpc id.'''
        result = self._values.get("vpc_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EMRServerlessClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.EnvironmentConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "bootstrap": "bootstrap",
        "props": "props",
        "region": "region",
        "resources": "resources",
        "tags": "tags",
    },
)
class EnvironmentConfiguration:
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        bootstrap: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        props: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        region: typing.Optional[builtins.str] = None,
        resources: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param account: 
        :param bootstrap: 
        :param props: 
        :param region: 
        :param resources: 
        :param tags: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf306c436463dcb56197f32e9c4793604595ef2ca8f42b2d72de058d5806870c)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument bootstrap", value=bootstrap, expected_type=type_hints["bootstrap"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument resources", value=resources, expected_type=type_hints["resources"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if bootstrap is not None:
            self._values["bootstrap"] = bootstrap
        if props is not None:
            self._values["props"] = props
        if region is not None:
            self._values["region"] = region
        if resources is not None:
            self._values["resources"] = resources
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bootstrap(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("bootstrap")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def props(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        result = self._values.get("props")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resources(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        result = self._values.get("resources")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnvironmentConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.GetConfigProps",
    jsii_struct_bases=[],
    name_mapping={"config": "config"},
)
class GetConfigProps:
    def __init__(
        self,
        *,
        config: typing.Optional[typing.Union[builtins.str, typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param config: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dba6810d9499d40d626ee84f10a13e1cade1e4a1602afa74c9dd333695965bd)
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if config is not None:
            self._values["config"] = config

    @builtins.property
    def config(self) -> typing.Optional[typing.Union[builtins.str, Configuration]]:
        result = self._values.get("config")
        return typing.cast(typing.Optional[typing.Union[builtins.str, Configuration]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GetConfigProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.GetEnvConfigProps",
    jsii_struct_bases=[],
    name_mapping={"environment_id": "environmentId", "config_path": "configPath"},
)
class GetEnvConfigProps:
    def __init__(
        self,
        *,
        environment_id: builtins.str,
        config_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param environment_id: Environment identifier.
        :param config_path: Relative path to config file. Defaults to './ddk.json'
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__392d4bf9e0a3416c4cbfe2cfcca884cc2b98f96b99a23a03e386497b6cfd2fef)
            check_type(argname="argument environment_id", value=environment_id, expected_type=type_hints["environment_id"])
            check_type(argname="argument config_path", value=config_path, expected_type=type_hints["config_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "environment_id": environment_id,
        }
        if config_path is not None:
            self._values["config_path"] = config_path

    @builtins.property
    def environment_id(self) -> builtins.str:
        '''Environment identifier.'''
        result = self._values.get("environment_id")
        assert result is not None, "Required property 'environment_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config_path(self) -> typing.Optional[builtins.str]:
        '''Relative path to config file.

        Defaults to './ddk.json'
        '''
        result = self._values.get("config_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GetEnvConfigProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.GetEnvironmentProps",
    jsii_struct_bases=[],
    name_mapping={"config_path": "configPath", "environment_id": "environmentId"},
)
class GetEnvironmentProps:
    def __init__(
        self,
        *,
        config_path: typing.Optional[builtins.str] = None,
        environment_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config_path: Relative path to config file. Defaults to './ddk.json'
        :param environment_id: Environment identifier.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1d1864ebb63e794b66b601804d8a186ccc2fe70e5c1aeea9def8ecd1ab83dde)
            check_type(argname="argument config_path", value=config_path, expected_type=type_hints["config_path"])
            check_type(argname="argument environment_id", value=environment_id, expected_type=type_hints["environment_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if config_path is not None:
            self._values["config_path"] = config_path
        if environment_id is not None:
            self._values["environment_id"] = environment_id

    @builtins.property
    def config_path(self) -> typing.Optional[builtins.str]:
        '''Relative path to config file.

        Defaults to './ddk.json'
        '''
        result = self._values.get("config_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_id(self) -> typing.Optional[builtins.str]:
        '''Environment identifier.'''
        result = self._values.get("environment_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GetEnvironmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.GetSynthActionProps",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "additional_install_commands": "additionalInstallCommands",
        "cdk_version": "cdkVersion",
        "codeartifact_domain": "codeartifactDomain",
        "codeartifact_domain_owner": "codeartifactDomainOwner",
        "codeartifact_repository": "codeartifactRepository",
        "code_pipeline_source": "codePipelineSource",
        "env": "env",
        "partition": "partition",
        "region": "region",
        "role_policy_statements": "rolePolicyStatements",
    },
)
class GetSynthActionProps:
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        additional_install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_version: typing.Optional[builtins.str] = None,
        codeartifact_domain: typing.Optional[builtins.str] = None,
        codeartifact_domain_owner: typing.Optional[builtins.str] = None,
        codeartifact_repository: typing.Optional[builtins.str] = None,
        code_pipeline_source: typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        partition: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    ) -> None:
        '''
        :param account: 
        :param additional_install_commands: 
        :param cdk_version: 
        :param codeartifact_domain: 
        :param codeartifact_domain_owner: 
        :param codeartifact_repository: 
        :param code_pipeline_source: 
        :param env: 
        :param partition: 
        :param region: 
        :param role_policy_statements: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b411e230303f93f36fe42f88f3ae59e51d4746a608fa21c8fe560bb5fe18a352)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument additional_install_commands", value=additional_install_commands, expected_type=type_hints["additional_install_commands"])
            check_type(argname="argument cdk_version", value=cdk_version, expected_type=type_hints["cdk_version"])
            check_type(argname="argument codeartifact_domain", value=codeartifact_domain, expected_type=type_hints["codeartifact_domain"])
            check_type(argname="argument codeartifact_domain_owner", value=codeartifact_domain_owner, expected_type=type_hints["codeartifact_domain_owner"])
            check_type(argname="argument codeartifact_repository", value=codeartifact_repository, expected_type=type_hints["codeartifact_repository"])
            check_type(argname="argument code_pipeline_source", value=code_pipeline_source, expected_type=type_hints["code_pipeline_source"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument role_policy_statements", value=role_policy_statements, expected_type=type_hints["role_policy_statements"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if additional_install_commands is not None:
            self._values["additional_install_commands"] = additional_install_commands
        if cdk_version is not None:
            self._values["cdk_version"] = cdk_version
        if codeartifact_domain is not None:
            self._values["codeartifact_domain"] = codeartifact_domain
        if codeartifact_domain_owner is not None:
            self._values["codeartifact_domain_owner"] = codeartifact_domain_owner
        if codeartifact_repository is not None:
            self._values["codeartifact_repository"] = codeartifact_repository
        if code_pipeline_source is not None:
            self._values["code_pipeline_source"] = code_pipeline_source
        if env is not None:
            self._values["env"] = env
        if partition is not None:
            self._values["partition"] = partition
        if region is not None:
            self._values["region"] = region
        if role_policy_statements is not None:
            self._values["role_policy_statements"] = role_policy_statements

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_install_commands(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("additional_install_commands")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cdk_version(self) -> typing.Optional[builtins.str]:
        result = self._values.get("cdk_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codeartifact_domain(self) -> typing.Optional[builtins.str]:
        result = self._values.get("codeartifact_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codeartifact_domain_owner(self) -> typing.Optional[builtins.str]:
        result = self._values.get("codeartifact_domain_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codeartifact_repository(self) -> typing.Optional[builtins.str]:
        result = self._values.get("codeartifact_repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_pipeline_source(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer]:
        result = self._values.get("code_pipeline_source")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        result = self._values.get("role_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GetSynthActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.GetTagsProps",
    jsii_struct_bases=[],
    name_mapping={"config_path": "configPath", "environment_id": "environmentId"},
)
class GetTagsProps:
    def __init__(
        self,
        *,
        config_path: typing.Optional[builtins.str] = None,
        environment_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config_path: Relative path to config file. Defaults to './ddk.json'
        :param environment_id: Environment identifier.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f80411a398b3a95cafcc083fedf809e35c9f9d3c872682fa20c2c416251da930)
            check_type(argname="argument config_path", value=config_path, expected_type=type_hints["config_path"])
            check_type(argname="argument environment_id", value=environment_id, expected_type=type_hints["environment_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if config_path is not None:
            self._values["config_path"] = config_path
        if environment_id is not None:
            self._values["environment_id"] = environment_id

    @builtins.property
    def config_path(self) -> typing.Optional[builtins.str]:
        '''Relative path to config file.

        Defaults to './ddk.json'
        '''
        result = self._values.get("config_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_id(self) -> typing.Optional[builtins.str]:
        '''Environment identifier.'''
        result = self._values.get("environment_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GetTagsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GlueFactory(metaclass=jsii.JSIIMeta, jsii_type="aws-ddk-core.GlueFactory"):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="job")
    @builtins.classmethod
    def job(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        glue_job_properties: typing.Union[typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PythonShellJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkStreamingJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkFlexEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkFlexEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkStreamingJobProps, typing.Dict[builtins.str, typing.Any]]],
        glue_job_type: builtins.str,
    ) -> typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkEtlJob, _aws_cdk_aws_glue_alpha_ce674d29.PythonShellJob, _aws_cdk_aws_glue_alpha_ce674d29.PySparkStreamingJob, _aws_cdk_aws_glue_alpha_ce674d29.PySparkFlexEtlJob, _aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkEtlJob, _aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkFlexEtlJob, _aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkStreamingJob]:
        '''
        :param scope: -
        :param id: -
        :param glue_job_properties: 
        :param glue_job_type: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de56c47dda07ed1c4eda1133b7152caa819140d8ea5277eaf41f2802c2c16bfd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GlueFactoryProps(
            glue_job_properties=glue_job_properties, glue_job_type=glue_job_type
        )

        return typing.cast(typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkEtlJob, _aws_cdk_aws_glue_alpha_ce674d29.PythonShellJob, _aws_cdk_aws_glue_alpha_ce674d29.PySparkStreamingJob, _aws_cdk_aws_glue_alpha_ce674d29.PySparkFlexEtlJob, _aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkEtlJob, _aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkFlexEtlJob, _aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkStreamingJob], jsii.sinvoke(cls, "job", [scope, id, props]))


@jsii.data_type(
    jsii_type="aws-ddk-core.GlueFactoryProps",
    jsii_struct_bases=[],
    name_mapping={
        "glue_job_properties": "glueJobProperties",
        "glue_job_type": "glueJobType",
    },
)
class GlueFactoryProps:
    def __init__(
        self,
        *,
        glue_job_properties: typing.Union[typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PythonShellJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkStreamingJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkFlexEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkFlexEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkStreamingJobProps, typing.Dict[builtins.str, typing.Any]]],
        glue_job_type: builtins.str,
    ) -> None:
        '''
        :param glue_job_properties: 
        :param glue_job_type: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4195fefbe897d7974bd882c0bba9cb93090e2d887022e38416d5ae73a33a94e6)
            check_type(argname="argument glue_job_properties", value=glue_job_properties, expected_type=type_hints["glue_job_properties"])
            check_type(argname="argument glue_job_type", value=glue_job_type, expected_type=type_hints["glue_job_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "glue_job_properties": glue_job_properties,
            "glue_job_type": glue_job_type,
        }

    @builtins.property
    def glue_job_properties(
        self,
    ) -> typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkEtlJobProps, _aws_cdk_aws_glue_alpha_ce674d29.PythonShellJobProps, _aws_cdk_aws_glue_alpha_ce674d29.PySparkStreamingJobProps, _aws_cdk_aws_glue_alpha_ce674d29.PySparkFlexEtlJobProps, _aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkEtlJobProps, _aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkFlexEtlJobProps, _aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkStreamingJobProps]:
        result = self._values.get("glue_job_properties")
        assert result is not None, "Required property 'glue_job_properties' is missing"
        return typing.cast(typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkEtlJobProps, _aws_cdk_aws_glue_alpha_ce674d29.PythonShellJobProps, _aws_cdk_aws_glue_alpha_ce674d29.PySparkStreamingJobProps, _aws_cdk_aws_glue_alpha_ce674d29.PySparkFlexEtlJobProps, _aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkEtlJobProps, _aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkFlexEtlJobProps, _aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkStreamingJobProps], result)

    @builtins.property
    def glue_job_type(self) -> builtins.str:
        result = self._values.get("glue_job_type")
        assert result is not None, "Required property 'glue_job_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GlueFactoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="aws-ddk-core.GlueJobType")
class GlueJobType(enum.Enum):
    PY_SPARK_ETL_JOB = "PY_SPARK_ETL_JOB"
    PYTHON_SHELL_JOB = "PYTHON_SHELL_JOB"
    PY_SPARK_STREAMING_JOB = "PY_SPARK_STREAMING_JOB"
    PY_SPARK_FLEX_ETL_JOB = "PY_SPARK_FLEX_ETL_JOB"
    SCALA_SPARK_ETL_JOB = "SCALA_SPARK_ETL_JOB"
    SCALA_SPARK_FLEX_ETL_JOB = "SCALA_SPARK_FLEX_ETL_JOB"
    SCALA_SPARK_STREAMING_JOB = "SCALA_SPARK_STREAMING_JOB"


class KmsFactory(metaclass=jsii.JSIIMeta, jsii_type="aws-ddk-core.KmsFactory"):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="key")
    @builtins.classmethod
    def key(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        admins: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IPrincipal]] = None,
        alias: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_key_rotation: typing.Optional[builtins.bool] = None,
        key_spec: typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeySpec] = None,
        key_usage: typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyUsage] = None,
        multi_region: typing.Optional[builtins.bool] = None,
        pending_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        rotation_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> _aws_cdk_aws_kms_ceddda9d.Key:
        '''
        :param scope: -
        :param id: -
        :param admins: A list of principals to add as key administrators to the key policy. Key administrators have permissions to manage the key (e.g., change permissions, revoke), but do not have permissions to use the key in cryptographic operations (e.g., encrypt, decrypt). These principals will be added to the default key policy (if none specified), or to the specified policy (if provided). Default: []
        :param alias: Initial alias to add to the key. More aliases can be added later by calling ``addAlias``. Default: - No alias is added for the key.
        :param description: A description of the key. Use a description that helps your users decide whether the key is appropriate for a particular task. Default: - No description.
        :param enabled: Indicates whether the key is available for use. Default: - Key is enabled.
        :param enable_key_rotation: Indicates whether AWS KMS rotates the key. Default: false
        :param key_spec: The cryptographic configuration of the key. The valid value depends on usage of the key. IMPORTANT: If you change this property of an existing key, the existing key is scheduled for deletion and a new key is created with the specified value. Default: KeySpec.SYMMETRIC_DEFAULT
        :param key_usage: The cryptographic operations for which the key can be used. IMPORTANT: If you change this property of an existing key, the existing key is scheduled for deletion and a new key is created with the specified value. Default: KeyUsage.ENCRYPT_DECRYPT
        :param multi_region: Creates a multi-Region primary key that you can replicate in other AWS Regions. You can't change the ``multiRegion`` value after the KMS key is created. IMPORTANT: If you change the value of the ``multiRegion`` property on an existing KMS key, the update request fails, regardless of the value of the UpdateReplacePolicy attribute. This prevents you from accidentally deleting a KMS key by changing an immutable property value. Default: false
        :param pending_window: Specifies the number of days in the waiting period before AWS KMS deletes a CMK that has been removed from a CloudFormation stack. When you remove a customer master key (CMK) from a CloudFormation stack, AWS KMS schedules the CMK for deletion and starts the mandatory waiting period. The PendingWindowInDays property determines the length of waiting period. During the waiting period, the key state of CMK is Pending Deletion, which prevents the CMK from being used in cryptographic operations. When the waiting period expires, AWS KMS permanently deletes the CMK. Enter a value between 7 and 30 days. Default: - 30 days
        :param policy: Custom policy document to attach to the KMS key. NOTE - If the ``@aws-cdk/aws-kms:defaultKeyPolicies`` feature flag is set (the default for new projects), this policy will *override* the default key policy and become the only key policy for the key. If the feature flag is not set, this policy will be appended to the default key policy. Default: - A policy document with permissions for the account root to administer the key will be created.
        :param removal_policy: Whether the encryption key should be retained when it is removed from the Stack. This is useful when one wants to retain access to data that was encrypted with a key that is being retired. Default: RemovalPolicy.Retain
        :param rotation_period: The period between each automatic rotation. Default: - set by CFN to 365 days.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a14864520200528bc5a9369b081737198f4eb3e97462ea981304386c09050813)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_kms_ceddda9d.KeyProps(
            admins=admins,
            alias=alias,
            description=description,
            enabled=enabled,
            enable_key_rotation=enable_key_rotation,
            key_spec=key_spec,
            key_usage=key_usage,
            multi_region=multi_region,
            pending_window=pending_window,
            policy=policy,
            removal_policy=removal_policy,
            rotation_period=rotation_period,
        )

        return typing.cast(_aws_cdk_aws_kms_ceddda9d.Key, jsii.sinvoke(cls, "key", [scope, id, props]))


class MWAAEnvironment(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.MWAAEnvironment",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        additional_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        dag_files: typing.Optional[typing.Sequence[builtins.str]] = None,
        dag_processing_logs: typing.Optional[builtins.str] = None,
        plugin_file: typing.Optional[builtins.str] = None,
        requirements_file: typing.Optional[builtins.str] = None,
        s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        scheduler_logs_level: typing.Optional[builtins.str] = None,
        task_logs_level: typing.Optional[builtins.str] = None,
        vpc_cidr: typing.Optional[builtins.str] = None,
        vpc_id: typing.Optional[builtins.str] = None,
        webserver_logs_level: typing.Optional[builtins.str] = None,
        worker_logs_level: typing.Optional[builtins.str] = None,
        name: builtins.str,
        airflow_configuration_options: typing.Any = None,
        airflow_version: typing.Optional[builtins.str] = None,
        dag_s3_path: typing.Optional[builtins.str] = None,
        endpoint_management: typing.Optional[builtins.str] = None,
        environment_class: typing.Optional[builtins.str] = None,
        execution_role_arn: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        logging_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment.LoggingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        max_webservers: typing.Optional[jsii.Number] = None,
        max_workers: typing.Optional[jsii.Number] = None,
        min_webservers: typing.Optional[jsii.Number] = None,
        min_workers: typing.Optional[jsii.Number] = None,
        network_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        plugins_s3_object_version: typing.Optional[builtins.str] = None,
        plugins_s3_path: typing.Optional[builtins.str] = None,
        requirements_s3_object_version: typing.Optional[builtins.str] = None,
        requirements_s3_path: typing.Optional[builtins.str] = None,
        schedulers: typing.Optional[jsii.Number] = None,
        source_bucket_arn: typing.Optional[builtins.str] = None,
        startup_script_s3_object_version: typing.Optional[builtins.str] = None,
        startup_script_s3_path: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
        webserver_access_mode: typing.Optional[builtins.str] = None,
        weekly_maintenance_window_start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param additional_policy_statements: Additional policy statements to add to the airflow execution role.
        :param dag_files: File(s) to be uploaded to dags location in s3 bucket.
        :param dag_processing_logs: Log level for DagProcessing.
        :param plugin_file: Plugin file to be uploaded to plugin path in S3. 'pluginsS3Path' must be specified as well.
        :param requirements_file: Requirements file to be uploaded to plugin path in S3. 'requirementsS3Path' must be specified as well.
        :param s3_bucket: S3 Bucket.
        :param scheduler_logs_level: Log level for SchedulerLogs.
        :param task_logs_level: Log level for TaskLogs.
        :param vpc_cidr: The IP range (CIDR notation) for this VPC.
        :param vpc_id: Existing vpc id.
        :param webserver_logs_level: Log level for WebserverLogs.
        :param worker_logs_level: Log level for WorkerLogs.
        :param name: The name of your Amazon MWAA environment.
        :param airflow_configuration_options: A list of key-value pairs containing the Airflow configuration options for your environment. For example, ``core.default_timezone: utc`` . To learn more, see `Apache Airflow configuration options <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-env-variables.html>`_ .
        :param airflow_version: The version of Apache Airflow to use for the environment. If no value is specified, defaults to the latest version. If you specify a newer version number for an existing environment, the version update requires some service interruption before taking effect. *Allowed Values* : ``1.10.12`` | ``2.0.2`` | ``2.2.2`` | ``2.4.3`` | ``2.5.1`` | ``2.6.3`` | ``2.7.2`` | ``2.8.1`` | ``2.9.2`` (latest)
        :param dag_s3_path: The relative path to the DAGs folder on your Amazon S3 bucket. For example, ``dags`` . To learn more, see `Adding or updating DAGs <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-dag-folder.html>`_ .
        :param endpoint_management: Defines whether the VPC endpoints configured for the environment are created, and managed, by the customer or by Amazon MWAA. If set to ``SERVICE`` , Amazon MWAA will create and manage the required VPC endpoints in your VPC. If set to ``CUSTOMER`` , you must create, and manage, the VPC endpoints in your VPC.
        :param environment_class: The environment class type. Valid values: ``mw1.small`` , ``mw1.medium`` , ``mw1.large`` . To learn more, see `Amazon MWAA environment class <https://docs.aws.amazon.com/mwaa/latest/userguide/environment-class.html>`_ .
        :param execution_role_arn: The Amazon Resource Name (ARN) of the execution role in IAM that allows MWAA to access AWS resources in your environment. For example, ``arn:aws:iam::123456789:role/my-execution-role`` . To learn more, see `Amazon MWAA Execution role <https://docs.aws.amazon.com/mwaa/latest/userguide/mwaa-create-role.html>`_ .
        :param kms_key: The AWS Key Management Service (KMS) key to encrypt and decrypt the data in your environment. You can use an AWS KMS key managed by MWAA, or a customer-managed KMS key (advanced).
        :param logging_configuration: The Apache Airflow logs being sent to CloudWatch Logs: ``DagProcessingLogs`` , ``SchedulerLogs`` , ``TaskLogs`` , ``WebserverLogs`` , ``WorkerLogs`` .
        :param max_webservers: The maximum number of web servers that you want to run in your environment. Amazon MWAA scales the number of Apache Airflow web servers up to the number you specify for ``MaxWebservers`` when you interact with your Apache Airflow environment using Apache Airflow REST API, or the Apache Airflow CLI. For example, in scenarios where your workload requires network calls to the Apache Airflow REST API with a high transaction-per-second (TPS) rate, Amazon MWAA will increase the number of web servers up to the number set in ``MaxWebserers`` . As TPS rates decrease Amazon MWAA disposes of the additional web servers, and scales down to the number set in ``MinxWebserers`` . Valid values: For environments larger than mw1.micro, accepts values from ``2`` to ``5`` . Defaults to ``2`` for all environment sizes except mw1.micro, which defaults to ``1`` .
        :param max_workers: The maximum number of workers that you want to run in your environment. MWAA scales the number of Apache Airflow workers up to the number you specify in the ``MaxWorkers`` field. For example, ``20`` . When there are no more tasks running, and no more in the queue, MWAA disposes of the extra workers leaving the one worker that is included with your environment, or the number you specify in ``MinWorkers`` .
        :param min_webservers: The minimum number of web servers that you want to run in your environment. Amazon MWAA scales the number of Apache Airflow web servers up to the number you specify for ``MaxWebservers`` when you interact with your Apache Airflow environment using Apache Airflow REST API, or the Apache Airflow CLI. As the transaction-per-second rate, and the network load, decrease, Amazon MWAA disposes of the additional web servers, and scales down to the number set in ``MinxWebserers`` . Valid values: For environments larger than mw1.micro, accepts values from ``2`` to ``5`` . Defaults to ``2`` for all environment sizes except mw1.micro, which defaults to ``1`` .
        :param min_workers: The minimum number of workers that you want to run in your environment. MWAA scales the number of Apache Airflow workers up to the number you specify in the ``MaxWorkers`` field. When there are no more tasks running, and no more in the queue, MWAA disposes of the extra workers leaving the worker count you specify in the ``MinWorkers`` field. For example, ``2`` .
        :param network_configuration: The VPC networking components used to secure and enable network traffic between the AWS resources for your environment. To learn more, see `About networking on Amazon MWAA <https://docs.aws.amazon.com/mwaa/latest/userguide/networking-about.html>`_ .
        :param plugins_s3_object_version: The version of the plugins.zip file on your Amazon S3 bucket. To learn more, see `Installing custom plugins <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-dag-import-plugins.html>`_ .
        :param plugins_s3_path: The relative path to the ``plugins.zip`` file on your Amazon S3 bucket. For example, ``plugins.zip`` . To learn more, see `Installing custom plugins <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-dag-import-plugins.html>`_ .
        :param requirements_s3_object_version: The version of the requirements.txt file on your Amazon S3 bucket. To learn more, see `Installing Python dependencies <https://docs.aws.amazon.com/mwaa/latest/userguide/working-dags-dependencies.html>`_ .
        :param requirements_s3_path: The relative path to the ``requirements.txt`` file on your Amazon S3 bucket. For example, ``requirements.txt`` . To learn more, see `Installing Python dependencies <https://docs.aws.amazon.com/mwaa/latest/userguide/working-dags-dependencies.html>`_ .
        :param schedulers: The number of schedulers that you want to run in your environment. Valid values:. - *v2* - Accepts between 2 to 5. Defaults to 2. - *v1* - Accepts 1.
        :param source_bucket_arn: The Amazon Resource Name (ARN) of the Amazon S3 bucket where your DAG code and supporting files are stored. For example, ``arn:aws:s3:::my-airflow-bucket-unique-name`` . To learn more, see `Create an Amazon S3 bucket for Amazon MWAA <https://docs.aws.amazon.com/mwaa/latest/userguide/mwaa-s3-bucket.html>`_ .
        :param startup_script_s3_object_version: The version of the startup shell script in your Amazon S3 bucket. You must specify the `version ID <https://docs.aws.amazon.com/AmazonS3/latest/userguide/versioning-workflows.html>`_ that Amazon S3 assigns to the file every time you update the script. Version IDs are Unicode, UTF-8 encoded, URL-ready, opaque strings that are no more than 1,024 bytes long. The following is an example: ``3sL4kqtJlcpXroDTDmJ+rmSpXd3dIbrHY+MTRCxf3vjVBH40Nr8X8gdRQBpUMLUo`` For more information, see `Using a startup script <https://docs.aws.amazon.com/mwaa/latest/userguide/using-startup-script.html>`_ .
        :param startup_script_s3_path: The relative path to the startup shell script in your Amazon S3 bucket. For example, ``s3://mwaa-environment/startup.sh`` . Amazon MWAA runs the script as your environment starts, and before running the Apache Airflow process. You can use this script to install dependencies, modify Apache Airflow configuration options, and set environment variables. For more information, see `Using a startup script <https://docs.aws.amazon.com/mwaa/latest/userguide/using-startup-script.html>`_ .
        :param tags: The key-value tag pairs associated to your environment. For example, ``"Environment": "Staging"`` . To learn more, see `Tagging <https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html>`_ . If you specify new tags for an existing environment, the update requires service interruption before taking effect.
        :param webserver_access_mode: The Apache Airflow *Web server* access mode. To learn more, see `Apache Airflow access modes <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-networking.html>`_ . Valid values: ``PRIVATE_ONLY`` or ``PUBLIC_ONLY`` .
        :param weekly_maintenance_window_start: The day and time of the week to start weekly maintenance updates of your environment in the following format: ``DAY:HH:MM`` . For example: ``TUE:03:30`` . You can specify a start time in 30 minute increments only. Supported input includes the following: - MON|TUE|WED|THU|FRI|SAT|SUN:([01]\\d|2[0-3]):(00|30)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f57013032bd3f5e03e8cf2f82cc7c98b621d613c29a1e1844390ce9e164789e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MWAAEnvironmentProps(
            additional_policy_statements=additional_policy_statements,
            dag_files=dag_files,
            dag_processing_logs=dag_processing_logs,
            plugin_file=plugin_file,
            requirements_file=requirements_file,
            s3_bucket=s3_bucket,
            scheduler_logs_level=scheduler_logs_level,
            task_logs_level=task_logs_level,
            vpc_cidr=vpc_cidr,
            vpc_id=vpc_id,
            webserver_logs_level=webserver_logs_level,
            worker_logs_level=worker_logs_level,
            name=name,
            airflow_configuration_options=airflow_configuration_options,
            airflow_version=airflow_version,
            dag_s3_path=dag_s3_path,
            endpoint_management=endpoint_management,
            environment_class=environment_class,
            execution_role_arn=execution_role_arn,
            kms_key=kms_key,
            logging_configuration=logging_configuration,
            max_webservers=max_webservers,
            max_workers=max_workers,
            min_webservers=min_webservers,
            min_workers=min_workers,
            network_configuration=network_configuration,
            plugins_s3_object_version=plugins_s3_object_version,
            plugins_s3_path=plugins_s3_path,
            requirements_s3_object_version=requirements_s3_object_version,
            requirements_s3_path=requirements_s3_path,
            schedulers=schedulers,
            source_bucket_arn=source_bucket_arn,
            startup_script_s3_object_version=startup_script_s3_object_version,
            startup_script_s3_path=startup_script_s3_path,
            tags=tags,
            webserver_access_mode=webserver_access_mode,
            weekly_maintenance_window_start=weekly_maintenance_window_start,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createVpc")
    def create_vpc(
        self,
        scope: _constructs_77d1e7e8.Construct,
        environment_name: builtins.str,
        vpc_cidr: builtins.str,
    ) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''
        :param scope: -
        :param environment_name: -
        :param vpc_cidr: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__274336e52a6efd650b5a38d3d50c0d6df8879c749af035d91610fec06e12c9fb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument environment_name", value=environment_name, expected_type=type_hints["environment_name"])
            check_type(argname="argument vpc_cidr", value=vpc_cidr, expected_type=type_hints["vpc_cidr"])
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.invoke(self, "createVpc", [scope, environment_name, vpc_cidr]))

    @builtins.property
    @jsii.member(jsii_name="dagProcessingLogs")
    def dag_processing_logs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dagProcessingLogs"))

    @builtins.property
    @jsii.member(jsii_name="dagS3Path")
    def dag_s3_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dagS3Path"))

    @builtins.property
    @jsii.member(jsii_name="mwaaEnvironment")
    def mwaa_environment(self) -> _aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment:
        return typing.cast(_aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment, jsii.get(self, "mwaaEnvironment"))

    @builtins.property
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "s3Bucket"))

    @builtins.property
    @jsii.member(jsii_name="schedulerLogsLevel")
    def scheduler_logs_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schedulerLogsLevel"))

    @builtins.property
    @jsii.member(jsii_name="taskLogsLevel")
    def task_logs_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskLogsLevel"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="webserverLogsLevel")
    def webserver_logs_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webserverLogsLevel"))

    @builtins.property
    @jsii.member(jsii_name="workerLogsLevel")
    def worker_logs_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workerLogsLevel"))

    @builtins.property
    @jsii.member(jsii_name="pluginFile")
    def plugin_file(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_deployment_ceddda9d.BucketDeployment]:
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_deployment_ceddda9d.BucketDeployment], jsii.get(self, "pluginFile"))


@jsii.data_type(
    jsii_type="aws-ddk-core.MWAAEnvironmentProps",
    jsii_struct_bases=[_aws_cdk_aws_mwaa_ceddda9d.CfnEnvironmentProps],
    name_mapping={
        "name": "name",
        "airflow_configuration_options": "airflowConfigurationOptions",
        "airflow_version": "airflowVersion",
        "dag_s3_path": "dagS3Path",
        "endpoint_management": "endpointManagement",
        "environment_class": "environmentClass",
        "execution_role_arn": "executionRoleArn",
        "kms_key": "kmsKey",
        "logging_configuration": "loggingConfiguration",
        "max_webservers": "maxWebservers",
        "max_workers": "maxWorkers",
        "min_webservers": "minWebservers",
        "min_workers": "minWorkers",
        "network_configuration": "networkConfiguration",
        "plugins_s3_object_version": "pluginsS3ObjectVersion",
        "plugins_s3_path": "pluginsS3Path",
        "requirements_s3_object_version": "requirementsS3ObjectVersion",
        "requirements_s3_path": "requirementsS3Path",
        "schedulers": "schedulers",
        "source_bucket_arn": "sourceBucketArn",
        "startup_script_s3_object_version": "startupScriptS3ObjectVersion",
        "startup_script_s3_path": "startupScriptS3Path",
        "tags": "tags",
        "webserver_access_mode": "webserverAccessMode",
        "weekly_maintenance_window_start": "weeklyMaintenanceWindowStart",
        "additional_policy_statements": "additionalPolicyStatements",
        "dag_files": "dagFiles",
        "dag_processing_logs": "dagProcessingLogs",
        "plugin_file": "pluginFile",
        "requirements_file": "requirementsFile",
        "s3_bucket": "s3Bucket",
        "scheduler_logs_level": "schedulerLogsLevel",
        "task_logs_level": "taskLogsLevel",
        "vpc_cidr": "vpcCidr",
        "vpc_id": "vpcId",
        "webserver_logs_level": "webserverLogsLevel",
        "worker_logs_level": "workerLogsLevel",
    },
)
class MWAAEnvironmentProps(_aws_cdk_aws_mwaa_ceddda9d.CfnEnvironmentProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        airflow_configuration_options: typing.Any = None,
        airflow_version: typing.Optional[builtins.str] = None,
        dag_s3_path: typing.Optional[builtins.str] = None,
        endpoint_management: typing.Optional[builtins.str] = None,
        environment_class: typing.Optional[builtins.str] = None,
        execution_role_arn: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        logging_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment.LoggingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        max_webservers: typing.Optional[jsii.Number] = None,
        max_workers: typing.Optional[jsii.Number] = None,
        min_webservers: typing.Optional[jsii.Number] = None,
        min_workers: typing.Optional[jsii.Number] = None,
        network_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        plugins_s3_object_version: typing.Optional[builtins.str] = None,
        plugins_s3_path: typing.Optional[builtins.str] = None,
        requirements_s3_object_version: typing.Optional[builtins.str] = None,
        requirements_s3_path: typing.Optional[builtins.str] = None,
        schedulers: typing.Optional[jsii.Number] = None,
        source_bucket_arn: typing.Optional[builtins.str] = None,
        startup_script_s3_object_version: typing.Optional[builtins.str] = None,
        startup_script_s3_path: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
        webserver_access_mode: typing.Optional[builtins.str] = None,
        weekly_maintenance_window_start: typing.Optional[builtins.str] = None,
        additional_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        dag_files: typing.Optional[typing.Sequence[builtins.str]] = None,
        dag_processing_logs: typing.Optional[builtins.str] = None,
        plugin_file: typing.Optional[builtins.str] = None,
        requirements_file: typing.Optional[builtins.str] = None,
        s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        scheduler_logs_level: typing.Optional[builtins.str] = None,
        task_logs_level: typing.Optional[builtins.str] = None,
        vpc_cidr: typing.Optional[builtins.str] = None,
        vpc_id: typing.Optional[builtins.str] = None,
        webserver_logs_level: typing.Optional[builtins.str] = None,
        worker_logs_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: The name of your Amazon MWAA environment.
        :param airflow_configuration_options: A list of key-value pairs containing the Airflow configuration options for your environment. For example, ``core.default_timezone: utc`` . To learn more, see `Apache Airflow configuration options <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-env-variables.html>`_ .
        :param airflow_version: The version of Apache Airflow to use for the environment. If no value is specified, defaults to the latest version. If you specify a newer version number for an existing environment, the version update requires some service interruption before taking effect. *Allowed Values* : ``1.10.12`` | ``2.0.2`` | ``2.2.2`` | ``2.4.3`` | ``2.5.1`` | ``2.6.3`` | ``2.7.2`` | ``2.8.1`` | ``2.9.2`` (latest)
        :param dag_s3_path: The relative path to the DAGs folder on your Amazon S3 bucket. For example, ``dags`` . To learn more, see `Adding or updating DAGs <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-dag-folder.html>`_ .
        :param endpoint_management: Defines whether the VPC endpoints configured for the environment are created, and managed, by the customer or by Amazon MWAA. If set to ``SERVICE`` , Amazon MWAA will create and manage the required VPC endpoints in your VPC. If set to ``CUSTOMER`` , you must create, and manage, the VPC endpoints in your VPC.
        :param environment_class: The environment class type. Valid values: ``mw1.small`` , ``mw1.medium`` , ``mw1.large`` . To learn more, see `Amazon MWAA environment class <https://docs.aws.amazon.com/mwaa/latest/userguide/environment-class.html>`_ .
        :param execution_role_arn: The Amazon Resource Name (ARN) of the execution role in IAM that allows MWAA to access AWS resources in your environment. For example, ``arn:aws:iam::123456789:role/my-execution-role`` . To learn more, see `Amazon MWAA Execution role <https://docs.aws.amazon.com/mwaa/latest/userguide/mwaa-create-role.html>`_ .
        :param kms_key: The AWS Key Management Service (KMS) key to encrypt and decrypt the data in your environment. You can use an AWS KMS key managed by MWAA, or a customer-managed KMS key (advanced).
        :param logging_configuration: The Apache Airflow logs being sent to CloudWatch Logs: ``DagProcessingLogs`` , ``SchedulerLogs`` , ``TaskLogs`` , ``WebserverLogs`` , ``WorkerLogs`` .
        :param max_webservers: The maximum number of web servers that you want to run in your environment. Amazon MWAA scales the number of Apache Airflow web servers up to the number you specify for ``MaxWebservers`` when you interact with your Apache Airflow environment using Apache Airflow REST API, or the Apache Airflow CLI. For example, in scenarios where your workload requires network calls to the Apache Airflow REST API with a high transaction-per-second (TPS) rate, Amazon MWAA will increase the number of web servers up to the number set in ``MaxWebserers`` . As TPS rates decrease Amazon MWAA disposes of the additional web servers, and scales down to the number set in ``MinxWebserers`` . Valid values: For environments larger than mw1.micro, accepts values from ``2`` to ``5`` . Defaults to ``2`` for all environment sizes except mw1.micro, which defaults to ``1`` .
        :param max_workers: The maximum number of workers that you want to run in your environment. MWAA scales the number of Apache Airflow workers up to the number you specify in the ``MaxWorkers`` field. For example, ``20`` . When there are no more tasks running, and no more in the queue, MWAA disposes of the extra workers leaving the one worker that is included with your environment, or the number you specify in ``MinWorkers`` .
        :param min_webservers: The minimum number of web servers that you want to run in your environment. Amazon MWAA scales the number of Apache Airflow web servers up to the number you specify for ``MaxWebservers`` when you interact with your Apache Airflow environment using Apache Airflow REST API, or the Apache Airflow CLI. As the transaction-per-second rate, and the network load, decrease, Amazon MWAA disposes of the additional web servers, and scales down to the number set in ``MinxWebserers`` . Valid values: For environments larger than mw1.micro, accepts values from ``2`` to ``5`` . Defaults to ``2`` for all environment sizes except mw1.micro, which defaults to ``1`` .
        :param min_workers: The minimum number of workers that you want to run in your environment. MWAA scales the number of Apache Airflow workers up to the number you specify in the ``MaxWorkers`` field. When there are no more tasks running, and no more in the queue, MWAA disposes of the extra workers leaving the worker count you specify in the ``MinWorkers`` field. For example, ``2`` .
        :param network_configuration: The VPC networking components used to secure and enable network traffic between the AWS resources for your environment. To learn more, see `About networking on Amazon MWAA <https://docs.aws.amazon.com/mwaa/latest/userguide/networking-about.html>`_ .
        :param plugins_s3_object_version: The version of the plugins.zip file on your Amazon S3 bucket. To learn more, see `Installing custom plugins <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-dag-import-plugins.html>`_ .
        :param plugins_s3_path: The relative path to the ``plugins.zip`` file on your Amazon S3 bucket. For example, ``plugins.zip`` . To learn more, see `Installing custom plugins <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-dag-import-plugins.html>`_ .
        :param requirements_s3_object_version: The version of the requirements.txt file on your Amazon S3 bucket. To learn more, see `Installing Python dependencies <https://docs.aws.amazon.com/mwaa/latest/userguide/working-dags-dependencies.html>`_ .
        :param requirements_s3_path: The relative path to the ``requirements.txt`` file on your Amazon S3 bucket. For example, ``requirements.txt`` . To learn more, see `Installing Python dependencies <https://docs.aws.amazon.com/mwaa/latest/userguide/working-dags-dependencies.html>`_ .
        :param schedulers: The number of schedulers that you want to run in your environment. Valid values:. - *v2* - Accepts between 2 to 5. Defaults to 2. - *v1* - Accepts 1.
        :param source_bucket_arn: The Amazon Resource Name (ARN) of the Amazon S3 bucket where your DAG code and supporting files are stored. For example, ``arn:aws:s3:::my-airflow-bucket-unique-name`` . To learn more, see `Create an Amazon S3 bucket for Amazon MWAA <https://docs.aws.amazon.com/mwaa/latest/userguide/mwaa-s3-bucket.html>`_ .
        :param startup_script_s3_object_version: The version of the startup shell script in your Amazon S3 bucket. You must specify the `version ID <https://docs.aws.amazon.com/AmazonS3/latest/userguide/versioning-workflows.html>`_ that Amazon S3 assigns to the file every time you update the script. Version IDs are Unicode, UTF-8 encoded, URL-ready, opaque strings that are no more than 1,024 bytes long. The following is an example: ``3sL4kqtJlcpXroDTDmJ+rmSpXd3dIbrHY+MTRCxf3vjVBH40Nr8X8gdRQBpUMLUo`` For more information, see `Using a startup script <https://docs.aws.amazon.com/mwaa/latest/userguide/using-startup-script.html>`_ .
        :param startup_script_s3_path: The relative path to the startup shell script in your Amazon S3 bucket. For example, ``s3://mwaa-environment/startup.sh`` . Amazon MWAA runs the script as your environment starts, and before running the Apache Airflow process. You can use this script to install dependencies, modify Apache Airflow configuration options, and set environment variables. For more information, see `Using a startup script <https://docs.aws.amazon.com/mwaa/latest/userguide/using-startup-script.html>`_ .
        :param tags: The key-value tag pairs associated to your environment. For example, ``"Environment": "Staging"`` . To learn more, see `Tagging <https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html>`_ . If you specify new tags for an existing environment, the update requires service interruption before taking effect.
        :param webserver_access_mode: The Apache Airflow *Web server* access mode. To learn more, see `Apache Airflow access modes <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-networking.html>`_ . Valid values: ``PRIVATE_ONLY`` or ``PUBLIC_ONLY`` .
        :param weekly_maintenance_window_start: The day and time of the week to start weekly maintenance updates of your environment in the following format: ``DAY:HH:MM`` . For example: ``TUE:03:30`` . You can specify a start time in 30 minute increments only. Supported input includes the following: - MON|TUE|WED|THU|FRI|SAT|SUN:([01]\\d|2[0-3]):(00|30)
        :param additional_policy_statements: Additional policy statements to add to the airflow execution role.
        :param dag_files: File(s) to be uploaded to dags location in s3 bucket.
        :param dag_processing_logs: Log level for DagProcessing.
        :param plugin_file: Plugin file to be uploaded to plugin path in S3. 'pluginsS3Path' must be specified as well.
        :param requirements_file: Requirements file to be uploaded to plugin path in S3. 'requirementsS3Path' must be specified as well.
        :param s3_bucket: S3 Bucket.
        :param scheduler_logs_level: Log level for SchedulerLogs.
        :param task_logs_level: Log level for TaskLogs.
        :param vpc_cidr: The IP range (CIDR notation) for this VPC.
        :param vpc_id: Existing vpc id.
        :param webserver_logs_level: Log level for WebserverLogs.
        :param worker_logs_level: Log level for WorkerLogs.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8947f25c6bd15e846e7d13e9c335c4e41f800116e21ba100b25118382fcd659c)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument airflow_configuration_options", value=airflow_configuration_options, expected_type=type_hints["airflow_configuration_options"])
            check_type(argname="argument airflow_version", value=airflow_version, expected_type=type_hints["airflow_version"])
            check_type(argname="argument dag_s3_path", value=dag_s3_path, expected_type=type_hints["dag_s3_path"])
            check_type(argname="argument endpoint_management", value=endpoint_management, expected_type=type_hints["endpoint_management"])
            check_type(argname="argument environment_class", value=environment_class, expected_type=type_hints["environment_class"])
            check_type(argname="argument execution_role_arn", value=execution_role_arn, expected_type=type_hints["execution_role_arn"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument logging_configuration", value=logging_configuration, expected_type=type_hints["logging_configuration"])
            check_type(argname="argument max_webservers", value=max_webservers, expected_type=type_hints["max_webservers"])
            check_type(argname="argument max_workers", value=max_workers, expected_type=type_hints["max_workers"])
            check_type(argname="argument min_webservers", value=min_webservers, expected_type=type_hints["min_webservers"])
            check_type(argname="argument min_workers", value=min_workers, expected_type=type_hints["min_workers"])
            check_type(argname="argument network_configuration", value=network_configuration, expected_type=type_hints["network_configuration"])
            check_type(argname="argument plugins_s3_object_version", value=plugins_s3_object_version, expected_type=type_hints["plugins_s3_object_version"])
            check_type(argname="argument plugins_s3_path", value=plugins_s3_path, expected_type=type_hints["plugins_s3_path"])
            check_type(argname="argument requirements_s3_object_version", value=requirements_s3_object_version, expected_type=type_hints["requirements_s3_object_version"])
            check_type(argname="argument requirements_s3_path", value=requirements_s3_path, expected_type=type_hints["requirements_s3_path"])
            check_type(argname="argument schedulers", value=schedulers, expected_type=type_hints["schedulers"])
            check_type(argname="argument source_bucket_arn", value=source_bucket_arn, expected_type=type_hints["source_bucket_arn"])
            check_type(argname="argument startup_script_s3_object_version", value=startup_script_s3_object_version, expected_type=type_hints["startup_script_s3_object_version"])
            check_type(argname="argument startup_script_s3_path", value=startup_script_s3_path, expected_type=type_hints["startup_script_s3_path"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument webserver_access_mode", value=webserver_access_mode, expected_type=type_hints["webserver_access_mode"])
            check_type(argname="argument weekly_maintenance_window_start", value=weekly_maintenance_window_start, expected_type=type_hints["weekly_maintenance_window_start"])
            check_type(argname="argument additional_policy_statements", value=additional_policy_statements, expected_type=type_hints["additional_policy_statements"])
            check_type(argname="argument dag_files", value=dag_files, expected_type=type_hints["dag_files"])
            check_type(argname="argument dag_processing_logs", value=dag_processing_logs, expected_type=type_hints["dag_processing_logs"])
            check_type(argname="argument plugin_file", value=plugin_file, expected_type=type_hints["plugin_file"])
            check_type(argname="argument requirements_file", value=requirements_file, expected_type=type_hints["requirements_file"])
            check_type(argname="argument s3_bucket", value=s3_bucket, expected_type=type_hints["s3_bucket"])
            check_type(argname="argument scheduler_logs_level", value=scheduler_logs_level, expected_type=type_hints["scheduler_logs_level"])
            check_type(argname="argument task_logs_level", value=task_logs_level, expected_type=type_hints["task_logs_level"])
            check_type(argname="argument vpc_cidr", value=vpc_cidr, expected_type=type_hints["vpc_cidr"])
            check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
            check_type(argname="argument webserver_logs_level", value=webserver_logs_level, expected_type=type_hints["webserver_logs_level"])
            check_type(argname="argument worker_logs_level", value=worker_logs_level, expected_type=type_hints["worker_logs_level"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if airflow_configuration_options is not None:
            self._values["airflow_configuration_options"] = airflow_configuration_options
        if airflow_version is not None:
            self._values["airflow_version"] = airflow_version
        if dag_s3_path is not None:
            self._values["dag_s3_path"] = dag_s3_path
        if endpoint_management is not None:
            self._values["endpoint_management"] = endpoint_management
        if environment_class is not None:
            self._values["environment_class"] = environment_class
        if execution_role_arn is not None:
            self._values["execution_role_arn"] = execution_role_arn
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if logging_configuration is not None:
            self._values["logging_configuration"] = logging_configuration
        if max_webservers is not None:
            self._values["max_webservers"] = max_webservers
        if max_workers is not None:
            self._values["max_workers"] = max_workers
        if min_webservers is not None:
            self._values["min_webservers"] = min_webservers
        if min_workers is not None:
            self._values["min_workers"] = min_workers
        if network_configuration is not None:
            self._values["network_configuration"] = network_configuration
        if plugins_s3_object_version is not None:
            self._values["plugins_s3_object_version"] = plugins_s3_object_version
        if plugins_s3_path is not None:
            self._values["plugins_s3_path"] = plugins_s3_path
        if requirements_s3_object_version is not None:
            self._values["requirements_s3_object_version"] = requirements_s3_object_version
        if requirements_s3_path is not None:
            self._values["requirements_s3_path"] = requirements_s3_path
        if schedulers is not None:
            self._values["schedulers"] = schedulers
        if source_bucket_arn is not None:
            self._values["source_bucket_arn"] = source_bucket_arn
        if startup_script_s3_object_version is not None:
            self._values["startup_script_s3_object_version"] = startup_script_s3_object_version
        if startup_script_s3_path is not None:
            self._values["startup_script_s3_path"] = startup_script_s3_path
        if tags is not None:
            self._values["tags"] = tags
        if webserver_access_mode is not None:
            self._values["webserver_access_mode"] = webserver_access_mode
        if weekly_maintenance_window_start is not None:
            self._values["weekly_maintenance_window_start"] = weekly_maintenance_window_start
        if additional_policy_statements is not None:
            self._values["additional_policy_statements"] = additional_policy_statements
        if dag_files is not None:
            self._values["dag_files"] = dag_files
        if dag_processing_logs is not None:
            self._values["dag_processing_logs"] = dag_processing_logs
        if plugin_file is not None:
            self._values["plugin_file"] = plugin_file
        if requirements_file is not None:
            self._values["requirements_file"] = requirements_file
        if s3_bucket is not None:
            self._values["s3_bucket"] = s3_bucket
        if scheduler_logs_level is not None:
            self._values["scheduler_logs_level"] = scheduler_logs_level
        if task_logs_level is not None:
            self._values["task_logs_level"] = task_logs_level
        if vpc_cidr is not None:
            self._values["vpc_cidr"] = vpc_cidr
        if vpc_id is not None:
            self._values["vpc_id"] = vpc_id
        if webserver_logs_level is not None:
            self._values["webserver_logs_level"] = webserver_logs_level
        if worker_logs_level is not None:
            self._values["worker_logs_level"] = worker_logs_level

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of your Amazon MWAA environment.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def airflow_configuration_options(self) -> typing.Any:
        '''A list of key-value pairs containing the Airflow configuration options for your environment.

        For example, ``core.default_timezone: utc`` . To learn more, see `Apache Airflow configuration options <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-env-variables.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-airflowconfigurationoptions
        '''
        result = self._values.get("airflow_configuration_options")
        return typing.cast(typing.Any, result)

    @builtins.property
    def airflow_version(self) -> typing.Optional[builtins.str]:
        '''The version of Apache Airflow to use for the environment.

        If no value is specified, defaults to the latest version.

        If you specify a newer version number for an existing environment, the version update requires some service interruption before taking effect.

        *Allowed Values* : ``1.10.12`` | ``2.0.2`` | ``2.2.2`` | ``2.4.3`` | ``2.5.1`` | ``2.6.3`` | ``2.7.2`` | ``2.8.1`` | ``2.9.2`` (latest)

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-airflowversion
        '''
        result = self._values.get("airflow_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dag_s3_path(self) -> typing.Optional[builtins.str]:
        '''The relative path to the DAGs folder on your Amazon S3 bucket.

        For example, ``dags`` . To learn more, see `Adding or updating DAGs <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-dag-folder.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-dags3path
        '''
        result = self._values.get("dag_s3_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint_management(self) -> typing.Optional[builtins.str]:
        '''Defines whether the VPC endpoints configured for the environment are created, and managed, by the customer or by Amazon MWAA.

        If set to ``SERVICE`` , Amazon MWAA will create and manage the required VPC endpoints in your VPC. If set to ``CUSTOMER`` , you must create, and manage, the VPC endpoints in your VPC.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-endpointmanagement
        '''
        result = self._values.get("endpoint_management")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_class(self) -> typing.Optional[builtins.str]:
        '''The environment class type.

        Valid values: ``mw1.small`` , ``mw1.medium`` , ``mw1.large`` . To learn more, see `Amazon MWAA environment class <https://docs.aws.amazon.com/mwaa/latest/userguide/environment-class.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-environmentclass
        '''
        result = self._values.get("environment_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def execution_role_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of the execution role in IAM that allows MWAA to access AWS resources in your environment.

        For example, ``arn:aws:iam::123456789:role/my-execution-role`` . To learn more, see `Amazon MWAA Execution role <https://docs.aws.amazon.com/mwaa/latest/userguide/mwaa-create-role.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-executionrolearn
        '''
        result = self._values.get("execution_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[builtins.str]:
        '''The AWS Key Management Service (KMS) key to encrypt and decrypt the data in your environment.

        You can use an AWS KMS key managed by MWAA, or a customer-managed KMS key (advanced).

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-kmskey
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment.LoggingConfigurationProperty]]:
        '''The Apache Airflow logs being sent to CloudWatch Logs: ``DagProcessingLogs`` , ``SchedulerLogs`` , ``TaskLogs`` , ``WebserverLogs`` , ``WorkerLogs`` .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-loggingconfiguration
        '''
        result = self._values.get("logging_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment.LoggingConfigurationProperty]], result)

    @builtins.property
    def max_webservers(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of web servers that you want to run in your environment.

        Amazon MWAA scales the number of Apache Airflow web servers up to the number you specify for ``MaxWebservers`` when you interact with your Apache Airflow environment using Apache Airflow REST API, or the Apache Airflow CLI. For example, in scenarios where your workload requires network calls to the Apache Airflow REST API with a high transaction-per-second (TPS) rate, Amazon MWAA will increase the number of web servers up to the number set in ``MaxWebserers`` . As TPS rates decrease Amazon MWAA disposes of the additional web servers, and scales down to the number set in ``MinxWebserers`` .

        Valid values: For environments larger than mw1.micro, accepts values from ``2`` to ``5`` . Defaults to ``2`` for all environment sizes except mw1.micro, which defaults to ``1`` .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-maxwebservers
        '''
        result = self._values.get("max_webservers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_workers(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of workers that you want to run in your environment.

        MWAA scales the number of Apache Airflow workers up to the number you specify in the ``MaxWorkers`` field. For example, ``20`` . When there are no more tasks running, and no more in the queue, MWAA disposes of the extra workers leaving the one worker that is included with your environment, or the number you specify in ``MinWorkers`` .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-maxworkers
        '''
        result = self._values.get("max_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_webservers(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of web servers that you want to run in your environment.

        Amazon MWAA scales the number of Apache Airflow web servers up to the number you specify for ``MaxWebservers`` when you interact with your Apache Airflow environment using Apache Airflow REST API, or the Apache Airflow CLI. As the transaction-per-second rate, and the network load, decrease, Amazon MWAA disposes of the additional web servers, and scales down to the number set in ``MinxWebserers`` .

        Valid values: For environments larger than mw1.micro, accepts values from ``2`` to ``5`` . Defaults to ``2`` for all environment sizes except mw1.micro, which defaults to ``1`` .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-minwebservers
        '''
        result = self._values.get("min_webservers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_workers(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of workers that you want to run in your environment.

        MWAA scales the number of Apache Airflow workers up to the number you specify in the ``MaxWorkers`` field. When there are no more tasks running, and no more in the queue, MWAA disposes of the extra workers leaving the worker count you specify in the ``MinWorkers`` field. For example, ``2`` .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-minworkers
        '''
        result = self._values.get("min_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def network_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment.NetworkConfigurationProperty]]:
        '''The VPC networking components used to secure and enable network traffic between the AWS resources for your environment.

        To learn more, see `About networking on Amazon MWAA <https://docs.aws.amazon.com/mwaa/latest/userguide/networking-about.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-networkconfiguration
        '''
        result = self._values.get("network_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment.NetworkConfigurationProperty]], result)

    @builtins.property
    def plugins_s3_object_version(self) -> typing.Optional[builtins.str]:
        '''The version of the plugins.zip file on your Amazon S3 bucket. To learn more, see `Installing custom plugins <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-dag-import-plugins.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-pluginss3objectversion
        '''
        result = self._values.get("plugins_s3_object_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def plugins_s3_path(self) -> typing.Optional[builtins.str]:
        '''The relative path to the ``plugins.zip`` file on your Amazon S3 bucket. For example, ``plugins.zip`` . To learn more, see `Installing custom plugins <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-dag-import-plugins.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-pluginss3path
        '''
        result = self._values.get("plugins_s3_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def requirements_s3_object_version(self) -> typing.Optional[builtins.str]:
        '''The version of the requirements.txt file on your Amazon S3 bucket. To learn more, see `Installing Python dependencies <https://docs.aws.amazon.com/mwaa/latest/userguide/working-dags-dependencies.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-requirementss3objectversion
        '''
        result = self._values.get("requirements_s3_object_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def requirements_s3_path(self) -> typing.Optional[builtins.str]:
        '''The relative path to the ``requirements.txt`` file on your Amazon S3 bucket. For example, ``requirements.txt`` . To learn more, see `Installing Python dependencies <https://docs.aws.amazon.com/mwaa/latest/userguide/working-dags-dependencies.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-requirementss3path
        '''
        result = self._values.get("requirements_s3_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schedulers(self) -> typing.Optional[jsii.Number]:
        '''The number of schedulers that you want to run in your environment. Valid values:.

        - *v2* - Accepts between 2 to 5. Defaults to 2.
        - *v1* - Accepts 1.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-schedulers
        '''
        result = self._values.get("schedulers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def source_bucket_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of the Amazon S3 bucket where your DAG code and supporting files are stored.

        For example, ``arn:aws:s3:::my-airflow-bucket-unique-name`` . To learn more, see `Create an Amazon S3 bucket for Amazon MWAA <https://docs.aws.amazon.com/mwaa/latest/userguide/mwaa-s3-bucket.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-sourcebucketarn
        '''
        result = self._values.get("source_bucket_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def startup_script_s3_object_version(self) -> typing.Optional[builtins.str]:
        '''The version of the startup shell script in your Amazon S3 bucket.

        You must specify the `version ID <https://docs.aws.amazon.com/AmazonS3/latest/userguide/versioning-workflows.html>`_ that Amazon S3 assigns to the file every time you update the script.

        Version IDs are Unicode, UTF-8 encoded, URL-ready, opaque strings that are no more than 1,024 bytes long. The following is an example:

        ``3sL4kqtJlcpXroDTDmJ+rmSpXd3dIbrHY+MTRCxf3vjVBH40Nr8X8gdRQBpUMLUo``

        For more information, see `Using a startup script <https://docs.aws.amazon.com/mwaa/latest/userguide/using-startup-script.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-startupscripts3objectversion
        '''
        result = self._values.get("startup_script_s3_object_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def startup_script_s3_path(self) -> typing.Optional[builtins.str]:
        '''The relative path to the startup shell script in your Amazon S3 bucket. For example, ``s3://mwaa-environment/startup.sh`` .

        Amazon MWAA runs the script as your environment starts, and before running the Apache Airflow process. You can use this script to install dependencies, modify Apache Airflow configuration options, and set environment variables. For more information, see `Using a startup script <https://docs.aws.amazon.com/mwaa/latest/userguide/using-startup-script.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-startupscripts3path
        '''
        result = self._values.get("startup_script_s3_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''The key-value tag pairs associated to your environment. For example, ``"Environment": "Staging"`` . To learn more, see `Tagging <https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html>`_ .

        If you specify new tags for an existing environment, the update requires service interruption before taking effect.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    @builtins.property
    def webserver_access_mode(self) -> typing.Optional[builtins.str]:
        '''The Apache Airflow *Web server* access mode.

        To learn more, see `Apache Airflow access modes <https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-networking.html>`_ . Valid values: ``PRIVATE_ONLY`` or ``PUBLIC_ONLY`` .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-webserveraccessmode
        '''
        result = self._values.get("webserver_access_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def weekly_maintenance_window_start(self) -> typing.Optional[builtins.str]:
        '''The day and time of the week to start weekly maintenance updates of your environment in the following format: ``DAY:HH:MM`` .

        For example: ``TUE:03:30`` . You can specify a start time in 30 minute increments only. Supported input includes the following:

        - MON|TUE|WED|THU|FRI|SAT|SUN:([01]\\d|2[0-3]):(00|30)

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mwaa-environment.html#cfn-mwaa-environment-weeklymaintenancewindowstart
        '''
        result = self._values.get("weekly_maintenance_window_start")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Additional policy statements to add to the airflow execution role.'''
        result = self._values.get("additional_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def dag_files(self) -> typing.Optional[typing.List[builtins.str]]:
        '''File(s) to be uploaded to dags location in s3 bucket.'''
        result = self._values.get("dag_files")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dag_processing_logs(self) -> typing.Optional[builtins.str]:
        '''Log level for DagProcessing.'''
        result = self._values.get("dag_processing_logs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def plugin_file(self) -> typing.Optional[builtins.str]:
        '''Plugin file to be uploaded to plugin path in S3.

        'pluginsS3Path' must be specified as well.
        '''
        result = self._values.get("plugin_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def requirements_file(self) -> typing.Optional[builtins.str]:
        '''Requirements file to be uploaded to plugin path in S3.

        'requirementsS3Path' must be specified as well.
        '''
        result = self._values.get("requirements_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''S3 Bucket.'''
        result = self._values.get("s3_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def scheduler_logs_level(self) -> typing.Optional[builtins.str]:
        '''Log level for SchedulerLogs.'''
        result = self._values.get("scheduler_logs_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task_logs_level(self) -> typing.Optional[builtins.str]:
        '''Log level for TaskLogs.'''
        result = self._values.get("task_logs_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_cidr(self) -> typing.Optional[builtins.str]:
        '''The IP range (CIDR notation) for this VPC.'''
        result = self._values.get("vpc_cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_id(self) -> typing.Optional[builtins.str]:
        '''Existing vpc id.'''
        result = self._values.get("vpc_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def webserver_logs_level(self) -> typing.Optional[builtins.str]:
        '''Log level for WebserverLogs.'''
        result = self._values.get("webserver_logs_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def worker_logs_level(self) -> typing.Optional[builtins.str]:
        '''Log level for WorkerLogs.'''
        result = self._values.get("worker_logs_level")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MWAAEnvironmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.MWAALambdasResult",
    jsii_struct_bases=[],
    name_mapping={"status_lambda": "statusLambda", "trigger_lambda": "triggerLambda"},
)
class MWAALambdasResult:
    def __init__(
        self,
        *,
        status_lambda: _aws_cdk_aws_lambda_ceddda9d.Function,
        trigger_lambda: _aws_cdk_aws_lambda_ceddda9d.Function,
    ) -> None:
        '''
        :param status_lambda: 
        :param trigger_lambda: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a03e72d8a80ef31dd9345bbdbea98b4abaf3d0a8612fd59523bd5d47407ab0c)
            check_type(argname="argument status_lambda", value=status_lambda, expected_type=type_hints["status_lambda"])
            check_type(argname="argument trigger_lambda", value=trigger_lambda, expected_type=type_hints["trigger_lambda"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status_lambda": status_lambda,
            "trigger_lambda": trigger_lambda,
        }

    @builtins.property
    def status_lambda(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        result = self._values.get("status_lambda")
        assert result is not None, "Required property 'status_lambda' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, result)

    @builtins.property
    def trigger_lambda(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        result = self._values.get("trigger_lambda")
        assert result is not None, "Required property 'trigger_lambda' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MWAALambdasResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.PermissionsBoundaryProps",
    jsii_struct_bases=[],
    name_mapping={
        "environment_id": "environmentId",
        "prefix": "prefix",
        "qualifier": "qualifier",
    },
)
class PermissionsBoundaryProps:
    def __init__(
        self,
        *,
        environment_id: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        qualifier: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param environment_id: 
        :param prefix: 
        :param qualifier: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efd5392745ac5f11de7c7110e4c4c8cc4060becd6944d345396c27f2c82152b4)
            check_type(argname="argument environment_id", value=environment_id, expected_type=type_hints["environment_id"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument qualifier", value=qualifier, expected_type=type_hints["qualifier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if environment_id is not None:
            self._values["environment_id"] = environment_id
        if prefix is not None:
            self._values["prefix"] = prefix
        if qualifier is not None:
            self._values["qualifier"] = qualifier

    @builtins.property
    def environment_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("environment_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def qualifier(self) -> typing.Optional[builtins.str]:
        result = self._values.get("qualifier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PermissionsBoundaryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3Factory(metaclass=jsii.JSIIMeta, jsii_type="aws-ddk-core.S3Factory"):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="bucket")
    @builtins.classmethod
    def bucket(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        access_control: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl] = None,
        auto_delete_objects: typing.Optional[builtins.bool] = None,
        block_public_access: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess] = None,
        bucket_key_enabled: typing.Optional[builtins.bool] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.CorsRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        encryption: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        enforce_ssl: typing.Optional[builtins.bool] = None,
        event_bridge_enabled: typing.Optional[builtins.bool] = None,
        intelligent_tiering_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        inventories: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.Inventory, typing.Dict[builtins.str, typing.Any]]]] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        metrics: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketMetrics, typing.Dict[builtins.str, typing.Any]]]] = None,
        minimum_tls_version: typing.Optional[jsii.Number] = None,
        notifications_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        notifications_skip_destination_validation: typing.Optional[builtins.bool] = None,
        object_lock_default_retention: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention] = None,
        object_lock_enabled: typing.Optional[builtins.bool] = None,
        object_ownership: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership] = None,
        public_read_access: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replication_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.ReplicationRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        server_access_logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        server_access_logs_prefix: typing.Optional[builtins.str] = None,
        target_object_key_format: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat] = None,
        transfer_acceleration: typing.Optional[builtins.bool] = None,
        transition_default_minimum_object_size: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize] = None,
        versioned: typing.Optional[builtins.bool] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
        website_redirect: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.RedirectTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        website_routing_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.RoutingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''
        :param scope: -
        :param id: -
        :param access_control: Specifies a canned ACL that grants predefined permissions to the bucket. Default: BucketAccessControl.PRIVATE
        :param auto_delete_objects: Whether all objects should be automatically deleted when the bucket is removed from the stack or when the stack is deleted. Requires the ``removalPolicy`` to be set to ``RemovalPolicy.DESTROY``. **Warning** if you have deployed a bucket with ``autoDeleteObjects: true``, switching this to ``false`` in a CDK version *before* ``1.126.0`` will lead to all objects in the bucket being deleted. Be sure to update your bucket resources by deploying with CDK version ``1.126.0`` or later **before** switching this value to ``false``. Setting ``autoDeleteObjects`` to true on a bucket will add ``s3:PutBucketPolicy`` to the bucket policy. This is because during bucket deletion, the custom resource provider needs to update the bucket policy by adding a deny policy for ``s3:PutObject`` to prevent race conditions with external bucket writers. Default: false
        :param block_public_access: The block public access configuration of this bucket. Default: - CloudFormation defaults will apply. New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access
        :param bucket_key_enabled: Whether Amazon S3 should use its own intermediary key to generate data keys. Only relevant when using KMS for encryption. - If not enabled, every object GET and PUT will cause an API call to KMS (with the attendant cost implications of that). - If enabled, S3 will use its own time-limited key instead. Only relevant, when Encryption is not set to ``BucketEncryption.UNENCRYPTED``. Default: - false
        :param bucket_name: Physical name of this bucket. Default: - Assigned by CloudFormation (recommended).
        :param cors: The CORS configuration of this bucket. Default: - No CORS configuration.
        :param encryption: The kind of server-side encryption to apply to this bucket. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - ``KMS`` if ``encryptionKey`` is specified, or ``UNENCRYPTED`` otherwise. But if ``UNENCRYPTED`` is specified, the bucket will be encrypted as ``S3_MANAGED`` automatically.
        :param encryption_key: External KMS key to use for bucket encryption. The ``encryption`` property must be either not specified or set to ``KMS`` or ``DSSE``. An error will be emitted if ``encryption`` is set to ``UNENCRYPTED`` or ``S3_MANAGED``. Default: - If ``encryption`` is set to ``KMS`` and this property is undefined, a new KMS key will be created and associated with this bucket.
        :param enforce_ssl: Enforces SSL for requests. S3.5 of the AWS Foundational Security Best Practices Regarding S3. Default: false
        :param event_bridge_enabled: Whether this bucket should send notifications to Amazon EventBridge or not. Default: false
        :param intelligent_tiering_configurations: Intelligent Tiering Configurations. Default: No Intelligent Tiiering Configurations.
        :param inventories: The inventory configuration of the bucket. Default: - No inventory configuration
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime. Default: - No lifecycle rules.
        :param metrics: The metrics configuration of this bucket. Default: - No metrics configuration.
        :param minimum_tls_version: Enforces minimum TLS version for requests. Requires ``enforceSSL`` to be enabled. Default: No minimum TLS version is enforced.
        :param notifications_handler_role: The role to be used by the notifications handler. Default: - a new role will be created.
        :param notifications_skip_destination_validation: Skips notification validation of Amazon SQS, Amazon SNS, and Lambda destinations. Default: false
        :param object_lock_default_retention: The default retention mode and rules for S3 Object Lock. Default retention can be configured after a bucket is created if the bucket already has object lock enabled. Enabling object lock for existing buckets is not supported. Default: no default retention period
        :param object_lock_enabled: Enable object lock on the bucket. Enabling object lock for existing buckets is not supported. Object lock must be enabled when the bucket is created. Default: false, unless objectLockDefaultRetention is set (then, true)
        :param object_ownership: The objectOwnership of the bucket. Default: - No ObjectOwnership configuration. By default, Amazon S3 sets Object Ownership to ``Bucket owner enforced``. This means ACLs are disabled and the bucket owner will own every object.
        :param public_read_access: Grants public read access to all objects in the bucket. Similar to calling ``bucket.grantPublicAccess()`` Default: false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param replication_rules: A container for one or more replication rules. Default: - No replication
        :param server_access_logs_bucket: Destination bucket for the server access logs. Default: - If "serverAccessLogsPrefix" undefined - access logs disabled, otherwise - log to current bucket.
        :param server_access_logs_prefix: Optional log file prefix to use for the bucket's access logs. If defined without "serverAccessLogsBucket", enables access logs to current bucket with this prefix. Default: - No log file prefix
        :param target_object_key_format: Optional key format for log objects. Default: - the default key format is: [DestinationPrefix][YYYY]-[MM]-[DD]-[hh]-[mm]-[ss]-[UniqueString]
        :param transfer_acceleration: Whether this bucket should have transfer acceleration turned on or not. Default: false
        :param transition_default_minimum_object_size: Indicates which default minimum object size behavior is applied to the lifecycle configuration. To customize the minimum object size for any transition you can add a filter that specifies a custom ``objectSizeGreaterThan`` or ``objectSizeLessThan`` for ``lifecycleRules`` property. Custom filters always take precedence over the default transition behavior. Default: - TransitionDefaultMinimumObjectSize.VARIES_BY_STORAGE_CLASS before September 2024, otherwise TransitionDefaultMinimumObjectSize.ALL_STORAGE_CLASSES_128_K.
        :param versioned: Whether this bucket should have versioning turned on or not. Default: false (unless object lock is enabled, then true)
        :param website_error_document: The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set. Default: - No error document.
        :param website_index_document: The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket. Default: - No index document.
        :param website_redirect: Specifies the redirect behavior of all requests to a website endpoint of a bucket. If you specify this property, you can't specify "websiteIndexDocument", "websiteErrorDocument" nor , "websiteRoutingRules". Default: - No redirection.
        :param website_routing_rules: Rules that define when a redirect is applied and the redirect behavior. Default: - No redirection rules.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__302aa44a04efd7039f32314924ad83f7735955102f1c3d6163fb082aae834c76)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_s3_ceddda9d.BucketProps(
            access_control=access_control,
            auto_delete_objects=auto_delete_objects,
            block_public_access=block_public_access,
            bucket_key_enabled=bucket_key_enabled,
            bucket_name=bucket_name,
            cors=cors,
            encryption=encryption,
            encryption_key=encryption_key,
            enforce_ssl=enforce_ssl,
            event_bridge_enabled=event_bridge_enabled,
            intelligent_tiering_configurations=intelligent_tiering_configurations,
            inventories=inventories,
            lifecycle_rules=lifecycle_rules,
            metrics=metrics,
            minimum_tls_version=minimum_tls_version,
            notifications_handler_role=notifications_handler_role,
            notifications_skip_destination_validation=notifications_skip_destination_validation,
            object_lock_default_retention=object_lock_default_retention,
            object_lock_enabled=object_lock_enabled,
            object_ownership=object_ownership,
            public_read_access=public_read_access,
            removal_policy=removal_policy,
            replication_rules=replication_rules,
            server_access_logs_bucket=server_access_logs_bucket,
            server_access_logs_prefix=server_access_logs_prefix,
            target_object_key_format=target_object_key_format,
            transfer_acceleration=transfer_acceleration,
            transition_default_minimum_object_size=transition_default_minimum_object_size,
            versioned=versioned,
            website_error_document=website_error_document,
            website_index_document=website_index_document,
            website_redirect=website_redirect,
            website_routing_rules=website_routing_rules,
        )

        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.sinvoke(cls, "bucket", [scope, id, props]))


class SnsFactory(metaclass=jsii.JSIIMeta, jsii_type="aws-ddk-core.SnsFactory"):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="secureSnsTopicPolicy")
    @builtins.classmethod
    def secure_sns_topic_policy(cls, topic: _aws_cdk_aws_sns_ceddda9d.ITopic) -> None:
        '''
        :param topic: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__576a40c037c0f9a1e8953e9d1b17a1026f7d596ac5fc54fc43e0d213874fae25)
            check_type(argname="argument topic", value=topic, expected_type=type_hints["topic"])
        return typing.cast(None, jsii.sinvoke(cls, "secureSnsTopicPolicy", [topic]))


@jsii.data_type(
    jsii_type="aws-ddk-core.SourceActionProps",
    jsii_struct_bases=[],
    name_mapping={
        "repository_name": "repositoryName",
        "branch": "branch",
        "source_action": "sourceAction",
    },
)
class SourceActionProps:
    def __init__(
        self,
        *,
        repository_name: builtins.str,
        branch: typing.Optional[builtins.str] = None,
        source_action: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource] = None,
    ) -> None:
        '''Properties for the source action.

        :param repository_name: Name of the SCM repository.
        :param branch: Branch of the SCM repository.
        :param source_action: Override source action.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c722ae4d9bf55cce29be798641c0fc2edce1bd6666919da164ce1643888b11e)
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
            check_type(argname="argument source_action", value=source_action, expected_type=type_hints["source_action"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "repository_name": repository_name,
        }
        if branch is not None:
            self._values["branch"] = branch
        if source_action is not None:
            self._values["source_action"] = source_action

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''Name of the SCM repository.'''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch(self) -> typing.Optional[builtins.str]:
        '''Branch of the SCM repository.'''
        result = self._values.get("branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_action(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource]:
        '''Override source action.'''
        result = self._values.get("source_action")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SourceActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.SqsToLambdaStageFunctionProps",
    jsii_struct_bases=[_aws_cdk_aws_lambda_ceddda9d.FunctionProps],
    name_mapping={
        "max_event_age": "maxEventAge",
        "on_failure": "onFailure",
        "on_success": "onSuccess",
        "retry_attempts": "retryAttempts",
        "adot_instrumentation": "adotInstrumentation",
        "allow_all_ipv6_outbound": "allowAllIpv6Outbound",
        "allow_all_outbound": "allowAllOutbound",
        "allow_public_subnet": "allowPublicSubnet",
        "application_log_level": "applicationLogLevel",
        "application_log_level_v2": "applicationLogLevelV2",
        "architecture": "architecture",
        "code_signing_config": "codeSigningConfig",
        "current_version_options": "currentVersionOptions",
        "dead_letter_queue": "deadLetterQueue",
        "dead_letter_queue_enabled": "deadLetterQueueEnabled",
        "dead_letter_topic": "deadLetterTopic",
        "description": "description",
        "environment": "environment",
        "environment_encryption": "environmentEncryption",
        "ephemeral_storage_size": "ephemeralStorageSize",
        "events": "events",
        "filesystem": "filesystem",
        "function_name": "functionName",
        "initial_policy": "initialPolicy",
        "insights_version": "insightsVersion",
        "ipv6_allowed_for_dual_stack": "ipv6AllowedForDualStack",
        "layers": "layers",
        "log_format": "logFormat",
        "logging_format": "loggingFormat",
        "log_group": "logGroup",
        "log_retention": "logRetention",
        "log_retention_retry_options": "logRetentionRetryOptions",
        "log_retention_role": "logRetentionRole",
        "memory_size": "memorySize",
        "params_and_secrets": "paramsAndSecrets",
        "profiling": "profiling",
        "profiling_group": "profilingGroup",
        "recursive_loop": "recursiveLoop",
        "reserved_concurrent_executions": "reservedConcurrentExecutions",
        "role": "role",
        "runtime_management_mode": "runtimeManagementMode",
        "security_groups": "securityGroups",
        "snap_start": "snapStart",
        "system_log_level": "systemLogLevel",
        "system_log_level_v2": "systemLogLevelV2",
        "timeout": "timeout",
        "tracing": "tracing",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "code": "code",
        "handler": "handler",
        "runtime": "runtime",
        "errors_alarm_threshold": "errorsAlarmThreshold",
        "errors_comparison_operator": "errorsComparisonOperator",
        "errors_evaluation_periods": "errorsEvaluationPeriods",
    },
)
class SqsToLambdaStageFunctionProps(_aws_cdk_aws_lambda_ceddda9d.FunctionProps):
    def __init__(
        self,
        *,
        max_event_age: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        on_failure: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination] = None,
        on_success: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
        adot_instrumentation: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.AdotInstrumentationConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        allow_public_subnet: typing.Optional[builtins.bool] = None,
        application_log_level: typing.Optional[builtins.str] = None,
        application_log_level_v2: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ApplicationLogLevel] = None,
        architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
        code_signing_config: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ICodeSigningConfig] = None,
        current_version_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.VersionOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
        dead_letter_queue_enabled: typing.Optional[builtins.bool] = None,
        dead_letter_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        ephemeral_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        events: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.IEventSource]] = None,
        filesystem: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FileSystem] = None,
        function_name: typing.Optional[builtins.str] = None,
        initial_policy: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        insights_version: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LambdaInsightsVersion] = None,
        ipv6_allowed_for_dual_stack: typing.Optional[builtins.bool] = None,
        layers: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]] = None,
        log_format: typing.Optional[builtins.str] = None,
        logging_format: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LoggingFormat] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        log_retention_retry_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.LogRetentionRetryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        log_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        params_and_secrets: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ParamsAndSecretsLayerVersion] = None,
        profiling: typing.Optional[builtins.bool] = None,
        profiling_group: typing.Optional[_aws_cdk_aws_codeguruprofiler_ceddda9d.IProfilingGroup] = None,
        recursive_loop: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RecursiveLoop] = None,
        reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        runtime_management_mode: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RuntimeManagementMode] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        snap_start: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SnapStartConf] = None,
        system_log_level: typing.Optional[builtins.str] = None,
        system_log_level_v2: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SystemLogLevel] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        tracing: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Tracing] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        code: _aws_cdk_aws_lambda_ceddda9d.Code,
        handler: builtins.str,
        runtime: _aws_cdk_aws_lambda_ceddda9d.Runtime,
        errors_alarm_threshold: typing.Optional[jsii.Number] = None,
        errors_comparison_operator: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator] = None,
        errors_evaluation_periods: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Properties for the Lambda Function created by ``SqsToLambdaStage``.

        :param max_event_age: The maximum age of a request that Lambda sends to a function for processing. Minimum: 60 seconds Maximum: 6 hours Default: Duration.hours(6)
        :param on_failure: The destination for failed invocations. Default: - no destination
        :param on_success: The destination for successful invocations. Default: - no destination
        :param retry_attempts: The maximum number of times to retry when the function returns an error. Minimum: 0 Maximum: 2 Default: 2
        :param adot_instrumentation: Specify the configuration of AWS Distro for OpenTelemetry (ADOT) instrumentation. Default: - No ADOT instrumentation
        :param allow_all_ipv6_outbound: Whether to allow the Lambda to send all ipv6 network traffic. If set to true, there will only be a single egress rule which allows all outbound ipv6 traffic. If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets using ipv6. Do not specify this property if the ``securityGroups`` or ``securityGroup`` property is set. Instead, configure ``allowAllIpv6Outbound`` directly on the security group. Default: false
        :param allow_all_outbound: Whether to allow the Lambda to send all network traffic (except ipv6). If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets. Do not specify this property if the ``securityGroups`` or ``securityGroup`` property is set. Instead, configure ``allowAllOutbound`` directly on the security group. Default: true
        :param allow_public_subnet: Lambda Functions in a public subnet can NOT access the internet. Use this property to acknowledge this limitation and still place the function in a public subnet. Default: false
        :param application_log_level: (deprecated) Sets the application log level for the function. Default: "INFO"
        :param application_log_level_v2: Sets the application log level for the function. Default: ApplicationLogLevel.INFO
        :param architecture: The system architectures compatible with this lambda function. Default: Architecture.X86_64
        :param code_signing_config: Code signing config associated with this function. Default: - Not Sign the Code
        :param current_version_options: Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method. Default: - default options as described in ``VersionOptions``
        :param dead_letter_queue: The SQS queue to use if DLQ is enabled. If SNS topic is desired, specify ``deadLetterTopic`` property instead. Default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        :param dead_letter_queue_enabled: Enabled DLQ. If ``deadLetterQueue`` is undefined, an SQS queue with default options will be defined for your Function. Default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        :param dead_letter_topic: The SNS topic to use as a DLQ. Note that if ``deadLetterQueueEnabled`` is set to ``true``, an SQS queue will be created rather than an SNS topic. Using an SNS topic as a DLQ requires this property to be set explicitly. Default: - no SNS topic
        :param description: A description of the function. Default: - No description.
        :param environment: Key-value pairs that Lambda caches and makes available for your Lambda functions. Use environment variables to apply configuration changes, such as test and production environment configurations, without changing your Lambda function source code. Default: - No environment variables.
        :param environment_encryption: The AWS KMS key that's used to encrypt your function's environment variables. Default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        :param ephemeral_storage_size: The size of the function’s /tmp directory in MiB. Default: 512 MiB
        :param events: Event sources for this function. You can also add event sources using ``addEventSource``. Default: - No event sources.
        :param filesystem: The filesystem configuration for the lambda function. Default: - will not mount any filesystem
        :param function_name: A name for the function. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the function's name. For more information, see Name Type.
        :param initial_policy: Initial policy statements to add to the created Lambda Role. You can call ``addToRolePolicy`` to the created lambda to add statements post creation. Default: - No policy statements are added to the created Lambda role.
        :param insights_version: Specify the version of CloudWatch Lambda insights to use for monitoring. Default: - No Lambda Insights
        :param ipv6_allowed_for_dual_stack: Allows outbound IPv6 traffic on VPC functions that are connected to dual-stack subnets. Only used if 'vpc' is supplied. Default: false
        :param layers: A list of layers to add to the function's execution environment. You can configure your Lambda function to pull in additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies that can be used by multiple functions. Default: - No layers.
        :param log_format: (deprecated) Sets the logFormat for the function. Default: "Text"
        :param logging_format: Sets the loggingFormat for the function. Default: LoggingFormat.TEXT
        :param log_group: The log group the function sends logs to. By default, Lambda functions send logs to an automatically created default log group named /aws/lambda/<function name>. However you cannot change the properties of this auto-created log group using the AWS CDK, e.g. you cannot set a different log retention. Use the ``logGroup`` property to create a fully customizable LogGroup ahead of time, and instruct the Lambda function to send logs to it. Providing a user-controlled log group was rolled out to commercial regions on 2023-11-16. If you are deploying to another type of region, please check regional availability first. Default: ``/aws/lambda/${this.functionName}`` - default log group created by Lambda
        :param log_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. This is a legacy API and we strongly recommend you move away from it if you can. Instead create a fully customizable log group with ``logs.LogGroup`` and use the ``logGroup`` property to instruct the Lambda function to send logs to it. Migrating from ``logRetention`` to ``logGroup`` will cause the name of the log group to change. Users and code and referencing the name verbatim will have to adjust. In AWS CDK code, you can access the log group name directly from the LogGroup construct:: import * as logs from 'aws-cdk-lib/aws-logs'; declare const myLogGroup: logs.LogGroup; myLogGroup.logGroupName; Default: logs.RetentionDays.INFINITE
        :param log_retention_retry_options: When log retention is specified, a custom resource attempts to create the CloudWatch log group. These options control the retry policy when interacting with CloudWatch APIs. This is a legacy API and we strongly recommend you migrate to ``logGroup`` if you can. ``logGroup`` allows you to create a fully customizable log group and instruct the Lambda function to send logs to it. Default: - Default AWS SDK retry options.
        :param log_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. This is a legacy API and we strongly recommend you migrate to ``logGroup`` if you can. ``logGroup`` allows you to create a fully customizable log group and instruct the Lambda function to send logs to it. Default: - A new role is created.
        :param memory_size: The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide. Default: 128
        :param params_and_secrets: Specify the configuration of Parameters and Secrets Extension. Default: - No Parameters and Secrets Extension
        :param profiling: Enable profiling. Default: - No profiling.
        :param profiling_group: Profiling Group. Default: - A new profiling group will be created if ``profiling`` is set.
        :param recursive_loop: Sets the Recursive Loop Protection for Lambda Function. It lets Lambda detect and terminate unintended recursive loops. Default: RecursiveLoop.Terminate
        :param reserved_concurrent_executions: The maximum of concurrent executions you want to reserve for the function. Default: - No specific limit - account limit.
        :param role: Lambda execution role. This is the role that will be assumed by the function upon execution. It controls the permissions that the function will have. The Role must be assumable by the 'lambda.amazonaws.com' service principal. The default Role automatically has permissions granted for Lambda execution. If you provide a Role, you must add the relevant AWS managed policies yourself. The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and "service-role/AWSLambdaVPCAccessExecutionRole". Default: - A unique role will be generated for this lambda function. Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        :param runtime_management_mode: Sets the runtime management configuration for a function's version. Default: Auto
        :param security_groups: The list of security groups to associate with the Lambda's network interfaces. Only used if 'vpc' is supplied. Default: - If the function is placed within a VPC and a security group is not specified, either by this or securityGroup prop, a dedicated security group will be created for this function.
        :param snap_start: Enable SnapStart for Lambda Function. SnapStart is currently supported for Java 11, Java 17, Python 3.12, Python 3.13, and .NET 8 runtime Default: - No snapstart
        :param system_log_level: (deprecated) Sets the system log level for the function. Default: "INFO"
        :param system_log_level_v2: Sets the system log level for the function. Default: SystemLogLevel.INFO
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.seconds(3)
        :param tracing: Enable AWS X-Ray Tracing for Lambda Function. Default: Tracing.Disabled
        :param vpc: VPC network to place Lambda network interfaces. Specify this if the Lambda function needs to access resources in a VPC. This is required when ``vpcSubnets`` is specified. Default: - Function is not placed within a VPC.
        :param vpc_subnets: Where to place the network interfaces within the VPC. This requires ``vpc`` to be specified in order for interfaces to actually be placed in the subnets. If ``vpc`` is not specify, this will raise an error. Note: Internet access for Lambda Functions requires a NAT Gateway, so picking public subnets is not allowed (unless ``allowPublicSubnet`` is set to ``true``). Default: - the Vpc default strategy if not specified
        :param code: The source code of your Lambda function. You can point to a file in an Amazon Simple Storage Service (Amazon S3) bucket or specify your source code as inline text.
        :param handler: The name of the method within your code that Lambda calls to execute your function. The format includes the file name. It can also include namespaces and other qualifiers, depending on the runtime. For more information, see https://docs.aws.amazon.com/lambda/latest/dg/foundation-progmodel.html. Use ``Handler.FROM_IMAGE`` when defining a function from a Docker image. NOTE: If you specify your source code as inline text by specifying the ZipFile property within the Code property, specify index.function_name as the handler.
        :param runtime: The runtime environment for the Lambda function that you are uploading. For valid values, see the Runtime property in the AWS Lambda Developer Guide. Use ``Runtime.FROM_IMAGE`` when defining a function from a Docker image.
        :param errors_alarm_threshold: Amount of errored function invocations before triggering CloudWatch alarm. Default: 5
        :param errors_comparison_operator: Comparison operator for evaluating alarms. Default: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        :param errors_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        '''
        if isinstance(adot_instrumentation, dict):
            adot_instrumentation = _aws_cdk_aws_lambda_ceddda9d.AdotInstrumentationConfig(**adot_instrumentation)
        if isinstance(current_version_options, dict):
            current_version_options = _aws_cdk_aws_lambda_ceddda9d.VersionOptions(**current_version_options)
        if isinstance(log_retention_retry_options, dict):
            log_retention_retry_options = _aws_cdk_aws_lambda_ceddda9d.LogRetentionRetryOptions(**log_retention_retry_options)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd35d3f7ab025a947f003bfa8401771bc19ba3bee2d5d3483d2a11a867543e9b)
            check_type(argname="argument max_event_age", value=max_event_age, expected_type=type_hints["max_event_age"])
            check_type(argname="argument on_failure", value=on_failure, expected_type=type_hints["on_failure"])
            check_type(argname="argument on_success", value=on_success, expected_type=type_hints["on_success"])
            check_type(argname="argument retry_attempts", value=retry_attempts, expected_type=type_hints["retry_attempts"])
            check_type(argname="argument adot_instrumentation", value=adot_instrumentation, expected_type=type_hints["adot_instrumentation"])
            check_type(argname="argument allow_all_ipv6_outbound", value=allow_all_ipv6_outbound, expected_type=type_hints["allow_all_ipv6_outbound"])
            check_type(argname="argument allow_all_outbound", value=allow_all_outbound, expected_type=type_hints["allow_all_outbound"])
            check_type(argname="argument allow_public_subnet", value=allow_public_subnet, expected_type=type_hints["allow_public_subnet"])
            check_type(argname="argument application_log_level", value=application_log_level, expected_type=type_hints["application_log_level"])
            check_type(argname="argument application_log_level_v2", value=application_log_level_v2, expected_type=type_hints["application_log_level_v2"])
            check_type(argname="argument architecture", value=architecture, expected_type=type_hints["architecture"])
            check_type(argname="argument code_signing_config", value=code_signing_config, expected_type=type_hints["code_signing_config"])
            check_type(argname="argument current_version_options", value=current_version_options, expected_type=type_hints["current_version_options"])
            check_type(argname="argument dead_letter_queue", value=dead_letter_queue, expected_type=type_hints["dead_letter_queue"])
            check_type(argname="argument dead_letter_queue_enabled", value=dead_letter_queue_enabled, expected_type=type_hints["dead_letter_queue_enabled"])
            check_type(argname="argument dead_letter_topic", value=dead_letter_topic, expected_type=type_hints["dead_letter_topic"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument environment_encryption", value=environment_encryption, expected_type=type_hints["environment_encryption"])
            check_type(argname="argument ephemeral_storage_size", value=ephemeral_storage_size, expected_type=type_hints["ephemeral_storage_size"])
            check_type(argname="argument events", value=events, expected_type=type_hints["events"])
            check_type(argname="argument filesystem", value=filesystem, expected_type=type_hints["filesystem"])
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument initial_policy", value=initial_policy, expected_type=type_hints["initial_policy"])
            check_type(argname="argument insights_version", value=insights_version, expected_type=type_hints["insights_version"])
            check_type(argname="argument ipv6_allowed_for_dual_stack", value=ipv6_allowed_for_dual_stack, expected_type=type_hints["ipv6_allowed_for_dual_stack"])
            check_type(argname="argument layers", value=layers, expected_type=type_hints["layers"])
            check_type(argname="argument log_format", value=log_format, expected_type=type_hints["log_format"])
            check_type(argname="argument logging_format", value=logging_format, expected_type=type_hints["logging_format"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument log_retention", value=log_retention, expected_type=type_hints["log_retention"])
            check_type(argname="argument log_retention_retry_options", value=log_retention_retry_options, expected_type=type_hints["log_retention_retry_options"])
            check_type(argname="argument log_retention_role", value=log_retention_role, expected_type=type_hints["log_retention_role"])
            check_type(argname="argument memory_size", value=memory_size, expected_type=type_hints["memory_size"])
            check_type(argname="argument params_and_secrets", value=params_and_secrets, expected_type=type_hints["params_and_secrets"])
            check_type(argname="argument profiling", value=profiling, expected_type=type_hints["profiling"])
            check_type(argname="argument profiling_group", value=profiling_group, expected_type=type_hints["profiling_group"])
            check_type(argname="argument recursive_loop", value=recursive_loop, expected_type=type_hints["recursive_loop"])
            check_type(argname="argument reserved_concurrent_executions", value=reserved_concurrent_executions, expected_type=type_hints["reserved_concurrent_executions"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument runtime_management_mode", value=runtime_management_mode, expected_type=type_hints["runtime_management_mode"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument snap_start", value=snap_start, expected_type=type_hints["snap_start"])
            check_type(argname="argument system_log_level", value=system_log_level, expected_type=type_hints["system_log_level"])
            check_type(argname="argument system_log_level_v2", value=system_log_level_v2, expected_type=type_hints["system_log_level_v2"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument tracing", value=tracing, expected_type=type_hints["tracing"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument code", value=code, expected_type=type_hints["code"])
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
            check_type(argname="argument runtime", value=runtime, expected_type=type_hints["runtime"])
            check_type(argname="argument errors_alarm_threshold", value=errors_alarm_threshold, expected_type=type_hints["errors_alarm_threshold"])
            check_type(argname="argument errors_comparison_operator", value=errors_comparison_operator, expected_type=type_hints["errors_comparison_operator"])
            check_type(argname="argument errors_evaluation_periods", value=errors_evaluation_periods, expected_type=type_hints["errors_evaluation_periods"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "code": code,
            "handler": handler,
            "runtime": runtime,
        }
        if max_event_age is not None:
            self._values["max_event_age"] = max_event_age
        if on_failure is not None:
            self._values["on_failure"] = on_failure
        if on_success is not None:
            self._values["on_success"] = on_success
        if retry_attempts is not None:
            self._values["retry_attempts"] = retry_attempts
        if adot_instrumentation is not None:
            self._values["adot_instrumentation"] = adot_instrumentation
        if allow_all_ipv6_outbound is not None:
            self._values["allow_all_ipv6_outbound"] = allow_all_ipv6_outbound
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if allow_public_subnet is not None:
            self._values["allow_public_subnet"] = allow_public_subnet
        if application_log_level is not None:
            self._values["application_log_level"] = application_log_level
        if application_log_level_v2 is not None:
            self._values["application_log_level_v2"] = application_log_level_v2
        if architecture is not None:
            self._values["architecture"] = architecture
        if code_signing_config is not None:
            self._values["code_signing_config"] = code_signing_config
        if current_version_options is not None:
            self._values["current_version_options"] = current_version_options
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if dead_letter_queue_enabled is not None:
            self._values["dead_letter_queue_enabled"] = dead_letter_queue_enabled
        if dead_letter_topic is not None:
            self._values["dead_letter_topic"] = dead_letter_topic
        if description is not None:
            self._values["description"] = description
        if environment is not None:
            self._values["environment"] = environment
        if environment_encryption is not None:
            self._values["environment_encryption"] = environment_encryption
        if ephemeral_storage_size is not None:
            self._values["ephemeral_storage_size"] = ephemeral_storage_size
        if events is not None:
            self._values["events"] = events
        if filesystem is not None:
            self._values["filesystem"] = filesystem
        if function_name is not None:
            self._values["function_name"] = function_name
        if initial_policy is not None:
            self._values["initial_policy"] = initial_policy
        if insights_version is not None:
            self._values["insights_version"] = insights_version
        if ipv6_allowed_for_dual_stack is not None:
            self._values["ipv6_allowed_for_dual_stack"] = ipv6_allowed_for_dual_stack
        if layers is not None:
            self._values["layers"] = layers
        if log_format is not None:
            self._values["log_format"] = log_format
        if logging_format is not None:
            self._values["logging_format"] = logging_format
        if log_group is not None:
            self._values["log_group"] = log_group
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if log_retention_retry_options is not None:
            self._values["log_retention_retry_options"] = log_retention_retry_options
        if log_retention_role is not None:
            self._values["log_retention_role"] = log_retention_role
        if memory_size is not None:
            self._values["memory_size"] = memory_size
        if params_and_secrets is not None:
            self._values["params_and_secrets"] = params_and_secrets
        if profiling is not None:
            self._values["profiling"] = profiling
        if profiling_group is not None:
            self._values["profiling_group"] = profiling_group
        if recursive_loop is not None:
            self._values["recursive_loop"] = recursive_loop
        if reserved_concurrent_executions is not None:
            self._values["reserved_concurrent_executions"] = reserved_concurrent_executions
        if role is not None:
            self._values["role"] = role
        if runtime_management_mode is not None:
            self._values["runtime_management_mode"] = runtime_management_mode
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if snap_start is not None:
            self._values["snap_start"] = snap_start
        if system_log_level is not None:
            self._values["system_log_level"] = system_log_level
        if system_log_level_v2 is not None:
            self._values["system_log_level_v2"] = system_log_level_v2
        if timeout is not None:
            self._values["timeout"] = timeout
        if tracing is not None:
            self._values["tracing"] = tracing
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if errors_alarm_threshold is not None:
            self._values["errors_alarm_threshold"] = errors_alarm_threshold
        if errors_comparison_operator is not None:
            self._values["errors_comparison_operator"] = errors_comparison_operator
        if errors_evaluation_periods is not None:
            self._values["errors_evaluation_periods"] = errors_evaluation_periods

    @builtins.property
    def max_event_age(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The maximum age of a request that Lambda sends to a function for processing.

        Minimum: 60 seconds
        Maximum: 6 hours

        :default: Duration.hours(6)
        '''
        result = self._values.get("max_event_age")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def on_failure(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination]:
        '''The destination for failed invocations.

        :default: - no destination
        '''
        result = self._values.get("on_failure")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination], result)

    @builtins.property
    def on_success(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination]:
        '''The destination for successful invocations.

        :default: - no destination
        '''
        result = self._values.get("on_success")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination], result)

    @builtins.property
    def retry_attempts(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of times to retry when the function returns an error.

        Minimum: 0
        Maximum: 2

        :default: 2
        '''
        result = self._values.get("retry_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def adot_instrumentation(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.AdotInstrumentationConfig]:
        '''Specify the configuration of AWS Distro for OpenTelemetry (ADOT) instrumentation.

        :default: - No ADOT instrumentation

        :see: https://aws-otel.github.io/docs/getting-started/lambda
        '''
        result = self._values.get("adot_instrumentation")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.AdotInstrumentationConfig], result)

    @builtins.property
    def allow_all_ipv6_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow the Lambda to send all ipv6 network traffic.

        If set to true, there will only be a single egress rule which allows all
        outbound ipv6 traffic. If set to false, you must individually add traffic rules to allow the
        Lambda to connect to network targets using ipv6.

        Do not specify this property if the ``securityGroups`` or ``securityGroup`` property is set.
        Instead, configure ``allowAllIpv6Outbound`` directly on the security group.

        :default: false
        '''
        result = self._values.get("allow_all_ipv6_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow the Lambda to send all network traffic (except ipv6).

        If set to false, you must individually add traffic rules to allow the
        Lambda to connect to network targets.

        Do not specify this property if the ``securityGroups`` or ``securityGroup`` property is set.
        Instead, configure ``allowAllOutbound`` directly on the security group.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_public_subnet(self) -> typing.Optional[builtins.bool]:
        '''Lambda Functions in a public subnet can NOT access the internet.

        Use this property to acknowledge this limitation and still place the function in a public subnet.

        :default: false

        :see: https://stackoverflow.com/questions/52992085/why-cant-an-aws-lambda-function-inside-a-public-subnet-in-a-vpc-connect-to-the/52994841#52994841
        '''
        result = self._values.get("allow_public_subnet")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def application_log_level(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Sets the application log level for the function.

        :default: "INFO"

        :deprecated: Use ``applicationLogLevelV2`` as a property instead.

        :stability: deprecated
        '''
        result = self._values.get("application_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application_log_level_v2(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ApplicationLogLevel]:
        '''Sets the application log level for the function.

        :default: ApplicationLogLevel.INFO
        '''
        result = self._values.get("application_log_level_v2")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ApplicationLogLevel], result)

    @builtins.property
    def architecture(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture]:
        '''The system architectures compatible with this lambda function.

        :default: Architecture.X86_64
        '''
        result = self._values.get("architecture")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture], result)

    @builtins.property
    def code_signing_config(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ICodeSigningConfig]:
        '''Code signing config associated with this function.

        :default: - Not Sign the Code
        '''
        result = self._values.get("code_signing_config")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ICodeSigningConfig], result)

    @builtins.property
    def current_version_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.VersionOptions]:
        '''Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method.

        :default: - default options as described in ``VersionOptions``
        '''
        result = self._values.get("current_version_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.VersionOptions], result)

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue]:
        '''The SQS queue to use if DLQ is enabled.

        If SNS topic is desired, specify ``deadLetterTopic`` property instead.

        :default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue], result)

    @builtins.property
    def dead_letter_queue_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enabled DLQ.

        If ``deadLetterQueue`` is undefined,
        an SQS queue with default options will be defined for your Function.

        :default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        '''
        result = self._values.get("dead_letter_queue_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dead_letter_topic(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''The SNS topic to use as a DLQ.

        Note that if ``deadLetterQueueEnabled`` is set to ``true``, an SQS queue will be created
        rather than an SNS topic. Using an SNS topic as a DLQ requires this property to be set explicitly.

        :default: - no SNS topic
        '''
        result = self._values.get("dead_letter_topic")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the function.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Key-value pairs that Lambda caches and makes available for your Lambda functions.

        Use environment variables to apply configuration changes, such
        as test and production environment configurations, without changing your
        Lambda function source code.

        :default: - No environment variables.
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def environment_encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The AWS KMS key that's used to encrypt your function's environment variables.

        :default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        '''
        result = self._values.get("environment_encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def ephemeral_storage_size(self) -> typing.Optional[_aws_cdk_ceddda9d.Size]:
        '''The size of the function’s /tmp directory in MiB.

        :default: 512 MiB
        '''
        result = self._values.get("ephemeral_storage_size")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Size], result)

    @builtins.property
    def events(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.IEventSource]]:
        '''Event sources for this function.

        You can also add event sources using ``addEventSource``.

        :default: - No event sources.
        '''
        result = self._values.get("events")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.IEventSource]], result)

    @builtins.property
    def filesystem(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FileSystem]:
        '''The filesystem configuration for the lambda function.

        :default: - will not mount any filesystem
        '''
        result = self._values.get("filesystem")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FileSystem], result)

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''A name for the function.

        :default:

        - AWS CloudFormation generates a unique physical ID and uses that
        ID for the function's name. For more information, see Name Type.
        '''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def initial_policy(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Initial policy statements to add to the created Lambda Role.

        You can call ``addToRolePolicy`` to the created lambda to add statements post creation.

        :default: - No policy statements are added to the created Lambda role.
        '''
        result = self._values.get("initial_policy")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def insights_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LambdaInsightsVersion]:
        '''Specify the version of CloudWatch Lambda insights to use for monitoring.

        :default: - No Lambda Insights

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Lambda-Insights-Getting-Started-docker.html
        '''
        result = self._values.get("insights_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LambdaInsightsVersion], result)

    @builtins.property
    def ipv6_allowed_for_dual_stack(self) -> typing.Optional[builtins.bool]:
        '''Allows outbound IPv6 traffic on VPC functions that are connected to dual-stack subnets.

        Only used if 'vpc' is supplied.

        :default: false
        '''
        result = self._values.get("ipv6_allowed_for_dual_stack")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def layers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]]:
        '''A list of layers to add to the function's execution environment.

        You can configure your Lambda function to pull in
        additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies
        that can be used by multiple functions.

        :default: - No layers.
        '''
        result = self._values.get("layers")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]], result)

    @builtins.property
    def log_format(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Sets the logFormat for the function.

        :default: "Text"

        :deprecated: Use ``loggingFormat`` as a property instead.

        :stability: deprecated
        '''
        result = self._values.get("log_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging_format(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LoggingFormat]:
        '''Sets the loggingFormat for the function.

        :default: LoggingFormat.TEXT
        '''
        result = self._values.get("logging_format")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LoggingFormat], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The log group the function sends logs to.

        By default, Lambda functions send logs to an automatically created default log group named /aws/lambda/.
        However you cannot change the properties of this auto-created log group using the AWS CDK, e.g. you cannot set a different log retention.

        Use the ``logGroup`` property to create a fully customizable LogGroup ahead of time, and instruct the Lambda function to send logs to it.

        Providing a user-controlled log group was rolled out to commercial regions on 2023-11-16.
        If you are deploying to another type of region, please check regional availability first.

        :default: ``/aws/lambda/${this.functionName}`` - default log group created by Lambda
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def log_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''The number of days log events are kept in CloudWatch Logs.

        When updating
        this property, unsetting it doesn't remove the log retention policy. To
        remove the retention policy, set the value to ``INFINITE``.

        This is a legacy API and we strongly recommend you move away from it if you can.
        Instead create a fully customizable log group with ``logs.LogGroup`` and use the ``logGroup`` property
        to instruct the Lambda function to send logs to it.
        Migrating from ``logRetention`` to ``logGroup`` will cause the name of the log group to change.
        Users and code and referencing the name verbatim will have to adjust.

        In AWS CDK code, you can access the log group name directly from the LogGroup construct::

           import * as logs from 'aws-cdk-lib/aws-logs';

           declare const myLogGroup: logs.LogGroup;
           myLogGroup.logGroupName;

        :default: logs.RetentionDays.INFINITE
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def log_retention_retry_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LogRetentionRetryOptions]:
        '''When log retention is specified, a custom resource attempts to create the CloudWatch log group.

        These options control the retry policy when interacting with CloudWatch APIs.

        This is a legacy API and we strongly recommend you migrate to ``logGroup`` if you can.
        ``logGroup`` allows you to create a fully customizable log group and instruct the Lambda function to send logs to it.

        :default: - Default AWS SDK retry options.
        '''
        result = self._values.get("log_retention_retry_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LogRetentionRetryOptions], result)

    @builtins.property
    def log_retention_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role for the Lambda function associated with the custom resource that sets the retention policy.

        This is a legacy API and we strongly recommend you migrate to ``logGroup`` if you can.
        ``logGroup`` allows you to create a fully customizable log group and instruct the Lambda function to send logs to it.

        :default: - A new role is created.
        '''
        result = self._values.get("log_retention_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def memory_size(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory, in MB, that is allocated to your Lambda function.

        Lambda uses this value to proportionally allocate the amount of CPU
        power. For more information, see Resource Model in the AWS Lambda
        Developer Guide.

        :default: 128
        '''
        result = self._values.get("memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def params_and_secrets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ParamsAndSecretsLayerVersion]:
        '''Specify the configuration of Parameters and Secrets Extension.

        :default: - No Parameters and Secrets Extension

        :see: https://docs.aws.amazon.com/systems-manager/latest/userguide/ps-integration-lambda-extensions.html
        '''
        result = self._values.get("params_and_secrets")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ParamsAndSecretsLayerVersion], result)

    @builtins.property
    def profiling(self) -> typing.Optional[builtins.bool]:
        '''Enable profiling.

        :default: - No profiling.

        :see: https://docs.aws.amazon.com/codeguru/latest/profiler-ug/setting-up-lambda.html
        '''
        result = self._values.get("profiling")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def profiling_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codeguruprofiler_ceddda9d.IProfilingGroup]:
        '''Profiling Group.

        :default: - A new profiling group will be created if ``profiling`` is set.

        :see: https://docs.aws.amazon.com/codeguru/latest/profiler-ug/setting-up-lambda.html
        '''
        result = self._values.get("profiling_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_codeguruprofiler_ceddda9d.IProfilingGroup], result)

    @builtins.property
    def recursive_loop(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RecursiveLoop]:
        '''Sets the Recursive Loop Protection for Lambda Function.

        It lets Lambda detect and terminate unintended recursive loops.

        :default: RecursiveLoop.Terminate
        '''
        result = self._values.get("recursive_loop")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RecursiveLoop], result)

    @builtins.property
    def reserved_concurrent_executions(self) -> typing.Optional[jsii.Number]:
        '''The maximum of concurrent executions you want to reserve for the function.

        :default: - No specific limit - account limit.

        :see: https://docs.aws.amazon.com/lambda/latest/dg/concurrent-executions.html
        '''
        result = self._values.get("reserved_concurrent_executions")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Lambda execution role.

        This is the role that will be assumed by the function upon execution.
        It controls the permissions that the function will have. The Role must
        be assumable by the 'lambda.amazonaws.com' service principal.

        The default Role automatically has permissions granted for Lambda execution. If you
        provide a Role, you must add the relevant AWS managed policies yourself.

        The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and
        "service-role/AWSLambdaVPCAccessExecutionRole".

        :default:

        - A unique role will be generated for this lambda function.
        Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def runtime_management_mode(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RuntimeManagementMode]:
        '''Sets the runtime management configuration for a function's version.

        :default: Auto
        '''
        result = self._values.get("runtime_management_mode")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RuntimeManagementMode], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The list of security groups to associate with the Lambda's network interfaces.

        Only used if 'vpc' is supplied.

        :default:

        - If the function is placed within a VPC and a security group is
        not specified, either by this or securityGroup prop, a dedicated security
        group will be created for this function.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def snap_start(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SnapStartConf]:
        '''Enable SnapStart for Lambda Function.

        SnapStart is currently supported for Java 11, Java 17, Python 3.12, Python 3.13, and .NET 8 runtime

        :default: - No snapstart
        '''
        result = self._values.get("snap_start")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SnapStartConf], result)

    @builtins.property
    def system_log_level(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Sets the system log level for the function.

        :default: "INFO"

        :deprecated: Use ``systemLogLevelV2`` as a property instead.

        :stability: deprecated
        '''
        result = self._values.get("system_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def system_log_level_v2(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SystemLogLevel]:
        '''Sets the system log level for the function.

        :default: SystemLogLevel.INFO
        '''
        result = self._values.get("system_log_level_v2")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SystemLogLevel], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The function execution time (in seconds) after which Lambda terminates the function.

        Because the execution time affects cost, set this value
        based on the function's expected execution time.

        :default: Duration.seconds(3)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def tracing(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Tracing]:
        '''Enable AWS X-Ray Tracing for Lambda Function.

        :default: Tracing.Disabled
        '''
        result = self._values.get("tracing")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Tracing], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''VPC network to place Lambda network interfaces.

        Specify this if the Lambda function needs to access resources in a VPC.
        This is required when ``vpcSubnets`` is specified.

        :default: - Function is not placed within a VPC.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place the network interfaces within the VPC.

        This requires ``vpc`` to be specified in order for interfaces to actually be
        placed in the subnets. If ``vpc`` is not specify, this will raise an error.

        Note: Internet access for Lambda Functions requires a NAT Gateway, so picking
        public subnets is not allowed (unless ``allowPublicSubnet`` is set to ``true``).

        :default: - the Vpc default strategy if not specified
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def code(self) -> _aws_cdk_aws_lambda_ceddda9d.Code:
        '''The source code of your Lambda function.

        You can point to a file in an
        Amazon Simple Storage Service (Amazon S3) bucket or specify your source
        code as inline text.
        '''
        result = self._values.get("code")
        assert result is not None, "Required property 'code' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Code, result)

    @builtins.property
    def handler(self) -> builtins.str:
        '''The name of the method within your code that Lambda calls to execute your function.

        The format includes the file name. It can also include
        namespaces and other qualifiers, depending on the runtime.
        For more information, see https://docs.aws.amazon.com/lambda/latest/dg/foundation-progmodel.html.

        Use ``Handler.FROM_IMAGE`` when defining a function from a Docker image.

        NOTE: If you specify your source code as inline text by specifying the
        ZipFile property within the Code property, specify index.function_name as
        the handler.
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def runtime(self) -> _aws_cdk_aws_lambda_ceddda9d.Runtime:
        '''The runtime environment for the Lambda function that you are uploading.

        For valid values, see the Runtime property in the AWS Lambda Developer
        Guide.

        Use ``Runtime.FROM_IMAGE`` when defining a function from a Docker image.
        '''
        result = self._values.get("runtime")
        assert result is not None, "Required property 'runtime' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Runtime, result)

    @builtins.property
    def errors_alarm_threshold(self) -> typing.Optional[jsii.Number]:
        '''Amount of errored function invocations before triggering CloudWatch alarm.

        :default: 5
        '''
        result = self._values.get("errors_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def errors_comparison_operator(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator]:
        '''Comparison operator for evaluating alarms.

        :default: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        '''
        result = self._values.get("errors_comparison_operator")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator], result)

    @builtins.property
    def errors_evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''The number of periods over which data is compared to the specified threshold.

        :default: 1
        '''
        result = self._values.get("errors_evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqsToLambdaStageFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Stage(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="aws-ddk-core.Stage",
):
    '''Abstract class representing a stage.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs the stage.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9cf7c3474ce139a45c8e31d476f0b548b9db19082dbea4dffb9287504da5dff)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StageProps(description=description, name=name)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="eventPattern")
    @abc.abstractmethod
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        '''Output event pattern of the stage.

        Event pattern describes the structure of output event(s) produced by this stage.
        Event Rules use event patterns to select events and route them to targets.
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="targets")
    @abc.abstractmethod
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Input targets for the stage.

        Targets are used by Event Rules to describe what should be invoked when a rule matches an event.
        '''
        ...


class _StageProxy(Stage):
    @builtins.property
    @jsii.member(jsii_name="eventPattern")
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        '''Output event pattern of the stage.

        Event pattern describes the structure of output event(s) produced by this stage.
        Event Rules use event patterns to select events and route them to targets.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern], jsii.get(self, "eventPattern"))

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Input targets for the stage.

        Targets are used by Event Rules to describe what should be invoked when a rule matches an event.
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], jsii.get(self, "targets"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Stage).__jsii_proxy_class__ = lambda : _StageProxy


@jsii.data_type(
    jsii_type="aws-ddk-core.StageProps",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "name": "name"},
)
class StageProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for the base abstract stage.

        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e854dfb73af2b1e5b672ba3ec79ee122851867f8bde404e9918340757b3847c)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.StateMachineStageProps",
    jsii_struct_bases=[StageProps],
    name_mapping={
        "description": "description",
        "name": "name",
        "additional_role_policy_statements": "additionalRolePolicyStatements",
        "alarms_enabled": "alarmsEnabled",
        "definition": "definition",
        "definition_file": "definitionFile",
        "state_machine_failed_executions_alarm_evaluation_periods": "stateMachineFailedExecutionsAlarmEvaluationPeriods",
        "state_machine_failed_executions_alarm_threshold": "stateMachineFailedExecutionsAlarmThreshold",
        "state_machine_input": "stateMachineInput",
        "state_machine_name": "stateMachineName",
    },
)
class StateMachineStageProps(StageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties of a state machine stage.

        :param description: Description of the stage.
        :param name: Name of the stage.
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5069a8477e1d868a51858f29afe4a12917625d0a7370bc4090fd23bf809c081c)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument additional_role_policy_statements", value=additional_role_policy_statements, expected_type=type_hints["additional_role_policy_statements"])
            check_type(argname="argument alarms_enabled", value=alarms_enabled, expected_type=type_hints["alarms_enabled"])
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
            check_type(argname="argument definition_file", value=definition_file, expected_type=type_hints["definition_file"])
            check_type(argname="argument state_machine_failed_executions_alarm_evaluation_periods", value=state_machine_failed_executions_alarm_evaluation_periods, expected_type=type_hints["state_machine_failed_executions_alarm_evaluation_periods"])
            check_type(argname="argument state_machine_failed_executions_alarm_threshold", value=state_machine_failed_executions_alarm_threshold, expected_type=type_hints["state_machine_failed_executions_alarm_threshold"])
            check_type(argname="argument state_machine_input", value=state_machine_input, expected_type=type_hints["state_machine_input"])
            check_type(argname="argument state_machine_name", value=state_machine_name, expected_type=type_hints["state_machine_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if additional_role_policy_statements is not None:
            self._values["additional_role_policy_statements"] = additional_role_policy_statements
        if alarms_enabled is not None:
            self._values["alarms_enabled"] = alarms_enabled
        if definition is not None:
            self._values["definition"] = definition
        if definition_file is not None:
            self._values["definition_file"] = definition_file
        if state_machine_failed_executions_alarm_evaluation_periods is not None:
            self._values["state_machine_failed_executions_alarm_evaluation_periods"] = state_machine_failed_executions_alarm_evaluation_periods
        if state_machine_failed_executions_alarm_threshold is not None:
            self._values["state_machine_failed_executions_alarm_threshold"] = state_machine_failed_executions_alarm_threshold
        if state_machine_input is not None:
            self._values["state_machine_input"] = state_machine_input
        if state_machine_name is not None:
            self._values["state_machine_name"] = state_machine_name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_role_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Additional IAM policy statements to add to the state machine role.'''
        result = self._values.get("additional_role_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def alarms_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable/Disable all alarms in the stage.

        :default: true
        '''
        result = self._values.get("alarms_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def definition(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]]:
        '''Steps for the state machine.

        Can either be provided as 'sfn.IChainable' or a JSON string.
        '''
        result = self._values.get("definition")
        return typing.cast(typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]], result)

    @builtins.property
    def definition_file(self) -> typing.Optional[builtins.str]:
        '''File containing a JSON definition for the state machine.'''
        result = self._values.get("definition_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_machine_failed_executions_alarm_evaluation_periods(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of periods over which data is compared to the specified threshold.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_failed_executions_alarm_threshold(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of failed state machine executions before triggering CW alarm.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Input of the state machine.'''
        result = self._values.get("state_machine_input")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_machine_name(self) -> typing.Optional[builtins.str]:
        '''Name of the state machine.'''
        result = self._values.get("state_machine_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StateMachineStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.SynthActionProps",
    jsii_struct_bases=[],
    name_mapping={
        "additional_install_commands": "additionalInstallCommands",
        "cdk_language_command_line_arguments": "cdkLanguageCommandLineArguments",
        "cdk_version": "cdkVersion",
        "codeartifact_domain": "codeartifactDomain",
        "codeartifact_domain_owner": "codeartifactDomainOwner",
        "codeartifact_repository": "codeartifactRepository",
        "env": "env",
        "role_policy_statements": "rolePolicyStatements",
        "synth_action": "synthAction",
    },
)
class SynthActionProps:
    def __init__(
        self,
        *,
        additional_install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_language_command_line_arguments: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        cdk_version: typing.Optional[builtins.str] = None,
        codeartifact_domain: typing.Optional[builtins.str] = None,
        codeartifact_domain_owner: typing.Optional[builtins.str] = None,
        codeartifact_repository: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        synth_action: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildStep] = None,
    ) -> None:
        '''Properties for the synth action.

        :param additional_install_commands: Additional install commands.
        :param cdk_language_command_line_arguments: Additional command line arguements to append to the install command of the ``cdk_langauge`` that is specified. Default: - No command line arguments are appended
        :param cdk_version: CDK versio to use during the synth action. Default: "latest"
        :param codeartifact_domain: Name of the CodeArtifact domain.
        :param codeartifact_domain_owner: CodeArtifact domain owner account.
        :param codeartifact_repository: Name of the CodeArtifact repository to pull artifacts from.
        :param env: Environment variables to set.
        :param role_policy_statements: Additional policies to add to the synth action role.
        :param synth_action: Override synth action.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05acfa3cda54a17101814d614a246f97dc36de4bf27ef87f72f7aa4824dd7b35)
            check_type(argname="argument additional_install_commands", value=additional_install_commands, expected_type=type_hints["additional_install_commands"])
            check_type(argname="argument cdk_language_command_line_arguments", value=cdk_language_command_line_arguments, expected_type=type_hints["cdk_language_command_line_arguments"])
            check_type(argname="argument cdk_version", value=cdk_version, expected_type=type_hints["cdk_version"])
            check_type(argname="argument codeartifact_domain", value=codeartifact_domain, expected_type=type_hints["codeartifact_domain"])
            check_type(argname="argument codeartifact_domain_owner", value=codeartifact_domain_owner, expected_type=type_hints["codeartifact_domain_owner"])
            check_type(argname="argument codeartifact_repository", value=codeartifact_repository, expected_type=type_hints["codeartifact_repository"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument role_policy_statements", value=role_policy_statements, expected_type=type_hints["role_policy_statements"])
            check_type(argname="argument synth_action", value=synth_action, expected_type=type_hints["synth_action"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if additional_install_commands is not None:
            self._values["additional_install_commands"] = additional_install_commands
        if cdk_language_command_line_arguments is not None:
            self._values["cdk_language_command_line_arguments"] = cdk_language_command_line_arguments
        if cdk_version is not None:
            self._values["cdk_version"] = cdk_version
        if codeartifact_domain is not None:
            self._values["codeartifact_domain"] = codeartifact_domain
        if codeartifact_domain_owner is not None:
            self._values["codeartifact_domain_owner"] = codeartifact_domain_owner
        if codeartifact_repository is not None:
            self._values["codeartifact_repository"] = codeartifact_repository
        if env is not None:
            self._values["env"] = env
        if role_policy_statements is not None:
            self._values["role_policy_statements"] = role_policy_statements
        if synth_action is not None:
            self._values["synth_action"] = synth_action

    @builtins.property
    def additional_install_commands(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional install commands.'''
        result = self._values.get("additional_install_commands")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cdk_language_command_line_arguments(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Additional command line arguements to append to the install command of the ``cdk_langauge`` that is specified.

        :default: - No command line arguments are appended
        '''
        result = self._values.get("cdk_language_command_line_arguments")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def cdk_version(self) -> typing.Optional[builtins.str]:
        '''CDK versio to use during the synth action.

        :default: "latest"
        '''
        result = self._values.get("cdk_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codeartifact_domain(self) -> typing.Optional[builtins.str]:
        '''Name of the CodeArtifact domain.'''
        result = self._values.get("codeartifact_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codeartifact_domain_owner(self) -> typing.Optional[builtins.str]:
        '''CodeArtifact domain owner account.'''
        result = self._values.get("codeartifact_domain_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codeartifact_repository(self) -> typing.Optional[builtins.str]:
        '''Name of the CodeArtifact repository to pull artifacts from.'''
        result = self._values.get("codeartifact_repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Environment variables to set.'''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def role_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Additional policies to add to the synth action role.'''
        result = self._values.get("role_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def synth_action(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildStep]:
        '''Override synth action.'''
        result = self._values.get("synth_action")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildStep], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SynthActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.AppFlowIngestionStageProps",
    jsii_struct_bases=[StateMachineStageProps],
    name_mapping={
        "description": "description",
        "name": "name",
        "additional_role_policy_statements": "additionalRolePolicyStatements",
        "alarms_enabled": "alarmsEnabled",
        "definition": "definition",
        "definition_file": "definitionFile",
        "state_machine_failed_executions_alarm_evaluation_periods": "stateMachineFailedExecutionsAlarmEvaluationPeriods",
        "state_machine_failed_executions_alarm_threshold": "stateMachineFailedExecutionsAlarmThreshold",
        "state_machine_input": "stateMachineInput",
        "state_machine_name": "stateMachineName",
        "destination_flow_config": "destinationFlowConfig",
        "flow_execution_status_check_period": "flowExecutionStatusCheckPeriod",
        "flow_name": "flowName",
        "flow_tasks": "flowTasks",
        "source_flow_config": "sourceFlowConfig",
    },
)
class AppFlowIngestionStageProps(StateMachineStageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        destination_flow_config: typing.Optional[typing.Union[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        flow_execution_status_check_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        flow_name: typing.Optional[builtins.str] = None,
        flow_tasks: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        source_flow_config: typing.Optional[typing.Union[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties of the AppFlow Ingestion stage.

        :param description: Description of the stage.
        :param name: Name of the stage.
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param destination_flow_config: The flow ``appflow.CfnFlow.DestinationFlowConfigProperty`` properties.
        :param flow_execution_status_check_period: Time to wait between flow execution status checks. Default: aws_cdk.Duration.seconds(15)
        :param flow_name: Name of the AppFlow flow to run. If None, an AppFlow flow is created.
        :param flow_tasks: The flow tasks properties.
        :param source_flow_config: The flow ``appflow.CfnFlow.SourceFlowConfigProperty`` properties.
        '''
        if isinstance(destination_flow_config, dict):
            destination_flow_config = _aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty(**destination_flow_config)
        if isinstance(source_flow_config, dict):
            source_flow_config = _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty(**source_flow_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50f57d5c758f4bb8a7385b25c9dd1756786a7af562ac0cf743837ff675065839)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument additional_role_policy_statements", value=additional_role_policy_statements, expected_type=type_hints["additional_role_policy_statements"])
            check_type(argname="argument alarms_enabled", value=alarms_enabled, expected_type=type_hints["alarms_enabled"])
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
            check_type(argname="argument definition_file", value=definition_file, expected_type=type_hints["definition_file"])
            check_type(argname="argument state_machine_failed_executions_alarm_evaluation_periods", value=state_machine_failed_executions_alarm_evaluation_periods, expected_type=type_hints["state_machine_failed_executions_alarm_evaluation_periods"])
            check_type(argname="argument state_machine_failed_executions_alarm_threshold", value=state_machine_failed_executions_alarm_threshold, expected_type=type_hints["state_machine_failed_executions_alarm_threshold"])
            check_type(argname="argument state_machine_input", value=state_machine_input, expected_type=type_hints["state_machine_input"])
            check_type(argname="argument state_machine_name", value=state_machine_name, expected_type=type_hints["state_machine_name"])
            check_type(argname="argument destination_flow_config", value=destination_flow_config, expected_type=type_hints["destination_flow_config"])
            check_type(argname="argument flow_execution_status_check_period", value=flow_execution_status_check_period, expected_type=type_hints["flow_execution_status_check_period"])
            check_type(argname="argument flow_name", value=flow_name, expected_type=type_hints["flow_name"])
            check_type(argname="argument flow_tasks", value=flow_tasks, expected_type=type_hints["flow_tasks"])
            check_type(argname="argument source_flow_config", value=source_flow_config, expected_type=type_hints["source_flow_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if additional_role_policy_statements is not None:
            self._values["additional_role_policy_statements"] = additional_role_policy_statements
        if alarms_enabled is not None:
            self._values["alarms_enabled"] = alarms_enabled
        if definition is not None:
            self._values["definition"] = definition
        if definition_file is not None:
            self._values["definition_file"] = definition_file
        if state_machine_failed_executions_alarm_evaluation_periods is not None:
            self._values["state_machine_failed_executions_alarm_evaluation_periods"] = state_machine_failed_executions_alarm_evaluation_periods
        if state_machine_failed_executions_alarm_threshold is not None:
            self._values["state_machine_failed_executions_alarm_threshold"] = state_machine_failed_executions_alarm_threshold
        if state_machine_input is not None:
            self._values["state_machine_input"] = state_machine_input
        if state_machine_name is not None:
            self._values["state_machine_name"] = state_machine_name
        if destination_flow_config is not None:
            self._values["destination_flow_config"] = destination_flow_config
        if flow_execution_status_check_period is not None:
            self._values["flow_execution_status_check_period"] = flow_execution_status_check_period
        if flow_name is not None:
            self._values["flow_name"] = flow_name
        if flow_tasks is not None:
            self._values["flow_tasks"] = flow_tasks
        if source_flow_config is not None:
            self._values["source_flow_config"] = source_flow_config

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_role_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Additional IAM policy statements to add to the state machine role.'''
        result = self._values.get("additional_role_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def alarms_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable/Disable all alarms in the stage.

        :default: true
        '''
        result = self._values.get("alarms_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def definition(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]]:
        '''Steps for the state machine.

        Can either be provided as 'sfn.IChainable' or a JSON string.
        '''
        result = self._values.get("definition")
        return typing.cast(typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]], result)

    @builtins.property
    def definition_file(self) -> typing.Optional[builtins.str]:
        '''File containing a JSON definition for the state machine.'''
        result = self._values.get("definition_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_machine_failed_executions_alarm_evaluation_periods(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of periods over which data is compared to the specified threshold.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_failed_executions_alarm_threshold(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of failed state machine executions before triggering CW alarm.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Input of the state machine.'''
        result = self._values.get("state_machine_input")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_machine_name(self) -> typing.Optional[builtins.str]:
        '''Name of the state machine.'''
        result = self._values.get("state_machine_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_flow_config(
        self,
    ) -> typing.Optional[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty]:
        '''The flow ``appflow.CfnFlow.DestinationFlowConfigProperty`` properties.'''
        result = self._values.get("destination_flow_config")
        return typing.cast(typing.Optional[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty], result)

    @builtins.property
    def flow_execution_status_check_period(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Time to wait between flow execution status checks.

        :default: aws_cdk.Duration.seconds(15)
        '''
        result = self._values.get("flow_execution_status_check_period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def flow_name(self) -> typing.Optional[builtins.str]:
        '''Name of the AppFlow flow to run.

        If None, an AppFlow flow is created.
        '''
        result = self._values.get("flow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def flow_tasks(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty]]:
        '''The flow tasks properties.'''
        result = self._values.get("flow_tasks")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty]], result)

    @builtins.property
    def source_flow_config(
        self,
    ) -> typing.Optional[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty]:
        '''The flow ``appflow.CfnFlow.SourceFlowConfigProperty`` properties.'''
        result = self._values.get("source_flow_config")
        return typing.cast(typing.Optional[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppFlowIngestionStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.AthenaToSQLStageProps",
    jsii_struct_bases=[StateMachineStageProps],
    name_mapping={
        "description": "description",
        "name": "name",
        "additional_role_policy_statements": "additionalRolePolicyStatements",
        "alarms_enabled": "alarmsEnabled",
        "definition": "definition",
        "definition_file": "definitionFile",
        "state_machine_failed_executions_alarm_evaluation_periods": "stateMachineFailedExecutionsAlarmEvaluationPeriods",
        "state_machine_failed_executions_alarm_threshold": "stateMachineFailedExecutionsAlarmThreshold",
        "state_machine_input": "stateMachineInput",
        "state_machine_name": "stateMachineName",
        "catalog_name": "catalogName",
        "database_name": "databaseName",
        "encryption_key": "encryptionKey",
        "encryption_option": "encryptionOption",
        "output_location": "outputLocation",
        "parallel": "parallel",
        "query_string": "queryString",
        "query_string_path": "queryStringPath",
        "work_group": "workGroup",
    },
)
class AthenaToSQLStageProps(StateMachineStageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        catalog_name: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        encryption_option: typing.Optional[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.EncryptionOption] = None,
        output_location: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.Location, typing.Dict[builtins.str, typing.Any]]] = None,
        parallel: typing.Optional[builtins.bool] = None,
        query_string: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_string_path: typing.Optional[builtins.str] = None,
        work_group: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for ``AthenaSQLStage``.

        :param description: Description of the stage.
        :param name: Name of the stage.
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param catalog_name: Catalog name.
        :param database_name: Database name.
        :param encryption_key: Encryption KMS key.
        :param encryption_option: Encryption configuration.
        :param output_location: Output S3 location.
        :param parallel: flag to determine parallel or sequential execution. Default: false
        :param query_string: SQL queries that will be started.
        :param query_string_path: dynamic path in statemachine for SQL query to be started.
        :param work_group: Athena workgroup name.
        '''
        if isinstance(output_location, dict):
            output_location = _aws_cdk_aws_s3_ceddda9d.Location(**output_location)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d02b2a3868910a4789cbcba2028e07a331d2da507e4b4c951dd7801d735bc0ac)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument additional_role_policy_statements", value=additional_role_policy_statements, expected_type=type_hints["additional_role_policy_statements"])
            check_type(argname="argument alarms_enabled", value=alarms_enabled, expected_type=type_hints["alarms_enabled"])
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
            check_type(argname="argument definition_file", value=definition_file, expected_type=type_hints["definition_file"])
            check_type(argname="argument state_machine_failed_executions_alarm_evaluation_periods", value=state_machine_failed_executions_alarm_evaluation_periods, expected_type=type_hints["state_machine_failed_executions_alarm_evaluation_periods"])
            check_type(argname="argument state_machine_failed_executions_alarm_threshold", value=state_machine_failed_executions_alarm_threshold, expected_type=type_hints["state_machine_failed_executions_alarm_threshold"])
            check_type(argname="argument state_machine_input", value=state_machine_input, expected_type=type_hints["state_machine_input"])
            check_type(argname="argument state_machine_name", value=state_machine_name, expected_type=type_hints["state_machine_name"])
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument encryption_option", value=encryption_option, expected_type=type_hints["encryption_option"])
            check_type(argname="argument output_location", value=output_location, expected_type=type_hints["output_location"])
            check_type(argname="argument parallel", value=parallel, expected_type=type_hints["parallel"])
            check_type(argname="argument query_string", value=query_string, expected_type=type_hints["query_string"])
            check_type(argname="argument query_string_path", value=query_string_path, expected_type=type_hints["query_string_path"])
            check_type(argname="argument work_group", value=work_group, expected_type=type_hints["work_group"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if additional_role_policy_statements is not None:
            self._values["additional_role_policy_statements"] = additional_role_policy_statements
        if alarms_enabled is not None:
            self._values["alarms_enabled"] = alarms_enabled
        if definition is not None:
            self._values["definition"] = definition
        if definition_file is not None:
            self._values["definition_file"] = definition_file
        if state_machine_failed_executions_alarm_evaluation_periods is not None:
            self._values["state_machine_failed_executions_alarm_evaluation_periods"] = state_machine_failed_executions_alarm_evaluation_periods
        if state_machine_failed_executions_alarm_threshold is not None:
            self._values["state_machine_failed_executions_alarm_threshold"] = state_machine_failed_executions_alarm_threshold
        if state_machine_input is not None:
            self._values["state_machine_input"] = state_machine_input
        if state_machine_name is not None:
            self._values["state_machine_name"] = state_machine_name
        if catalog_name is not None:
            self._values["catalog_name"] = catalog_name
        if database_name is not None:
            self._values["database_name"] = database_name
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if encryption_option is not None:
            self._values["encryption_option"] = encryption_option
        if output_location is not None:
            self._values["output_location"] = output_location
        if parallel is not None:
            self._values["parallel"] = parallel
        if query_string is not None:
            self._values["query_string"] = query_string
        if query_string_path is not None:
            self._values["query_string_path"] = query_string_path
        if work_group is not None:
            self._values["work_group"] = work_group

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_role_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Additional IAM policy statements to add to the state machine role.'''
        result = self._values.get("additional_role_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def alarms_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable/Disable all alarms in the stage.

        :default: true
        '''
        result = self._values.get("alarms_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def definition(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]]:
        '''Steps for the state machine.

        Can either be provided as 'sfn.IChainable' or a JSON string.
        '''
        result = self._values.get("definition")
        return typing.cast(typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]], result)

    @builtins.property
    def definition_file(self) -> typing.Optional[builtins.str]:
        '''File containing a JSON definition for the state machine.'''
        result = self._values.get("definition_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_machine_failed_executions_alarm_evaluation_periods(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of periods over which data is compared to the specified threshold.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_failed_executions_alarm_threshold(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of failed state machine executions before triggering CW alarm.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Input of the state machine.'''
        result = self._values.get("state_machine_input")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_machine_name(self) -> typing.Optional[builtins.str]:
        '''Name of the state machine.'''
        result = self._values.get("state_machine_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def catalog_name(self) -> typing.Optional[builtins.str]:
        '''Catalog name.'''
        result = self._values.get("catalog_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''Database name.'''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''Encryption KMS key.'''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def encryption_option(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.EncryptionOption]:
        '''Encryption configuration.'''
        result = self._values.get("encryption_option")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.EncryptionOption], result)

    @builtins.property
    def output_location(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Location]:
        '''Output S3 location.'''
        result = self._values.get("output_location")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Location], result)

    @builtins.property
    def parallel(self) -> typing.Optional[builtins.bool]:
        '''flag to determine parallel or sequential execution.

        :default: false
        '''
        result = self._values.get("parallel")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def query_string(self) -> typing.Optional[typing.List[builtins.str]]:
        '''SQL queries that will be started.'''
        result = self._values.get("query_string")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def query_string_path(self) -> typing.Optional[builtins.str]:
        '''dynamic path in statemachine for SQL query to be started.'''
        result = self._values.get("query_string_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def work_group(self) -> typing.Optional[builtins.str]:
        '''Athena workgroup name.'''
        result = self._values.get("work_group")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaToSQLStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.DataBrewTransformStageProps",
    jsii_struct_bases=[StateMachineStageProps],
    name_mapping={
        "description": "description",
        "name": "name",
        "additional_role_policy_statements": "additionalRolePolicyStatements",
        "alarms_enabled": "alarmsEnabled",
        "definition": "definition",
        "definition_file": "definitionFile",
        "state_machine_failed_executions_alarm_evaluation_periods": "stateMachineFailedExecutionsAlarmEvaluationPeriods",
        "state_machine_failed_executions_alarm_threshold": "stateMachineFailedExecutionsAlarmThreshold",
        "state_machine_input": "stateMachineInput",
        "state_machine_name": "stateMachineName",
        "create_job": "createJob",
        "database_outputs": "databaseOutputs",
        "data_catalog_outputs": "dataCatalogOutputs",
        "dataset_name": "datasetName",
        "encryption_key_arn": "encryptionKeyArn",
        "encryption_mode": "encryptionMode",
        "job_name": "jobName",
        "job_role_arn": "jobRoleArn",
        "job_sample": "jobSample",
        "job_type": "jobType",
        "log_subscription": "logSubscription",
        "max_capacity": "maxCapacity",
        "max_retries": "maxRetries",
        "output_location": "outputLocation",
        "outputs": "outputs",
        "profile_configuration": "profileConfiguration",
        "project_name": "projectName",
        "recipe": "recipe",
        "tags": "tags",
        "timeout": "timeout",
        "validation_configurations": "validationConfigurations",
    },
)
class DataBrewTransformStageProps(StateMachineStageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        create_job: typing.Optional[builtins.bool] = None,
        database_outputs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.DatabaseOutputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        data_catalog_outputs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.DataCatalogOutputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        dataset_name: typing.Optional[builtins.str] = None,
        encryption_key_arn: typing.Optional[builtins.str] = None,
        encryption_mode: typing.Optional[builtins.str] = None,
        job_name: typing.Optional[builtins.str] = None,
        job_role_arn: typing.Optional[builtins.str] = None,
        job_sample: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.JobSampleProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        job_type: typing.Optional[builtins.str] = None,
        log_subscription: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        output_location: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.OutputLocationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        outputs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.OutputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        profile_configuration: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.ProfileConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        project_name: typing.Optional[builtins.str] = None,
        recipe: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.RecipeProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        timeout: typing.Optional[jsii.Number] = None,
        validation_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.ValidationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for ``DataBrewTransformStage``.

        :param description: Description of the stage.
        :param name: Name of the stage.
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param create_job: Whether to create the DataBrew job or not.
        :param database_outputs: Represents a list of JDBC database output objects which defines the output destination for a DataBrew recipe job to write into.
        :param data_catalog_outputs: One or more artifacts that represent the AWS Glue Data Catalog output from running the job.
        :param dataset_name: The name of the dataset to use for the job.
        :param encryption_key_arn: The Amazon Resource Name (ARN) of an encryption key that is used to protect the job output. For more information, see `Encrypting data written by DataBrew jobs <https://docs.aws.amazon.com/databrew/latest/dg/encryption-security-configuration.html>`_
        :param encryption_mode: The encryption mode for the job, which can be one of the following:. - ``SSE-KMS`` - Server-side encryption with keys managed by AWS KMS . - ``SSE-S3`` - Server-side encryption with keys managed by Amazon S3.
        :param job_name: The name of a preexisting DataBrew job to run. If None, a DataBrew job is created.
        :param job_role_arn: The Arn of the job execution role. Required if job_name is None.
        :param job_sample: A sample configuration for profile jobs only, which determines the number of rows on which the profile job is run. If a ``JobSample`` value isn't provided, the default value is used. The default value is CUSTOM_ROWS for the mode parameter and 20,000 for the size parameter.
        :param job_type: The type of job to run. Required if job_name is None.
        :param log_subscription: The current status of Amazon CloudWatch logging for the job.
        :param max_capacity: The maximum number of nodes that can be consumed when the job processes data.
        :param max_retries: The maximum number of times to retry the job after a job run fails.
        :param output_location: ``AWS::DataBrew::Job.OutputLocation``.
        :param outputs: The output properties for the job.
        :param profile_configuration: Configuration for profile jobs. Configuration can be used to select columns, do evaluations, and override default parameters of evaluations. When configuration is undefined, the profile job will apply default settings to all supported columns.
        :param project_name: The name of the project that the job is associated with.
        :param recipe: The recipe to be used by the DataBrew job which is a series of data transformation steps.
        :param tags: Metadata tags that have been applied to the job.
        :param timeout: The job's timeout in minutes. A job that attempts to run longer than this timeout period ends with a status of ``TIMEOUT`` .
        :param validation_configurations: List of validation configurations that are applied to the profile job.
        '''
        if isinstance(job_sample, dict):
            job_sample = _aws_cdk_aws_databrew_ceddda9d.CfnJob.JobSampleProperty(**job_sample)
        if isinstance(output_location, dict):
            output_location = _aws_cdk_aws_databrew_ceddda9d.CfnJob.OutputLocationProperty(**output_location)
        if isinstance(profile_configuration, dict):
            profile_configuration = _aws_cdk_aws_databrew_ceddda9d.CfnJob.ProfileConfigurationProperty(**profile_configuration)
        if isinstance(recipe, dict):
            recipe = _aws_cdk_aws_databrew_ceddda9d.CfnJob.RecipeProperty(**recipe)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6be6b9ec4e805f427307a7bc1c743a3f56ffd52c0cc37a1436d75ce69e31b9f)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument additional_role_policy_statements", value=additional_role_policy_statements, expected_type=type_hints["additional_role_policy_statements"])
            check_type(argname="argument alarms_enabled", value=alarms_enabled, expected_type=type_hints["alarms_enabled"])
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
            check_type(argname="argument definition_file", value=definition_file, expected_type=type_hints["definition_file"])
            check_type(argname="argument state_machine_failed_executions_alarm_evaluation_periods", value=state_machine_failed_executions_alarm_evaluation_periods, expected_type=type_hints["state_machine_failed_executions_alarm_evaluation_periods"])
            check_type(argname="argument state_machine_failed_executions_alarm_threshold", value=state_machine_failed_executions_alarm_threshold, expected_type=type_hints["state_machine_failed_executions_alarm_threshold"])
            check_type(argname="argument state_machine_input", value=state_machine_input, expected_type=type_hints["state_machine_input"])
            check_type(argname="argument state_machine_name", value=state_machine_name, expected_type=type_hints["state_machine_name"])
            check_type(argname="argument create_job", value=create_job, expected_type=type_hints["create_job"])
            check_type(argname="argument database_outputs", value=database_outputs, expected_type=type_hints["database_outputs"])
            check_type(argname="argument data_catalog_outputs", value=data_catalog_outputs, expected_type=type_hints["data_catalog_outputs"])
            check_type(argname="argument dataset_name", value=dataset_name, expected_type=type_hints["dataset_name"])
            check_type(argname="argument encryption_key_arn", value=encryption_key_arn, expected_type=type_hints["encryption_key_arn"])
            check_type(argname="argument encryption_mode", value=encryption_mode, expected_type=type_hints["encryption_mode"])
            check_type(argname="argument job_name", value=job_name, expected_type=type_hints["job_name"])
            check_type(argname="argument job_role_arn", value=job_role_arn, expected_type=type_hints["job_role_arn"])
            check_type(argname="argument job_sample", value=job_sample, expected_type=type_hints["job_sample"])
            check_type(argname="argument job_type", value=job_type, expected_type=type_hints["job_type"])
            check_type(argname="argument log_subscription", value=log_subscription, expected_type=type_hints["log_subscription"])
            check_type(argname="argument max_capacity", value=max_capacity, expected_type=type_hints["max_capacity"])
            check_type(argname="argument max_retries", value=max_retries, expected_type=type_hints["max_retries"])
            check_type(argname="argument output_location", value=output_location, expected_type=type_hints["output_location"])
            check_type(argname="argument outputs", value=outputs, expected_type=type_hints["outputs"])
            check_type(argname="argument profile_configuration", value=profile_configuration, expected_type=type_hints["profile_configuration"])
            check_type(argname="argument project_name", value=project_name, expected_type=type_hints["project_name"])
            check_type(argname="argument recipe", value=recipe, expected_type=type_hints["recipe"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument validation_configurations", value=validation_configurations, expected_type=type_hints["validation_configurations"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if additional_role_policy_statements is not None:
            self._values["additional_role_policy_statements"] = additional_role_policy_statements
        if alarms_enabled is not None:
            self._values["alarms_enabled"] = alarms_enabled
        if definition is not None:
            self._values["definition"] = definition
        if definition_file is not None:
            self._values["definition_file"] = definition_file
        if state_machine_failed_executions_alarm_evaluation_periods is not None:
            self._values["state_machine_failed_executions_alarm_evaluation_periods"] = state_machine_failed_executions_alarm_evaluation_periods
        if state_machine_failed_executions_alarm_threshold is not None:
            self._values["state_machine_failed_executions_alarm_threshold"] = state_machine_failed_executions_alarm_threshold
        if state_machine_input is not None:
            self._values["state_machine_input"] = state_machine_input
        if state_machine_name is not None:
            self._values["state_machine_name"] = state_machine_name
        if create_job is not None:
            self._values["create_job"] = create_job
        if database_outputs is not None:
            self._values["database_outputs"] = database_outputs
        if data_catalog_outputs is not None:
            self._values["data_catalog_outputs"] = data_catalog_outputs
        if dataset_name is not None:
            self._values["dataset_name"] = dataset_name
        if encryption_key_arn is not None:
            self._values["encryption_key_arn"] = encryption_key_arn
        if encryption_mode is not None:
            self._values["encryption_mode"] = encryption_mode
        if job_name is not None:
            self._values["job_name"] = job_name
        if job_role_arn is not None:
            self._values["job_role_arn"] = job_role_arn
        if job_sample is not None:
            self._values["job_sample"] = job_sample
        if job_type is not None:
            self._values["job_type"] = job_type
        if log_subscription is not None:
            self._values["log_subscription"] = log_subscription
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if max_retries is not None:
            self._values["max_retries"] = max_retries
        if output_location is not None:
            self._values["output_location"] = output_location
        if outputs is not None:
            self._values["outputs"] = outputs
        if profile_configuration is not None:
            self._values["profile_configuration"] = profile_configuration
        if project_name is not None:
            self._values["project_name"] = project_name
        if recipe is not None:
            self._values["recipe"] = recipe
        if tags is not None:
            self._values["tags"] = tags
        if timeout is not None:
            self._values["timeout"] = timeout
        if validation_configurations is not None:
            self._values["validation_configurations"] = validation_configurations

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_role_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Additional IAM policy statements to add to the state machine role.'''
        result = self._values.get("additional_role_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def alarms_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable/Disable all alarms in the stage.

        :default: true
        '''
        result = self._values.get("alarms_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def definition(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]]:
        '''Steps for the state machine.

        Can either be provided as 'sfn.IChainable' or a JSON string.
        '''
        result = self._values.get("definition")
        return typing.cast(typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]], result)

    @builtins.property
    def definition_file(self) -> typing.Optional[builtins.str]:
        '''File containing a JSON definition for the state machine.'''
        result = self._values.get("definition_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_machine_failed_executions_alarm_evaluation_periods(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of periods over which data is compared to the specified threshold.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_failed_executions_alarm_threshold(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of failed state machine executions before triggering CW alarm.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Input of the state machine.'''
        result = self._values.get("state_machine_input")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_machine_name(self) -> typing.Optional[builtins.str]:
        '''Name of the state machine.'''
        result = self._values.get("state_machine_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_job(self) -> typing.Optional[builtins.bool]:
        '''Whether to create the DataBrew job or not.'''
        result = self._values.get("create_job")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def database_outputs(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_databrew_ceddda9d.CfnJob.DatabaseOutputProperty]]:
        '''Represents a list of JDBC database output objects which defines the output destination for a DataBrew recipe job to write into.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-databaseoutputs
        '''
        result = self._values.get("database_outputs")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_databrew_ceddda9d.CfnJob.DatabaseOutputProperty]], result)

    @builtins.property
    def data_catalog_outputs(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_databrew_ceddda9d.CfnJob.DataCatalogOutputProperty]]:
        '''One or more artifacts that represent the AWS Glue Data Catalog output from running the job.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-datacatalogoutputs
        '''
        result = self._values.get("data_catalog_outputs")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_databrew_ceddda9d.CfnJob.DataCatalogOutputProperty]], result)

    @builtins.property
    def dataset_name(self) -> typing.Optional[builtins.str]:
        '''The name of the dataset to use for the job.'''
        result = self._values.get("dataset_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of an encryption key that is used to protect the job output.

        For more information, see `Encrypting data written by DataBrew jobs <https://docs.aws.amazon.com/databrew/latest/dg/encryption-security-configuration.html>`_

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-encryptionkeyarn
        '''
        result = self._values.get("encryption_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_mode(self) -> typing.Optional[builtins.str]:
        '''The encryption mode for the job, which can be one of the following:.

        - ``SSE-KMS`` - Server-side encryption with keys managed by AWS KMS .
        - ``SSE-S3`` - Server-side encryption with keys managed by Amazon S3.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-encryptionmode
        '''
        result = self._values.get("encryption_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_name(self) -> typing.Optional[builtins.str]:
        '''The name of a preexisting DataBrew job to run.

        If None, a DataBrew job is created.
        '''
        result = self._values.get("job_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_role_arn(self) -> typing.Optional[builtins.str]:
        '''The Arn of the job execution role.

        Required if job_name is None.
        '''
        result = self._values.get("job_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_sample(
        self,
    ) -> typing.Optional[_aws_cdk_aws_databrew_ceddda9d.CfnJob.JobSampleProperty]:
        '''A sample configuration for profile jobs only, which determines the number of rows on which the profile job is run.

        If a ``JobSample`` value isn't provided, the default value is used. The default value is CUSTOM_ROWS for the mode parameter and 20,000 for the size parameter.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-jobsample
        '''
        result = self._values.get("job_sample")
        return typing.cast(typing.Optional[_aws_cdk_aws_databrew_ceddda9d.CfnJob.JobSampleProperty], result)

    @builtins.property
    def job_type(self) -> typing.Optional[builtins.str]:
        '''The type of job to run.

        Required if job_name is None.
        '''
        result = self._values.get("job_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_subscription(self) -> typing.Optional[builtins.str]:
        '''The current status of Amazon CloudWatch logging for the job.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-logsubscription
        '''
        result = self._values.get("log_subscription")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of nodes that can be consumed when the job processes data.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-maxcapacity
        '''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_retries(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of times to retry the job after a job run fails.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-maxretries
        '''
        result = self._values.get("max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def output_location(
        self,
    ) -> typing.Optional[_aws_cdk_aws_databrew_ceddda9d.CfnJob.OutputLocationProperty]:
        '''``AWS::DataBrew::Job.OutputLocation``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-outputlocation
        '''
        result = self._values.get("output_location")
        return typing.cast(typing.Optional[_aws_cdk_aws_databrew_ceddda9d.CfnJob.OutputLocationProperty], result)

    @builtins.property
    def outputs(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_databrew_ceddda9d.CfnJob.OutputProperty]]:
        '''The output properties for the job.'''
        result = self._values.get("outputs")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_databrew_ceddda9d.CfnJob.OutputProperty]], result)

    @builtins.property
    def profile_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_databrew_ceddda9d.CfnJob.ProfileConfigurationProperty]:
        '''Configuration for profile jobs.

        Configuration can be used to select columns, do evaluations, and override default parameters of evaluations. When configuration is undefined, the profile job will apply default settings to all supported columns.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-profileconfiguration
        '''
        result = self._values.get("profile_configuration")
        return typing.cast(typing.Optional[_aws_cdk_aws_databrew_ceddda9d.CfnJob.ProfileConfigurationProperty], result)

    @builtins.property
    def project_name(self) -> typing.Optional[builtins.str]:
        '''The name of the project that the job is associated with.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-projectname
        '''
        result = self._values.get("project_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recipe(
        self,
    ) -> typing.Optional[_aws_cdk_aws_databrew_ceddda9d.CfnJob.RecipeProperty]:
        '''The recipe to be used by the DataBrew job which is a series of data transformation steps.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-recipe
        '''
        result = self._values.get("recipe")
        return typing.cast(typing.Optional[_aws_cdk_aws_databrew_ceddda9d.CfnJob.RecipeProperty], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''Metadata tags that have been applied to the job.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''The job's timeout in minutes.

        A job that attempts to run longer than this timeout period ends with a status of ``TIMEOUT`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-timeout
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def validation_configurations(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_databrew_ceddda9d.CfnJob.ValidationConfigurationProperty]]:
        '''List of validation configurations that are applied to the profile job.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-databrew-job.html#cfn-databrew-job-validationconfigurations
        '''
        result = self._values.get("validation_configurations")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_databrew_ceddda9d.CfnJob.ValidationConfigurationProperty]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataBrewTransformStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataStage(
    Stage,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="aws-ddk-core.DataStage",
):
    '''Class that represents a data stage within a data pipeline.

    To create a DataStage, inherit from this class, add infrastructure required by the stage,
    and implement ``eventPatterns`` and ``targets`` properties.

    Example::

        class MyStage extends DataStage:
          readonly queue: sqs.Queue;
        
          constructor(scope: Construct, id: string, props: MyStageProps) {
             super(scope, id, props);
        
             this.queue = sqs.Queue(this, "Queue");
        
             this.eventPatterns = {
               detail_type: ["my-detail-type"],
             };
             this.targets = [new events_targets.SqsQueue(this.queue)];
          }
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs the stage.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param alarms_enabled: Enable/Disable all alarms in a DataStage. Default: true
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7ee0133925b96b521f696b544f087847c2e6916f79bbdcf76306ed73653fdb2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataStageProps(
            alarms_enabled=alarms_enabled, description=description, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addAlarm")
    def add_alarm(
        self,
        id: builtins.str,
        *,
        metric: _aws_cdk_aws_cloudwatch_ceddda9d.IMetric,
        comparison_operator: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        threshold: typing.Optional[jsii.Number] = None,
    ) -> "DataStage":
        '''Add a CloudWatch alarm for the DataStage.

        :param id: Identifier of the CloudWatch Alarm.
        :param metric: Metric to use for creating the stage's CloudWatch Alarm.
        :param comparison_operator: Comparison operator to use for alarm. Default: GREATER_THAN_THRESHOLD
        :param evaluation_periods: The value against which the specified alarm statistic is compared. Default: 5
        :param threshold: The number of periods over which data is compared to the specified threshold. Default: 1

        :return: this DataStage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfe170c2325021dad043fac92cbbedf46c28aacb0956794521a87dbad31593a0)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AlarmProps(
            metric=metric,
            comparison_operator=comparison_operator,
            evaluation_periods=evaluation_periods,
            threshold=threshold,
        )

        return typing.cast("DataStage", jsii.invoke(self, "addAlarm", [id, props]))

    @builtins.property
    @jsii.member(jsii_name="alarmsEnabled")
    def alarms_enabled(self) -> builtins.bool:
        '''Flag indicating whether the alarms are enabled for this stage.'''
        return typing.cast(builtins.bool, jsii.get(self, "alarmsEnabled"))

    @builtins.property
    @jsii.member(jsii_name="cloudwatchAlarms")
    def cloudwatch_alarms(self) -> typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.Alarm]:
        '''List of CloudWatch Alarms linked to the stage.'''
        return typing.cast(typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.Alarm], jsii.get(self, "cloudwatchAlarms"))


class _DataStageProxy(
    DataStage,
    jsii.proxy_for(Stage), # type: ignore[misc]
):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, DataStage).__jsii_proxy_class__ = lambda : _DataStageProxy


@jsii.data_type(
    jsii_type="aws-ddk-core.DataStageProps",
    jsii_struct_bases=[StageProps],
    name_mapping={
        "description": "description",
        "name": "name",
        "alarms_enabled": "alarmsEnabled",
    },
)
class DataStageProps(StageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties for the ``DataStage``.

        :param description: Description of the stage.
        :param name: Name of the stage.
        :param alarms_enabled: Enable/Disable all alarms in a DataStage. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cf78e5b7c077cc8d8a6b8227060c5d2b68df15e3f29e358244b75ef0b897e42)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument alarms_enabled", value=alarms_enabled, expected_type=type_hints["alarms_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if alarms_enabled is not None:
            self._values["alarms_enabled"] = alarms_enabled

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alarms_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable/Disable all alarms in a DataStage.

        :default: true
        '''
        result = self._values.get("alarms_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.EMRServerlessJobStageProps",
    jsii_struct_bases=[StateMachineStageProps],
    name_mapping={
        "description": "description",
        "name": "name",
        "additional_role_policy_statements": "additionalRolePolicyStatements",
        "alarms_enabled": "alarmsEnabled",
        "definition": "definition",
        "definition_file": "definitionFile",
        "state_machine_failed_executions_alarm_evaluation_periods": "stateMachineFailedExecutionsAlarmEvaluationPeriods",
        "state_machine_failed_executions_alarm_threshold": "stateMachineFailedExecutionsAlarmThreshold",
        "state_machine_input": "stateMachineInput",
        "state_machine_name": "stateMachineName",
        "application_id": "applicationId",
        "execution_role_arn": "executionRoleArn",
        "job_driver": "jobDriver",
        "job_execution_status_check_period": "jobExecutionStatusCheckPeriod",
        "start_job_run_props": "startJobRunProps",
    },
)
class EMRServerlessJobStageProps(StateMachineStageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        application_id: builtins.str,
        execution_role_arn: builtins.str,
        job_driver: typing.Mapping[builtins.str, typing.Any],
        job_execution_status_check_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        start_job_run_props: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''Properties of the EMR Serverless Job stage.

        :param description: Description of the stage.
        :param name: Name of the stage.
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param application_id: EMR Serverless Application Id.
        :param execution_role_arn: EMR Execution Role Arn.
        :param job_driver: The job driver for the job run. This is a Tagged Union structure. Only one of the following top level keys can be set: 'sparkSubmit', 'hive'
        :param job_execution_status_check_period: Duration to wait between polling job status. Defaults to 30 seconds.
        :param start_job_run_props: Additional properties to pass to 'emrserverless:StartJobRun'. https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_StartJobRun.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a74bc867d821b2a380e6cc61db61d700e291094dae87fe77909819ed40f25b02)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument additional_role_policy_statements", value=additional_role_policy_statements, expected_type=type_hints["additional_role_policy_statements"])
            check_type(argname="argument alarms_enabled", value=alarms_enabled, expected_type=type_hints["alarms_enabled"])
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
            check_type(argname="argument definition_file", value=definition_file, expected_type=type_hints["definition_file"])
            check_type(argname="argument state_machine_failed_executions_alarm_evaluation_periods", value=state_machine_failed_executions_alarm_evaluation_periods, expected_type=type_hints["state_machine_failed_executions_alarm_evaluation_periods"])
            check_type(argname="argument state_machine_failed_executions_alarm_threshold", value=state_machine_failed_executions_alarm_threshold, expected_type=type_hints["state_machine_failed_executions_alarm_threshold"])
            check_type(argname="argument state_machine_input", value=state_machine_input, expected_type=type_hints["state_machine_input"])
            check_type(argname="argument state_machine_name", value=state_machine_name, expected_type=type_hints["state_machine_name"])
            check_type(argname="argument application_id", value=application_id, expected_type=type_hints["application_id"])
            check_type(argname="argument execution_role_arn", value=execution_role_arn, expected_type=type_hints["execution_role_arn"])
            check_type(argname="argument job_driver", value=job_driver, expected_type=type_hints["job_driver"])
            check_type(argname="argument job_execution_status_check_period", value=job_execution_status_check_period, expected_type=type_hints["job_execution_status_check_period"])
            check_type(argname="argument start_job_run_props", value=start_job_run_props, expected_type=type_hints["start_job_run_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_id": application_id,
            "execution_role_arn": execution_role_arn,
            "job_driver": job_driver,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if additional_role_policy_statements is not None:
            self._values["additional_role_policy_statements"] = additional_role_policy_statements
        if alarms_enabled is not None:
            self._values["alarms_enabled"] = alarms_enabled
        if definition is not None:
            self._values["definition"] = definition
        if definition_file is not None:
            self._values["definition_file"] = definition_file
        if state_machine_failed_executions_alarm_evaluation_periods is not None:
            self._values["state_machine_failed_executions_alarm_evaluation_periods"] = state_machine_failed_executions_alarm_evaluation_periods
        if state_machine_failed_executions_alarm_threshold is not None:
            self._values["state_machine_failed_executions_alarm_threshold"] = state_machine_failed_executions_alarm_threshold
        if state_machine_input is not None:
            self._values["state_machine_input"] = state_machine_input
        if state_machine_name is not None:
            self._values["state_machine_name"] = state_machine_name
        if job_execution_status_check_period is not None:
            self._values["job_execution_status_check_period"] = job_execution_status_check_period
        if start_job_run_props is not None:
            self._values["start_job_run_props"] = start_job_run_props

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_role_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Additional IAM policy statements to add to the state machine role.'''
        result = self._values.get("additional_role_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def alarms_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable/Disable all alarms in the stage.

        :default: true
        '''
        result = self._values.get("alarms_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def definition(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]]:
        '''Steps for the state machine.

        Can either be provided as 'sfn.IChainable' or a JSON string.
        '''
        result = self._values.get("definition")
        return typing.cast(typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]], result)

    @builtins.property
    def definition_file(self) -> typing.Optional[builtins.str]:
        '''File containing a JSON definition for the state machine.'''
        result = self._values.get("definition_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_machine_failed_executions_alarm_evaluation_periods(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of periods over which data is compared to the specified threshold.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_failed_executions_alarm_threshold(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of failed state machine executions before triggering CW alarm.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Input of the state machine.'''
        result = self._values.get("state_machine_input")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_machine_name(self) -> typing.Optional[builtins.str]:
        '''Name of the state machine.'''
        result = self._values.get("state_machine_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application_id(self) -> builtins.str:
        '''EMR Serverless Application Id.'''
        result = self._values.get("application_id")
        assert result is not None, "Required property 'application_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def execution_role_arn(self) -> builtins.str:
        '''EMR Execution Role Arn.'''
        result = self._values.get("execution_role_arn")
        assert result is not None, "Required property 'execution_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def job_driver(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''The job driver for the job run.

        This is a Tagged Union structure.
        Only one of the following top level
        keys can be set: 'sparkSubmit', 'hive'
        '''
        result = self._values.get("job_driver")
        assert result is not None, "Required property 'job_driver' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def job_execution_status_check_period(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Duration to wait between polling job status.

        Defaults to 30 seconds.
        '''
        result = self._values.get("job_execution_status_check_period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def start_job_run_props(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Additional properties to pass to 'emrserverless:StartJobRun'.

        https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_StartJobRun.html
        '''
        result = self._values.get("start_job_run_props")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EMRServerlessJobStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EventStage(
    Stage,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="aws-ddk-core.EventStage",
):
    '''Class that represents an event stage within a data pipeline.

    To create an EventStage, inherit from this class, add infrastructure required by the stage,
    and implement the ``eventPattern`` property.

    The ``targets`` property will be set to null.

    Example::

        class MyStage extends EventStage:
          constructor(scope: Construct, id: string, props: MyStageProps) {
             super(scope, id, props);
        
             this.eventPatterns = {
               source: ["aws.s3"],
               detail: props.detail,
               detail_type: props.detail_type,
             };
          }
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs event stage.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41f4bcf520b1f5e4739a71110428c14cbff5ea45be37a68ea1fe04dbffd91d83)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EventStageProps(description=description, name=name)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Input targets for the stage.

        Targets are used by Event Rules to describe what should be invoked when a rule matches an event.
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], jsii.get(self, "targets"))


class _EventStageProxy(
    EventStage,
    jsii.proxy_for(Stage), # type: ignore[misc]
):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, EventStage).__jsii_proxy_class__ = lambda : _EventStageProxy


@jsii.data_type(
    jsii_type="aws-ddk-core.EventStageProps",
    jsii_struct_bases=[StageProps],
    name_mapping={"description": "description", "name": "name"},
)
class EventStageProps(StageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for the event stage.

        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2768fcf39322e444b8b05e9cfa0508e071c34b9e8a29e28fc79130506d7aeb6)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FirehoseToS3Stage(
    DataStage,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.FirehoseToS3Stage",
):
    '''DDK Kinesis Firehose Delivery stream to S3 stage, with an optional Kinesis Data Stream.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        data_output_prefix: typing.Optional[builtins.str] = None,
        data_stream: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream] = None,
        data_stream_enabled: typing.Optional[builtins.bool] = None,
        delivery_stream_data_freshness_errors_alarm_threshold: typing.Optional[jsii.Number] = None,
        delivery_stream_data_freshness_errors_evaluation_periods: typing.Optional[jsii.Number] = None,
        firehose_delivery_stream: typing.Optional[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.DeliveryStream] = None,
        firehose_delivery_stream_props: typing.Optional[typing.Union[DeliveryStreamProps, typing.Dict[builtins.str, typing.Any]]] = None,
        kinesis_firehose_destinations_s3_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_destinations_alpha_8ee8dbdc.S3BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        s3_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs ``FirehoseToS3Stage``.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param data_output_prefix: A prefix that Kinesis Data Firehose evaluates and adds to records before writing them to S3. This prefix appears immediately following the bucket name. Default: “YYYY/MM/DD/HH”
        :param data_stream: Preexisting Kinesis Data Stream to use in stage before Delivery Stream. Setting this parameter will override any creation of Kinesis Data Streams in this stage. The ``dataStreamEnabled`` parameter will have no effect.
        :param data_stream_enabled: Add Kinesis Data Stream to front Firehose Delivery. Default: false
        :param delivery_stream_data_freshness_errors_alarm_threshold: Threshold for Cloudwatch Alarm created for this stage. Default: 900
        :param delivery_stream_data_freshness_errors_evaluation_periods: Evaluation period value for Cloudwatch alarm created for this stage. Default: 1
        :param firehose_delivery_stream: Firehose Delivery stream. If no stram is provided, a new one is created.
        :param firehose_delivery_stream_props: Properties of the Firehose Delivery stream to be created.
        :param kinesis_firehose_destinations_s3_bucket_props: Props for defining an S3 destination of a Kinesis Data Firehose delivery stream.
        :param s3_bucket: Preexisting S3 Bucket to use as a destination for the Firehose Stream. If no bucket is provided, a new one is created. Amazon EventBridge notifications must be enabled on the bucket in order for this stage to produce events after its completion.
        :param s3_bucket_props: Properties of the S3 Bucket to be created as a delivery destination. Amazon EventBridge notifications must be enabled on the bucket in order for this stage to produce events after its completion.
        :param alarms_enabled: Enable/Disable all alarms in a DataStage. Default: true
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f9217104050cf03ef7cf7519808ce659edfe6c1ba00722ea6601239921cfd56)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FirehoseToS3StageProps(
            data_output_prefix=data_output_prefix,
            data_stream=data_stream,
            data_stream_enabled=data_stream_enabled,
            delivery_stream_data_freshness_errors_alarm_threshold=delivery_stream_data_freshness_errors_alarm_threshold,
            delivery_stream_data_freshness_errors_evaluation_periods=delivery_stream_data_freshness_errors_evaluation_periods,
            firehose_delivery_stream=firehose_delivery_stream,
            firehose_delivery_stream_props=firehose_delivery_stream_props,
            kinesis_firehose_destinations_s3_bucket_props=kinesis_firehose_destinations_s3_bucket_props,
            s3_bucket=s3_bucket,
            s3_bucket_props=s3_bucket_props,
            alarms_enabled=alarms_enabled,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "bucket"))

    @builtins.property
    @jsii.member(jsii_name="deliveryStream")
    def delivery_stream(
        self,
    ) -> _aws_cdk_aws_kinesisfirehose_alpha_30daaf29.DeliveryStream:
        return typing.cast(_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.DeliveryStream, jsii.get(self, "deliveryStream"))

    @builtins.property
    @jsii.member(jsii_name="dataStream")
    def data_stream(self) -> typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream]:
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream], jsii.get(self, "dataStream"))

    @builtins.property
    @jsii.member(jsii_name="eventPattern")
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        '''Output event pattern of the stage.

        Event pattern describes the structure of output event(s) produced by this stage.
        Event Rules use event patterns to select events and route them to targets.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern], jsii.get(self, "eventPattern"))

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Input targets for the stage.

        Targets are used by Event Rules to describe what should be invoked when a rule matches an event.
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], jsii.get(self, "targets"))


@jsii.data_type(
    jsii_type="aws-ddk-core.FirehoseToS3StageProps",
    jsii_struct_bases=[DataStageProps],
    name_mapping={
        "description": "description",
        "name": "name",
        "alarms_enabled": "alarmsEnabled",
        "data_output_prefix": "dataOutputPrefix",
        "data_stream": "dataStream",
        "data_stream_enabled": "dataStreamEnabled",
        "delivery_stream_data_freshness_errors_alarm_threshold": "deliveryStreamDataFreshnessErrorsAlarmThreshold",
        "delivery_stream_data_freshness_errors_evaluation_periods": "deliveryStreamDataFreshnessErrorsEvaluationPeriods",
        "firehose_delivery_stream": "firehoseDeliveryStream",
        "firehose_delivery_stream_props": "firehoseDeliveryStreamProps",
        "kinesis_firehose_destinations_s3_bucket_props": "kinesisFirehoseDestinationsS3BucketProps",
        "s3_bucket": "s3Bucket",
        "s3_bucket_props": "s3BucketProps",
    },
)
class FirehoseToS3StageProps(DataStageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        data_output_prefix: typing.Optional[builtins.str] = None,
        data_stream: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream] = None,
        data_stream_enabled: typing.Optional[builtins.bool] = None,
        delivery_stream_data_freshness_errors_alarm_threshold: typing.Optional[jsii.Number] = None,
        delivery_stream_data_freshness_errors_evaluation_periods: typing.Optional[jsii.Number] = None,
        firehose_delivery_stream: typing.Optional[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.DeliveryStream] = None,
        firehose_delivery_stream_props: typing.Optional[typing.Union[DeliveryStreamProps, typing.Dict[builtins.str, typing.Any]]] = None,
        kinesis_firehose_destinations_s3_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_destinations_alpha_8ee8dbdc.S3BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        s3_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for ``FirehoseToS3Stage``.

        :param description: Description of the stage.
        :param name: Name of the stage.
        :param alarms_enabled: Enable/Disable all alarms in a DataStage. Default: true
        :param data_output_prefix: A prefix that Kinesis Data Firehose evaluates and adds to records before writing them to S3. This prefix appears immediately following the bucket name. Default: “YYYY/MM/DD/HH”
        :param data_stream: Preexisting Kinesis Data Stream to use in stage before Delivery Stream. Setting this parameter will override any creation of Kinesis Data Streams in this stage. The ``dataStreamEnabled`` parameter will have no effect.
        :param data_stream_enabled: Add Kinesis Data Stream to front Firehose Delivery. Default: false
        :param delivery_stream_data_freshness_errors_alarm_threshold: Threshold for Cloudwatch Alarm created for this stage. Default: 900
        :param delivery_stream_data_freshness_errors_evaluation_periods: Evaluation period value for Cloudwatch alarm created for this stage. Default: 1
        :param firehose_delivery_stream: Firehose Delivery stream. If no stram is provided, a new one is created.
        :param firehose_delivery_stream_props: Properties of the Firehose Delivery stream to be created.
        :param kinesis_firehose_destinations_s3_bucket_props: Props for defining an S3 destination of a Kinesis Data Firehose delivery stream.
        :param s3_bucket: Preexisting S3 Bucket to use as a destination for the Firehose Stream. If no bucket is provided, a new one is created. Amazon EventBridge notifications must be enabled on the bucket in order for this stage to produce events after its completion.
        :param s3_bucket_props: Properties of the S3 Bucket to be created as a delivery destination. Amazon EventBridge notifications must be enabled on the bucket in order for this stage to produce events after its completion.
        '''
        if isinstance(firehose_delivery_stream_props, dict):
            firehose_delivery_stream_props = DeliveryStreamProps(**firehose_delivery_stream_props)
        if isinstance(kinesis_firehose_destinations_s3_bucket_props, dict):
            kinesis_firehose_destinations_s3_bucket_props = _aws_cdk_aws_kinesisfirehose_destinations_alpha_8ee8dbdc.S3BucketProps(**kinesis_firehose_destinations_s3_bucket_props)
        if isinstance(s3_bucket_props, dict):
            s3_bucket_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**s3_bucket_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__701f035bba059b01929f2b8055755baf96f72f5089bc32da86d2dc3cacf0f767)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument alarms_enabled", value=alarms_enabled, expected_type=type_hints["alarms_enabled"])
            check_type(argname="argument data_output_prefix", value=data_output_prefix, expected_type=type_hints["data_output_prefix"])
            check_type(argname="argument data_stream", value=data_stream, expected_type=type_hints["data_stream"])
            check_type(argname="argument data_stream_enabled", value=data_stream_enabled, expected_type=type_hints["data_stream_enabled"])
            check_type(argname="argument delivery_stream_data_freshness_errors_alarm_threshold", value=delivery_stream_data_freshness_errors_alarm_threshold, expected_type=type_hints["delivery_stream_data_freshness_errors_alarm_threshold"])
            check_type(argname="argument delivery_stream_data_freshness_errors_evaluation_periods", value=delivery_stream_data_freshness_errors_evaluation_periods, expected_type=type_hints["delivery_stream_data_freshness_errors_evaluation_periods"])
            check_type(argname="argument firehose_delivery_stream", value=firehose_delivery_stream, expected_type=type_hints["firehose_delivery_stream"])
            check_type(argname="argument firehose_delivery_stream_props", value=firehose_delivery_stream_props, expected_type=type_hints["firehose_delivery_stream_props"])
            check_type(argname="argument kinesis_firehose_destinations_s3_bucket_props", value=kinesis_firehose_destinations_s3_bucket_props, expected_type=type_hints["kinesis_firehose_destinations_s3_bucket_props"])
            check_type(argname="argument s3_bucket", value=s3_bucket, expected_type=type_hints["s3_bucket"])
            check_type(argname="argument s3_bucket_props", value=s3_bucket_props, expected_type=type_hints["s3_bucket_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if alarms_enabled is not None:
            self._values["alarms_enabled"] = alarms_enabled
        if data_output_prefix is not None:
            self._values["data_output_prefix"] = data_output_prefix
        if data_stream is not None:
            self._values["data_stream"] = data_stream
        if data_stream_enabled is not None:
            self._values["data_stream_enabled"] = data_stream_enabled
        if delivery_stream_data_freshness_errors_alarm_threshold is not None:
            self._values["delivery_stream_data_freshness_errors_alarm_threshold"] = delivery_stream_data_freshness_errors_alarm_threshold
        if delivery_stream_data_freshness_errors_evaluation_periods is not None:
            self._values["delivery_stream_data_freshness_errors_evaluation_periods"] = delivery_stream_data_freshness_errors_evaluation_periods
        if firehose_delivery_stream is not None:
            self._values["firehose_delivery_stream"] = firehose_delivery_stream
        if firehose_delivery_stream_props is not None:
            self._values["firehose_delivery_stream_props"] = firehose_delivery_stream_props
        if kinesis_firehose_destinations_s3_bucket_props is not None:
            self._values["kinesis_firehose_destinations_s3_bucket_props"] = kinesis_firehose_destinations_s3_bucket_props
        if s3_bucket is not None:
            self._values["s3_bucket"] = s3_bucket
        if s3_bucket_props is not None:
            self._values["s3_bucket_props"] = s3_bucket_props

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alarms_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable/Disable all alarms in a DataStage.

        :default: true
        '''
        result = self._values.get("alarms_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def data_output_prefix(self) -> typing.Optional[builtins.str]:
        '''A prefix that Kinesis Data Firehose evaluates and adds to records before writing them to S3.

        This prefix appears immediately following the bucket name.

        :default: “YYYY/MM/DD/HH”
        '''
        result = self._values.get("data_output_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_stream(self) -> typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream]:
        '''Preexisting Kinesis Data Stream to use in stage before Delivery Stream.

        Setting this parameter will override any creation of Kinesis Data Streams
        in this stage.
        The ``dataStreamEnabled`` parameter will have no effect.
        '''
        result = self._values.get("data_stream")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream], result)

    @builtins.property
    def data_stream_enabled(self) -> typing.Optional[builtins.bool]:
        '''Add Kinesis Data Stream to front Firehose Delivery.

        :default: false
        '''
        result = self._values.get("data_stream_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def delivery_stream_data_freshness_errors_alarm_threshold(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Threshold for Cloudwatch Alarm created for this stage.

        :default: 900
        '''
        result = self._values.get("delivery_stream_data_freshness_errors_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def delivery_stream_data_freshness_errors_evaluation_periods(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Evaluation period value for Cloudwatch alarm created for this stage.

        :default: 1
        '''
        result = self._values.get("delivery_stream_data_freshness_errors_evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def firehose_delivery_stream(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.DeliveryStream]:
        '''Firehose Delivery stream.

        If no stram is provided, a new one is created.
        '''
        result = self._values.get("firehose_delivery_stream")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.DeliveryStream], result)

    @builtins.property
    def firehose_delivery_stream_props(self) -> typing.Optional[DeliveryStreamProps]:
        '''Properties of the Firehose Delivery stream to be created.'''
        result = self._values.get("firehose_delivery_stream_props")
        return typing.cast(typing.Optional[DeliveryStreamProps], result)

    @builtins.property
    def kinesis_firehose_destinations_s3_bucket_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_destinations_alpha_8ee8dbdc.S3BucketProps]:
        '''Props for defining an S3 destination of a Kinesis Data Firehose delivery stream.'''
        result = self._values.get("kinesis_firehose_destinations_s3_bucket_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_destinations_alpha_8ee8dbdc.S3BucketProps], result)

    @builtins.property
    def s3_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''Preexisting S3 Bucket to use as a destination for the Firehose Stream.

        If no bucket is provided, a new one is created.

        Amazon EventBridge notifications must be enabled on the bucket in order
        for this stage to produce events after its completion.
        '''
        result = self._values.get("s3_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def s3_bucket_props(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        '''Properties of the S3 Bucket to be created as a delivery destination.

        Amazon EventBridge notifications must be enabled on the bucket in order
        for this stage to produce events after its completion.
        '''
        result = self._values.get("s3_bucket_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FirehoseToS3StageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.GlueTransformStageProps",
    jsii_struct_bases=[StateMachineStageProps],
    name_mapping={
        "description": "description",
        "name": "name",
        "additional_role_policy_statements": "additionalRolePolicyStatements",
        "alarms_enabled": "alarmsEnabled",
        "definition": "definition",
        "definition_file": "definitionFile",
        "state_machine_failed_executions_alarm_evaluation_periods": "stateMachineFailedExecutionsAlarmEvaluationPeriods",
        "state_machine_failed_executions_alarm_threshold": "stateMachineFailedExecutionsAlarmThreshold",
        "state_machine_input": "stateMachineInput",
        "state_machine_name": "stateMachineName",
        "crawler_allow_failure": "crawlerAllowFailure",
        "crawler_name": "crawlerName",
        "crawler_props": "crawlerProps",
        "crawler_role": "crawlerRole",
        "database_name": "databaseName",
        "job_name": "jobName",
        "job_props": "jobProps",
        "job_run_args": "jobRunArgs",
        "state_machine_retry_backoff_rate": "stateMachineRetryBackoffRate",
        "state_machine_retry_interval": "stateMachineRetryInterval",
        "state_machine_retry_max_attempts": "stateMachineRetryMaxAttempts",
        "targets": "targets",
    },
)
class GlueTransformStageProps(StateMachineStageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        crawler_allow_failure: typing.Optional[builtins.bool] = None,
        crawler_name: typing.Optional[builtins.str] = None,
        crawler_props: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawlerProps, typing.Dict[builtins.str, typing.Any]]] = None,
        crawler_role: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        job_name: typing.Optional[builtins.str] = None,
        job_props: typing.Optional[typing.Union[GlueFactoryProps, typing.Dict[builtins.str, typing.Any]]] = None,
        job_run_args: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_retry_backoff_rate: typing.Optional[jsii.Number] = None,
        state_machine_retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        state_machine_retry_max_attempts: typing.Optional[jsii.Number] = None,
        targets: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.TargetsProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for ``GlueTransformStage``.

        :param description: Description of the stage.
        :param name: Name of the stage.
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param crawler_allow_failure: Argument to allow stepfunction success for crawler failures/execption like Glue.CrawlerRunningException. Default: true
        :param crawler_name: The name of a preexisting Glue crawler to run. If None, a Glue crawler is created.
        :param crawler_props: Properties for the Glue Crawler.
        :param crawler_role: The crawler execution role.
        :param database_name: The name of the database in which the crawler's output is stored.
        :param job_name: The name of a preexisting Glue job to run. If None, a Glue job is created.
        :param job_props: Additional Glue job properties. For complete list of properties refer to CDK Documentation
        :param job_run_args: The input arguments to the Glue job.
        :param state_machine_retry_backoff_rate: Multiplication for how much longer the wait interval gets on every retry. Default: 2
        :param state_machine_retry_interval: How many seconds to wait initially before retrying. Default: cdk.Duration.seconds(1)
        :param state_machine_retry_max_attempts: How many times to retry this particular error. Default: 3
        :param targets: A collection of targets to crawl.
        '''
        if isinstance(crawler_props, dict):
            crawler_props = _aws_cdk_aws_glue_ceddda9d.CfnCrawlerProps(**crawler_props)
        if isinstance(job_props, dict):
            job_props = GlueFactoryProps(**job_props)
        if isinstance(targets, dict):
            targets = _aws_cdk_aws_glue_ceddda9d.CfnCrawler.TargetsProperty(**targets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36c864b97313236b09b597808a1574a4f4d21024bac872f4e182edbd9a3d0175)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument additional_role_policy_statements", value=additional_role_policy_statements, expected_type=type_hints["additional_role_policy_statements"])
            check_type(argname="argument alarms_enabled", value=alarms_enabled, expected_type=type_hints["alarms_enabled"])
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
            check_type(argname="argument definition_file", value=definition_file, expected_type=type_hints["definition_file"])
            check_type(argname="argument state_machine_failed_executions_alarm_evaluation_periods", value=state_machine_failed_executions_alarm_evaluation_periods, expected_type=type_hints["state_machine_failed_executions_alarm_evaluation_periods"])
            check_type(argname="argument state_machine_failed_executions_alarm_threshold", value=state_machine_failed_executions_alarm_threshold, expected_type=type_hints["state_machine_failed_executions_alarm_threshold"])
            check_type(argname="argument state_machine_input", value=state_machine_input, expected_type=type_hints["state_machine_input"])
            check_type(argname="argument state_machine_name", value=state_machine_name, expected_type=type_hints["state_machine_name"])
            check_type(argname="argument crawler_allow_failure", value=crawler_allow_failure, expected_type=type_hints["crawler_allow_failure"])
            check_type(argname="argument crawler_name", value=crawler_name, expected_type=type_hints["crawler_name"])
            check_type(argname="argument crawler_props", value=crawler_props, expected_type=type_hints["crawler_props"])
            check_type(argname="argument crawler_role", value=crawler_role, expected_type=type_hints["crawler_role"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument job_name", value=job_name, expected_type=type_hints["job_name"])
            check_type(argname="argument job_props", value=job_props, expected_type=type_hints["job_props"])
            check_type(argname="argument job_run_args", value=job_run_args, expected_type=type_hints["job_run_args"])
            check_type(argname="argument state_machine_retry_backoff_rate", value=state_machine_retry_backoff_rate, expected_type=type_hints["state_machine_retry_backoff_rate"])
            check_type(argname="argument state_machine_retry_interval", value=state_machine_retry_interval, expected_type=type_hints["state_machine_retry_interval"])
            check_type(argname="argument state_machine_retry_max_attempts", value=state_machine_retry_max_attempts, expected_type=type_hints["state_machine_retry_max_attempts"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if additional_role_policy_statements is not None:
            self._values["additional_role_policy_statements"] = additional_role_policy_statements
        if alarms_enabled is not None:
            self._values["alarms_enabled"] = alarms_enabled
        if definition is not None:
            self._values["definition"] = definition
        if definition_file is not None:
            self._values["definition_file"] = definition_file
        if state_machine_failed_executions_alarm_evaluation_periods is not None:
            self._values["state_machine_failed_executions_alarm_evaluation_periods"] = state_machine_failed_executions_alarm_evaluation_periods
        if state_machine_failed_executions_alarm_threshold is not None:
            self._values["state_machine_failed_executions_alarm_threshold"] = state_machine_failed_executions_alarm_threshold
        if state_machine_input is not None:
            self._values["state_machine_input"] = state_machine_input
        if state_machine_name is not None:
            self._values["state_machine_name"] = state_machine_name
        if crawler_allow_failure is not None:
            self._values["crawler_allow_failure"] = crawler_allow_failure
        if crawler_name is not None:
            self._values["crawler_name"] = crawler_name
        if crawler_props is not None:
            self._values["crawler_props"] = crawler_props
        if crawler_role is not None:
            self._values["crawler_role"] = crawler_role
        if database_name is not None:
            self._values["database_name"] = database_name
        if job_name is not None:
            self._values["job_name"] = job_name
        if job_props is not None:
            self._values["job_props"] = job_props
        if job_run_args is not None:
            self._values["job_run_args"] = job_run_args
        if state_machine_retry_backoff_rate is not None:
            self._values["state_machine_retry_backoff_rate"] = state_machine_retry_backoff_rate
        if state_machine_retry_interval is not None:
            self._values["state_machine_retry_interval"] = state_machine_retry_interval
        if state_machine_retry_max_attempts is not None:
            self._values["state_machine_retry_max_attempts"] = state_machine_retry_max_attempts
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_role_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Additional IAM policy statements to add to the state machine role.'''
        result = self._values.get("additional_role_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def alarms_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable/Disable all alarms in the stage.

        :default: true
        '''
        result = self._values.get("alarms_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def definition(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]]:
        '''Steps for the state machine.

        Can either be provided as 'sfn.IChainable' or a JSON string.
        '''
        result = self._values.get("definition")
        return typing.cast(typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]], result)

    @builtins.property
    def definition_file(self) -> typing.Optional[builtins.str]:
        '''File containing a JSON definition for the state machine.'''
        result = self._values.get("definition_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_machine_failed_executions_alarm_evaluation_periods(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of periods over which data is compared to the specified threshold.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_failed_executions_alarm_threshold(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of failed state machine executions before triggering CW alarm.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Input of the state machine.'''
        result = self._values.get("state_machine_input")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_machine_name(self) -> typing.Optional[builtins.str]:
        '''Name of the state machine.'''
        result = self._values.get("state_machine_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def crawler_allow_failure(self) -> typing.Optional[builtins.bool]:
        '''Argument to allow stepfunction success for crawler failures/execption like Glue.CrawlerRunningException.

        :default: true
        '''
        result = self._values.get("crawler_allow_failure")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def crawler_name(self) -> typing.Optional[builtins.str]:
        '''The name of a preexisting Glue crawler to run.

        If None, a Glue crawler is created.
        '''
        result = self._values.get("crawler_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def crawler_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnCrawlerProps]:
        '''Properties for the Glue Crawler.

        :link: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_glue.CfnCrawler.html
        '''
        result = self._values.get("crawler_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnCrawlerProps], result)

    @builtins.property
    def crawler_role(self) -> typing.Optional[builtins.str]:
        '''The crawler execution role.'''
        result = self._values.get("crawler_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''The name of the database in which the crawler's output is stored.'''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_name(self) -> typing.Optional[builtins.str]:
        '''The name of a preexisting Glue job to run.

        If None, a Glue job is created.
        '''
        result = self._values.get("job_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_props(self) -> typing.Optional[GlueFactoryProps]:
        '''Additional Glue job properties.

        For complete list of properties refer to CDK Documentation

        :aws-cdk_aws-glue-alpha: .Job.html
        :link: https://docs.aws.amazon.com/cdk/api/v2/docs/
        '''
        result = self._values.get("job_props")
        return typing.cast(typing.Optional[GlueFactoryProps], result)

    @builtins.property
    def job_run_args(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The input arguments to the Glue job.'''
        result = self._values.get("job_run_args")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_machine_retry_backoff_rate(self) -> typing.Optional[jsii.Number]:
        '''Multiplication for how much longer the wait interval gets on every retry.

        :default: 2
        '''
        result = self._values.get("state_machine_retry_backoff_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_retry_interval(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''How many seconds to wait initially before retrying.

        :default: cdk.Duration.seconds(1)
        '''
        result = self._values.get("state_machine_retry_interval")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def state_machine_retry_max_attempts(self) -> typing.Optional[jsii.Number]:
        '''How many times to retry this particular error.

        :default: 3
        '''
        result = self._values.get("state_machine_retry_max_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def targets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.TargetsProperty]:
        '''A collection of targets to crawl.'''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.TargetsProperty], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GlueTransformStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.MWAATriggerDagsStageProps",
    jsii_struct_bases=[StateMachineStageProps],
    name_mapping={
        "description": "description",
        "name": "name",
        "additional_role_policy_statements": "additionalRolePolicyStatements",
        "alarms_enabled": "alarmsEnabled",
        "definition": "definition",
        "definition_file": "definitionFile",
        "state_machine_failed_executions_alarm_evaluation_periods": "stateMachineFailedExecutionsAlarmEvaluationPeriods",
        "state_machine_failed_executions_alarm_threshold": "stateMachineFailedExecutionsAlarmThreshold",
        "state_machine_input": "stateMachineInput",
        "state_machine_name": "stateMachineName",
        "mwaa_environment_name": "mwaaEnvironmentName",
        "dag_path": "dagPath",
        "dags": "dags",
        "status_check_period": "statusCheckPeriod",
    },
)
class MWAATriggerDagsStageProps(StateMachineStageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        mwaa_environment_name: builtins.str,
        dag_path: typing.Optional[builtins.str] = None,
        dags: typing.Optional[typing.Sequence[builtins.str]] = None,
        status_check_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''Properties of the MWAA Trigger Dags stage.

        :param description: Description of the stage.
        :param name: Name of the stage.
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param mwaa_environment_name: Name of airflow environment.
        :param dag_path: Path to array of dag id's to check.
        :param dags: Name of dag(s) to trigger.
        :param status_check_period: Time to wait between execution status checks. Default: aws_cdk.Duration.seconds(15)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22752f7fca368ed1e29dd71501fbd74daab00450e10e80bb5c02b1233ef9c8f5)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument additional_role_policy_statements", value=additional_role_policy_statements, expected_type=type_hints["additional_role_policy_statements"])
            check_type(argname="argument alarms_enabled", value=alarms_enabled, expected_type=type_hints["alarms_enabled"])
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
            check_type(argname="argument definition_file", value=definition_file, expected_type=type_hints["definition_file"])
            check_type(argname="argument state_machine_failed_executions_alarm_evaluation_periods", value=state_machine_failed_executions_alarm_evaluation_periods, expected_type=type_hints["state_machine_failed_executions_alarm_evaluation_periods"])
            check_type(argname="argument state_machine_failed_executions_alarm_threshold", value=state_machine_failed_executions_alarm_threshold, expected_type=type_hints["state_machine_failed_executions_alarm_threshold"])
            check_type(argname="argument state_machine_input", value=state_machine_input, expected_type=type_hints["state_machine_input"])
            check_type(argname="argument state_machine_name", value=state_machine_name, expected_type=type_hints["state_machine_name"])
            check_type(argname="argument mwaa_environment_name", value=mwaa_environment_name, expected_type=type_hints["mwaa_environment_name"])
            check_type(argname="argument dag_path", value=dag_path, expected_type=type_hints["dag_path"])
            check_type(argname="argument dags", value=dags, expected_type=type_hints["dags"])
            check_type(argname="argument status_check_period", value=status_check_period, expected_type=type_hints["status_check_period"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "mwaa_environment_name": mwaa_environment_name,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if additional_role_policy_statements is not None:
            self._values["additional_role_policy_statements"] = additional_role_policy_statements
        if alarms_enabled is not None:
            self._values["alarms_enabled"] = alarms_enabled
        if definition is not None:
            self._values["definition"] = definition
        if definition_file is not None:
            self._values["definition_file"] = definition_file
        if state_machine_failed_executions_alarm_evaluation_periods is not None:
            self._values["state_machine_failed_executions_alarm_evaluation_periods"] = state_machine_failed_executions_alarm_evaluation_periods
        if state_machine_failed_executions_alarm_threshold is not None:
            self._values["state_machine_failed_executions_alarm_threshold"] = state_machine_failed_executions_alarm_threshold
        if state_machine_input is not None:
            self._values["state_machine_input"] = state_machine_input
        if state_machine_name is not None:
            self._values["state_machine_name"] = state_machine_name
        if dag_path is not None:
            self._values["dag_path"] = dag_path
        if dags is not None:
            self._values["dags"] = dags
        if status_check_period is not None:
            self._values["status_check_period"] = status_check_period

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_role_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Additional IAM policy statements to add to the state machine role.'''
        result = self._values.get("additional_role_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def alarms_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable/Disable all alarms in the stage.

        :default: true
        '''
        result = self._values.get("alarms_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def definition(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]]:
        '''Steps for the state machine.

        Can either be provided as 'sfn.IChainable' or a JSON string.
        '''
        result = self._values.get("definition")
        return typing.cast(typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]], result)

    @builtins.property
    def definition_file(self) -> typing.Optional[builtins.str]:
        '''File containing a JSON definition for the state machine.'''
        result = self._values.get("definition_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_machine_failed_executions_alarm_evaluation_periods(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of periods over which data is compared to the specified threshold.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_failed_executions_alarm_threshold(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of failed state machine executions before triggering CW alarm.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Input of the state machine.'''
        result = self._values.get("state_machine_input")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_machine_name(self) -> typing.Optional[builtins.str]:
        '''Name of the state machine.'''
        result = self._values.get("state_machine_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mwaa_environment_name(self) -> builtins.str:
        '''Name of airflow environment.'''
        result = self._values.get("mwaa_environment_name")
        assert result is not None, "Required property 'mwaa_environment_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dag_path(self) -> typing.Optional[builtins.str]:
        '''Path to array of dag id's to check.'''
        result = self._values.get("dag_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Name of dag(s) to trigger.'''
        result = self._values.get("dags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def status_check_period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Time to wait between execution status checks.

        :default: aws_cdk.Duration.seconds(15)
        '''
        result = self._values.get("status_check_period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MWAATriggerDagsStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-ddk-core.RedshiftDataApiStageProps",
    jsii_struct_bases=[StateMachineStageProps],
    name_mapping={
        "description": "description",
        "name": "name",
        "additional_role_policy_statements": "additionalRolePolicyStatements",
        "alarms_enabled": "alarmsEnabled",
        "definition": "definition",
        "definition_file": "definitionFile",
        "state_machine_failed_executions_alarm_evaluation_periods": "stateMachineFailedExecutionsAlarmEvaluationPeriods",
        "state_machine_failed_executions_alarm_threshold": "stateMachineFailedExecutionsAlarmThreshold",
        "state_machine_input": "stateMachineInput",
        "state_machine_name": "stateMachineName",
        "redshift_cluster_identifier": "redshiftClusterIdentifier",
        "sql_statements": "sqlStatements",
        "database_name": "databaseName",
        "database_user": "databaseUser",
        "polling_time": "pollingTime",
    },
)
class RedshiftDataApiStageProps(StateMachineStageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        redshift_cluster_identifier: builtins.str,
        sql_statements: typing.Sequence[builtins.str],
        database_name: typing.Optional[builtins.str] = None,
        database_user: typing.Optional[builtins.str] = None,
        polling_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''Properties for ``RedshiftDataApiStage``.

        :param description: Description of the stage.
        :param name: Name of the stage.
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param redshift_cluster_identifier: Identifier of the Redshift cluster.
        :param sql_statements: List of SQL statements to execute.
        :param database_name: Name of the database in Redshift. Default: "dev"
        :param database_user: Database user. Default: "awsuser"
        :param polling_time: Waiting time between checking whether the statements have finished executing. Default: cdk.Duration.seconds(15)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__defbc9333f2b8b3e2d55373f9b0155e5f6e83609e9153dc24f619d747ca4f133)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument additional_role_policy_statements", value=additional_role_policy_statements, expected_type=type_hints["additional_role_policy_statements"])
            check_type(argname="argument alarms_enabled", value=alarms_enabled, expected_type=type_hints["alarms_enabled"])
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
            check_type(argname="argument definition_file", value=definition_file, expected_type=type_hints["definition_file"])
            check_type(argname="argument state_machine_failed_executions_alarm_evaluation_periods", value=state_machine_failed_executions_alarm_evaluation_periods, expected_type=type_hints["state_machine_failed_executions_alarm_evaluation_periods"])
            check_type(argname="argument state_machine_failed_executions_alarm_threshold", value=state_machine_failed_executions_alarm_threshold, expected_type=type_hints["state_machine_failed_executions_alarm_threshold"])
            check_type(argname="argument state_machine_input", value=state_machine_input, expected_type=type_hints["state_machine_input"])
            check_type(argname="argument state_machine_name", value=state_machine_name, expected_type=type_hints["state_machine_name"])
            check_type(argname="argument redshift_cluster_identifier", value=redshift_cluster_identifier, expected_type=type_hints["redshift_cluster_identifier"])
            check_type(argname="argument sql_statements", value=sql_statements, expected_type=type_hints["sql_statements"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument database_user", value=database_user, expected_type=type_hints["database_user"])
            check_type(argname="argument polling_time", value=polling_time, expected_type=type_hints["polling_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "redshift_cluster_identifier": redshift_cluster_identifier,
            "sql_statements": sql_statements,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if additional_role_policy_statements is not None:
            self._values["additional_role_policy_statements"] = additional_role_policy_statements
        if alarms_enabled is not None:
            self._values["alarms_enabled"] = alarms_enabled
        if definition is not None:
            self._values["definition"] = definition
        if definition_file is not None:
            self._values["definition_file"] = definition_file
        if state_machine_failed_executions_alarm_evaluation_periods is not None:
            self._values["state_machine_failed_executions_alarm_evaluation_periods"] = state_machine_failed_executions_alarm_evaluation_periods
        if state_machine_failed_executions_alarm_threshold is not None:
            self._values["state_machine_failed_executions_alarm_threshold"] = state_machine_failed_executions_alarm_threshold
        if state_machine_input is not None:
            self._values["state_machine_input"] = state_machine_input
        if state_machine_name is not None:
            self._values["state_machine_name"] = state_machine_name
        if database_name is not None:
            self._values["database_name"] = database_name
        if database_user is not None:
            self._values["database_user"] = database_user
        if polling_time is not None:
            self._values["polling_time"] = polling_time

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_role_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Additional IAM policy statements to add to the state machine role.'''
        result = self._values.get("additional_role_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def alarms_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable/Disable all alarms in the stage.

        :default: true
        '''
        result = self._values.get("alarms_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def definition(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]]:
        '''Steps for the state machine.

        Can either be provided as 'sfn.IChainable' or a JSON string.
        '''
        result = self._values.get("definition")
        return typing.cast(typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]], result)

    @builtins.property
    def definition_file(self) -> typing.Optional[builtins.str]:
        '''File containing a JSON definition for the state machine.'''
        result = self._values.get("definition_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_machine_failed_executions_alarm_evaluation_periods(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of periods over which data is compared to the specified threshold.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_failed_executions_alarm_threshold(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The number of failed state machine executions before triggering CW alarm.

        :default: 1
        '''
        result = self._values.get("state_machine_failed_executions_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Input of the state machine.'''
        result = self._values.get("state_machine_input")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_machine_name(self) -> typing.Optional[builtins.str]:
        '''Name of the state machine.'''
        result = self._values.get("state_machine_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redshift_cluster_identifier(self) -> builtins.str:
        '''Identifier of the Redshift cluster.'''
        result = self._values.get("redshift_cluster_identifier")
        assert result is not None, "Required property 'redshift_cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sql_statements(self) -> typing.List[builtins.str]:
        '''List of SQL statements to execute.'''
        result = self._values.get("sql_statements")
        assert result is not None, "Required property 'sql_statements' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''Name of the database in Redshift.

        :default: "dev"
        '''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_user(self) -> typing.Optional[builtins.str]:
        '''Database user.

        :default: "awsuser"
        '''
        result = self._values.get("database_user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def polling_time(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Waiting time between checking whether the statements have finished executing.

        :default: cdk.Duration.seconds(15)
        '''
        result = self._values.get("polling_time")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftDataApiStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3EventStage(
    EventStage,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.S3EventStage",
):
    '''Stage implements an S3 event pattern based on event names, a bucket name and optional key prefix.

    Amazon EventBridge notifications must be enabled on the bucket in order to use this construct.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket: typing.Union[_aws_cdk_aws_s3_ceddda9d.IBucket, typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]],
        event_names: typing.Sequence[builtins.str],
        key_prefix: typing.Optional[typing.Union[builtins.str, typing.Sequence[builtins.str]]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs ``S3EventStage``.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param bucket: S3 Bucket or list of buckets. Amazon EventBridge notifications must be enabled on the bucket in order to use this construct.
        :param event_names: The list of events to capture, for example: ["Object Created"].
        :param key_prefix: The S3 prefix or list of prefixes. Capture root level prefix ("/") by default.
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faeff4d3ae690cf668837c5bb7641744355445bfe3e6990816e841afad5a577f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = S3EventStageProps(
            bucket=bucket,
            event_names=event_names,
            key_prefix=key_prefix,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="eventPattern")
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        '''Output event pattern of the stage.

        Event pattern describes the structure of output event(s) produced by this stage.
        Event Rules use event patterns to select events and route them to targets.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern], jsii.get(self, "eventPattern"))


@jsii.data_type(
    jsii_type="aws-ddk-core.S3EventStageProps",
    jsii_struct_bases=[EventStageProps],
    name_mapping={
        "description": "description",
        "name": "name",
        "bucket": "bucket",
        "event_names": "eventNames",
        "key_prefix": "keyPrefix",
    },
)
class S3EventStageProps(EventStageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        bucket: typing.Union[_aws_cdk_aws_s3_ceddda9d.IBucket, typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]],
        event_names: typing.Sequence[builtins.str],
        key_prefix: typing.Optional[typing.Union[builtins.str, typing.Sequence[builtins.str]]] = None,
    ) -> None:
        '''Properties for ``S3EventStage``.

        :param description: Description of the stage.
        :param name: Name of the stage.
        :param bucket: S3 Bucket or list of buckets. Amazon EventBridge notifications must be enabled on the bucket in order to use this construct.
        :param event_names: The list of events to capture, for example: ["Object Created"].
        :param key_prefix: The S3 prefix or list of prefixes. Capture root level prefix ("/") by default.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b66fa30f9df5c5a39526206778107c9f4992a0d357e41d5469d45e647a206a90)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument event_names", value=event_names, expected_type=type_hints["event_names"])
            check_type(argname="argument key_prefix", value=key_prefix, expected_type=type_hints["key_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "event_names": event_names,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if key_prefix is not None:
            self._values["key_prefix"] = key_prefix

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket(
        self,
    ) -> typing.Union[_aws_cdk_aws_s3_ceddda9d.IBucket, typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]]:
        '''S3 Bucket or list of buckets.

        Amazon EventBridge notifications must be enabled on the bucket in order to use this construct.
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(typing.Union[_aws_cdk_aws_s3_ceddda9d.IBucket, typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]], result)

    @builtins.property
    def event_names(self) -> typing.List[builtins.str]:
        '''The list of events to capture, for example: ["Object Created"].

        :link: https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventBridge.html
        '''
        result = self._values.get("event_names")
        assert result is not None, "Required property 'event_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def key_prefix(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, typing.List[builtins.str]]]:
        '''The S3 prefix or list of prefixes.

        Capture root level prefix ("/") by default.
        '''
        result = self._values.get("key_prefix")
        return typing.cast(typing.Optional[typing.Union[builtins.str, typing.List[builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3EventStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqsToLambdaStage(
    DataStage,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.SqsToLambdaStage",
):
    '''Stage implements an Amazon SQS queue connected to an AWS Lambda function, with an optional DLQ.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        batch_size: typing.Optional[jsii.Number] = None,
        dlq_enabled: typing.Optional[builtins.bool] = None,
        lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
        lambda_function_props: typing.Optional[typing.Union[SqsToLambdaStageFunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        max_batching_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        message_group_id: typing.Optional[builtins.str] = None,
        sqs_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
        sqs_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs ``SqsToLambdaStage``.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param batch_size: The maximum number of records retrieved from the event source at the function invocation time. Default: 10
        :param dlq_enabled: Determines if DLQ is enabled. Default: false
        :param lambda_function: Preexisting Lambda Function to use in stage. If not provided, a new function will be created.
        :param lambda_function_props: Properties for the Lambda Function that will be created by this construct (if ``lambdaFunction`` is not provided).
        :param max_batching_window: The maximum amount of time to gather records before invoking the function. Valid Range: Minimum value of 0 minutes, maximum value of 5 minutes. Default: - no batching window.
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: 1
        :param message_group_id: Message Group ID for messages sent to this queue. Required for FIFO queues.
        :param sqs_queue: Preexisting SQS Queue to use in stage. If not provided, a new queue will be created.
        :param sqs_queue_props: Properties for the SQS Queue that will be created by this construct (if ``sqsQueue`` is not provided).
        :param alarms_enabled: Enable/Disable all alarms in a DataStage. Default: true
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5be1a85b67aa2deae08f66dcc56eb002282a0b357ba91df9339c1c9e2cb7401)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SqsToLambdaStageProps(
            batch_size=batch_size,
            dlq_enabled=dlq_enabled,
            lambda_function=lambda_function,
            lambda_function_props=lambda_function_props,
            max_batching_window=max_batching_window,
            max_receive_count=max_receive_count,
            message_group_id=message_group_id,
            sqs_queue=sqs_queue,
            sqs_queue_props=sqs_queue_props,
            alarms_enabled=alarms_enabled,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "function"))

    @builtins.property
    @jsii.member(jsii_name="queue")
    def queue(self) -> _aws_cdk_aws_sqs_ceddda9d.IQueue:
        return typing.cast(_aws_cdk_aws_sqs_ceddda9d.IQueue, jsii.get(self, "queue"))

    @builtins.property
    @jsii.member(jsii_name="deadLetterQueue")
    def dead_letter_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue]:
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue], jsii.get(self, "deadLetterQueue"))

    @builtins.property
    @jsii.member(jsii_name="eventPattern")
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        '''Output event pattern of the stage.

        Event pattern describes the structure of output event(s) produced by this stage.
        Event Rules use event patterns to select events and route them to targets.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern], jsii.get(self, "eventPattern"))

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Input targets for the stage.

        Targets are used by Event Rules to describe what should be invoked when a rule matches an event.
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], jsii.get(self, "targets"))


@jsii.data_type(
    jsii_type="aws-ddk-core.SqsToLambdaStageProps",
    jsii_struct_bases=[DataStageProps],
    name_mapping={
        "description": "description",
        "name": "name",
        "alarms_enabled": "alarmsEnabled",
        "batch_size": "batchSize",
        "dlq_enabled": "dlqEnabled",
        "lambda_function": "lambdaFunction",
        "lambda_function_props": "lambdaFunctionProps",
        "max_batching_window": "maxBatchingWindow",
        "max_receive_count": "maxReceiveCount",
        "message_group_id": "messageGroupId",
        "sqs_queue": "sqsQueue",
        "sqs_queue_props": "sqsQueueProps",
    },
)
class SqsToLambdaStageProps(DataStageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        batch_size: typing.Optional[jsii.Number] = None,
        dlq_enabled: typing.Optional[builtins.bool] = None,
        lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
        lambda_function_props: typing.Optional[typing.Union[SqsToLambdaStageFunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        max_batching_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        message_group_id: typing.Optional[builtins.str] = None,
        sqs_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
        sqs_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for ``SqsToLambdaStage``.

        :param description: Description of the stage.
        :param name: Name of the stage.
        :param alarms_enabled: Enable/Disable all alarms in a DataStage. Default: true
        :param batch_size: The maximum number of records retrieved from the event source at the function invocation time. Default: 10
        :param dlq_enabled: Determines if DLQ is enabled. Default: false
        :param lambda_function: Preexisting Lambda Function to use in stage. If not provided, a new function will be created.
        :param lambda_function_props: Properties for the Lambda Function that will be created by this construct (if ``lambdaFunction`` is not provided).
        :param max_batching_window: The maximum amount of time to gather records before invoking the function. Valid Range: Minimum value of 0 minutes, maximum value of 5 minutes. Default: - no batching window.
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: 1
        :param message_group_id: Message Group ID for messages sent to this queue. Required for FIFO queues.
        :param sqs_queue: Preexisting SQS Queue to use in stage. If not provided, a new queue will be created.
        :param sqs_queue_props: Properties for the SQS Queue that will be created by this construct (if ``sqsQueue`` is not provided).
        '''
        if isinstance(lambda_function_props, dict):
            lambda_function_props = SqsToLambdaStageFunctionProps(**lambda_function_props)
        if isinstance(sqs_queue_props, dict):
            sqs_queue_props = _aws_cdk_aws_sqs_ceddda9d.QueueProps(**sqs_queue_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ea408fc3fa64f721e1e8e8f5dba2b0b6340914a77963785a7642a5943b0a04a)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument alarms_enabled", value=alarms_enabled, expected_type=type_hints["alarms_enabled"])
            check_type(argname="argument batch_size", value=batch_size, expected_type=type_hints["batch_size"])
            check_type(argname="argument dlq_enabled", value=dlq_enabled, expected_type=type_hints["dlq_enabled"])
            check_type(argname="argument lambda_function", value=lambda_function, expected_type=type_hints["lambda_function"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
            check_type(argname="argument max_batching_window", value=max_batching_window, expected_type=type_hints["max_batching_window"])
            check_type(argname="argument max_receive_count", value=max_receive_count, expected_type=type_hints["max_receive_count"])
            check_type(argname="argument message_group_id", value=message_group_id, expected_type=type_hints["message_group_id"])
            check_type(argname="argument sqs_queue", value=sqs_queue, expected_type=type_hints["sqs_queue"])
            check_type(argname="argument sqs_queue_props", value=sqs_queue_props, expected_type=type_hints["sqs_queue_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if alarms_enabled is not None:
            self._values["alarms_enabled"] = alarms_enabled
        if batch_size is not None:
            self._values["batch_size"] = batch_size
        if dlq_enabled is not None:
            self._values["dlq_enabled"] = dlq_enabled
        if lambda_function is not None:
            self._values["lambda_function"] = lambda_function
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if max_batching_window is not None:
            self._values["max_batching_window"] = max_batching_window
        if max_receive_count is not None:
            self._values["max_receive_count"] = max_receive_count
        if message_group_id is not None:
            self._values["message_group_id"] = message_group_id
        if sqs_queue is not None:
            self._values["sqs_queue"] = sqs_queue
        if sqs_queue_props is not None:
            self._values["sqs_queue_props"] = sqs_queue_props

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alarms_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable/Disable all alarms in a DataStage.

        :default: true
        '''
        result = self._values.get("alarms_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def batch_size(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of records retrieved from the event source at the function invocation time.

        :default: 10
        '''
        result = self._values.get("batch_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dlq_enabled(self) -> typing.Optional[builtins.bool]:
        '''Determines if DLQ is enabled.

        :default: false
        '''
        result = self._values.get("dlq_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lambda_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''Preexisting Lambda Function to use in stage.

        If not provided, a new function will be created.
        '''
        result = self._values.get("lambda_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], result)

    @builtins.property
    def lambda_function_props(self) -> typing.Optional[SqsToLambdaStageFunctionProps]:
        '''Properties for the Lambda Function that will be created by this construct (if ``lambdaFunction`` is not provided).'''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[SqsToLambdaStageFunctionProps], result)

    @builtins.property
    def max_batching_window(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The maximum amount of time to gather records before invoking the function.

        Valid Range: Minimum value of 0 minutes, maximum value of 5 minutes.
        Default: - no batching window.
        '''
        result = self._values.get("max_batching_window")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def max_receive_count(self) -> typing.Optional[jsii.Number]:
        '''The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue.

        :default: 1
        '''
        result = self._values.get("max_receive_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def message_group_id(self) -> typing.Optional[builtins.str]:
        '''Message Group ID for messages sent to this queue.

        Required for FIFO queues.
        '''
        result = self._values.get("message_group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sqs_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue]:
        '''Preexisting SQS Queue to use in stage.

        If not provided, a new queue will be created.
        '''
        result = self._values.get("sqs_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue], result)

    @builtins.property
    def sqs_queue_props(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps]:
        '''Properties for the SQS Queue that will be created by this construct (if ``sqsQueue`` is not provided).'''
        result = self._values.get("sqs_queue_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqsToLambdaStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StateMachineStage(
    DataStage,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="aws-ddk-core.StateMachineStage",
):
    '''DataStage with helper methods to simplify StateMachine stages creation.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs state machine stage.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9ccc4da0d6d8eb11cda39b2839889ebd93235f90bbfbdd93a92a3f816c9fd60)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StateMachineStageProps(
            additional_role_policy_statements=additional_role_policy_statements,
            alarms_enabled=alarms_enabled,
            definition=definition,
            definition_file=definition_file,
            state_machine_failed_executions_alarm_evaluation_periods=state_machine_failed_executions_alarm_evaluation_periods,
            state_machine_failed_executions_alarm_threshold=state_machine_failed_executions_alarm_threshold,
            state_machine_input=state_machine_input,
            state_machine_name=state_machine_name,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createStateMachine")
    def _create_state_machine(
        self,
        *,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> CreateStateMachineResult:
        '''Constructs a state machine from the definition.

        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param description: Description of the stage.
        :param name: Name of the stage.

        :return: Dictionary with event pattern, targets and state machine construct.
        '''
        props = StateMachineStageProps(
            additional_role_policy_statements=additional_role_policy_statements,
            alarms_enabled=alarms_enabled,
            definition=definition,
            definition_file=definition_file,
            state_machine_failed_executions_alarm_evaluation_periods=state_machine_failed_executions_alarm_evaluation_periods,
            state_machine_failed_executions_alarm_threshold=state_machine_failed_executions_alarm_threshold,
            state_machine_input=state_machine_input,
            state_machine_name=state_machine_name,
            description=description,
            name=name,
        )

        return typing.cast(CreateStateMachineResult, jsii.invoke(self, "createStateMachine", [props]))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    @abc.abstractmethod
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''State machine.'''
        ...


class _StateMachineStageProxy(
    StateMachineStage,
    jsii.proxy_for(DataStage), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''State machine.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, StateMachineStage).__jsii_proxy_class__ = lambda : _StateMachineStageProxy


class AppFlowIngestionStage(
    StateMachineStage,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.AppFlowIngestionStage",
):
    '''Stage that contains a step function that runs an AppFlow flow ingestion.

    If the AppFlow flow name is not supplied, then the flow is created.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        destination_flow_config: typing.Optional[typing.Union[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        flow_execution_status_check_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        flow_name: typing.Optional[builtins.str] = None,
        flow_tasks: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        source_flow_config: typing.Optional[typing.Union[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs AppFlowIngestionStage.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param destination_flow_config: The flow ``appflow.CfnFlow.DestinationFlowConfigProperty`` properties.
        :param flow_execution_status_check_period: Time to wait between flow execution status checks. Default: aws_cdk.Duration.seconds(15)
        :param flow_name: Name of the AppFlow flow to run. If None, an AppFlow flow is created.
        :param flow_tasks: The flow tasks properties.
        :param source_flow_config: The flow ``appflow.CfnFlow.SourceFlowConfigProperty`` properties.
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75fdc83ac05ea2b4078c2c89fa4beb028f1353a28c899b42364d275a692f3594)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AppFlowIngestionStageProps(
            destination_flow_config=destination_flow_config,
            flow_execution_status_check_period=flow_execution_status_check_period,
            flow_name=flow_name,
            flow_tasks=flow_tasks,
            source_flow_config=source_flow_config,
            additional_role_policy_statements=additional_role_policy_statements,
            alarms_enabled=alarms_enabled,
            definition=definition,
            definition_file=definition_file,
            state_machine_failed_executions_alarm_evaluation_periods=state_machine_failed_executions_alarm_evaluation_periods,
            state_machine_failed_executions_alarm_threshold=state_machine_failed_executions_alarm_threshold,
            state_machine_input=state_machine_input,
            state_machine_name=state_machine_name,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="flowName")
    def flow_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "flowName"))

    @builtins.property
    @jsii.member(jsii_name="flowObject")
    def flow_object(self) -> _aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsService:
        return typing.cast(_aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsService, jsii.get(self, "flowObject"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''State machine.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="eventPattern")
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        '''Output event pattern of the stage.

        Event pattern describes the structure of output event(s) produced by this stage.
        Event Rules use event patterns to select events and route them to targets.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern], jsii.get(self, "eventPattern"))

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Input targets for the stage.

        Targets are used by Event Rules to describe what should be invoked when a rule matches an event.
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], jsii.get(self, "targets"))


class AthenaSQLStage(
    StateMachineStage,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.AthenaSQLStage",
):
    '''Stage that contains a step function that execute Athena SQL query.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        encryption_option: typing.Optional[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.EncryptionOption] = None,
        output_location: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.Location, typing.Dict[builtins.str, typing.Any]]] = None,
        parallel: typing.Optional[builtins.bool] = None,
        query_string: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_string_path: typing.Optional[builtins.str] = None,
        work_group: typing.Optional[builtins.str] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs ``AthenaSQLStage``.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param catalog_name: Catalog name.
        :param database_name: Database name.
        :param encryption_key: Encryption KMS key.
        :param encryption_option: Encryption configuration.
        :param output_location: Output S3 location.
        :param parallel: flag to determine parallel or sequential execution. Default: false
        :param query_string: SQL queries that will be started.
        :param query_string_path: dynamic path in statemachine for SQL query to be started.
        :param work_group: Athena workgroup name.
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51d1732123dc8ece0c4c19240b905f56cb50227d150f624d8b798a82b65cbe29)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AthenaToSQLStageProps(
            catalog_name=catalog_name,
            database_name=database_name,
            encryption_key=encryption_key,
            encryption_option=encryption_option,
            output_location=output_location,
            parallel=parallel,
            query_string=query_string,
            query_string_path=query_string_path,
            work_group=work_group,
            additional_role_policy_statements=additional_role_policy_statements,
            alarms_enabled=alarms_enabled,
            definition=definition,
            definition_file=definition_file,
            state_machine_failed_executions_alarm_evaluation_periods=state_machine_failed_executions_alarm_evaluation_periods,
            state_machine_failed_executions_alarm_threshold=state_machine_failed_executions_alarm_threshold,
            state_machine_input=state_machine_input,
            state_machine_name=state_machine_name,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''State machine.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="eventBridgeEventPath")
    def event_bridge_event_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventBridgeEventPath"))

    @builtins.property
    @jsii.member(jsii_name="eventPattern")
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        '''Output event pattern of the stage.

        Event pattern describes the structure of output event(s) produced by this stage.
        Event Rules use event patterns to select events and route them to targets.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern], jsii.get(self, "eventPattern"))

    @builtins.property
    @jsii.member(jsii_name="stateMachineInput")
    def state_machine_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], jsii.get(self, "stateMachineInput"))

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Input targets for the stage.

        Targets are used by Event Rules to describe what should be invoked when a rule matches an event.
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], jsii.get(self, "targets"))


class DataBrewTransformStage(
    StateMachineStage,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.DataBrewTransformStage",
):
    '''Stage that contains a step function that runs DataBrew job.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        create_job: typing.Optional[builtins.bool] = None,
        database_outputs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.DatabaseOutputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        data_catalog_outputs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.DataCatalogOutputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        dataset_name: typing.Optional[builtins.str] = None,
        encryption_key_arn: typing.Optional[builtins.str] = None,
        encryption_mode: typing.Optional[builtins.str] = None,
        job_name: typing.Optional[builtins.str] = None,
        job_role_arn: typing.Optional[builtins.str] = None,
        job_sample: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.JobSampleProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        job_type: typing.Optional[builtins.str] = None,
        log_subscription: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        output_location: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.OutputLocationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        outputs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.OutputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        profile_configuration: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.ProfileConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        project_name: typing.Optional[builtins.str] = None,
        recipe: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.RecipeProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        timeout: typing.Optional[jsii.Number] = None,
        validation_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.ValidationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs ``DataBrewTransformStage``.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param create_job: Whether to create the DataBrew job or not.
        :param database_outputs: Represents a list of JDBC database output objects which defines the output destination for a DataBrew recipe job to write into.
        :param data_catalog_outputs: One or more artifacts that represent the AWS Glue Data Catalog output from running the job.
        :param dataset_name: The name of the dataset to use for the job.
        :param encryption_key_arn: The Amazon Resource Name (ARN) of an encryption key that is used to protect the job output. For more information, see `Encrypting data written by DataBrew jobs <https://docs.aws.amazon.com/databrew/latest/dg/encryption-security-configuration.html>`_
        :param encryption_mode: The encryption mode for the job, which can be one of the following:. - ``SSE-KMS`` - Server-side encryption with keys managed by AWS KMS . - ``SSE-S3`` - Server-side encryption with keys managed by Amazon S3.
        :param job_name: The name of a preexisting DataBrew job to run. If None, a DataBrew job is created.
        :param job_role_arn: The Arn of the job execution role. Required if job_name is None.
        :param job_sample: A sample configuration for profile jobs only, which determines the number of rows on which the profile job is run. If a ``JobSample`` value isn't provided, the default value is used. The default value is CUSTOM_ROWS for the mode parameter and 20,000 for the size parameter.
        :param job_type: The type of job to run. Required if job_name is None.
        :param log_subscription: The current status of Amazon CloudWatch logging for the job.
        :param max_capacity: The maximum number of nodes that can be consumed when the job processes data.
        :param max_retries: The maximum number of times to retry the job after a job run fails.
        :param output_location: ``AWS::DataBrew::Job.OutputLocation``.
        :param outputs: The output properties for the job.
        :param profile_configuration: Configuration for profile jobs. Configuration can be used to select columns, do evaluations, and override default parameters of evaluations. When configuration is undefined, the profile job will apply default settings to all supported columns.
        :param project_name: The name of the project that the job is associated with.
        :param recipe: The recipe to be used by the DataBrew job which is a series of data transformation steps.
        :param tags: Metadata tags that have been applied to the job.
        :param timeout: The job's timeout in minutes. A job that attempts to run longer than this timeout period ends with a status of ``TIMEOUT`` .
        :param validation_configurations: List of validation configurations that are applied to the profile job.
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9214d4641d831e11d83d601cf5e13ef25bd3d55977b689c3cefd7aaa9fb0fb5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataBrewTransformStageProps(
            create_job=create_job,
            database_outputs=database_outputs,
            data_catalog_outputs=data_catalog_outputs,
            dataset_name=dataset_name,
            encryption_key_arn=encryption_key_arn,
            encryption_mode=encryption_mode,
            job_name=job_name,
            job_role_arn=job_role_arn,
            job_sample=job_sample,
            job_type=job_type,
            log_subscription=log_subscription,
            max_capacity=max_capacity,
            max_retries=max_retries,
            output_location=output_location,
            outputs=outputs,
            profile_configuration=profile_configuration,
            project_name=project_name,
            recipe=recipe,
            tags=tags,
            timeout=timeout,
            validation_configurations=validation_configurations,
            additional_role_policy_statements=additional_role_policy_statements,
            alarms_enabled=alarms_enabled,
            definition=definition,
            definition_file=definition_file,
            state_machine_failed_executions_alarm_evaluation_periods=state_machine_failed_executions_alarm_evaluation_periods,
            state_machine_failed_executions_alarm_threshold=state_machine_failed_executions_alarm_threshold,
            state_machine_input=state_machine_input,
            state_machine_name=state_machine_name,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="createJob")
    def create_job(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "createJob"))

    @builtins.property
    @jsii.member(jsii_name="jobName")
    def job_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jobName"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''State machine.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="eventPattern")
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        '''Output event pattern of the stage.

        Event pattern describes the structure of output event(s) produced by this stage.
        Event Rules use event patterns to select events and route them to targets.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern], jsii.get(self, "eventPattern"))

    @builtins.property
    @jsii.member(jsii_name="job")
    def job(self) -> typing.Optional[_aws_cdk_aws_databrew_ceddda9d.CfnJob]:
        return typing.cast(typing.Optional[_aws_cdk_aws_databrew_ceddda9d.CfnJob], jsii.get(self, "job"))

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Input targets for the stage.

        Targets are used by Event Rules to describe what should be invoked when a rule matches an event.
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], jsii.get(self, "targets"))


class EMRServerlessJobStage(
    StateMachineStage,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.EMRServerlessJobStage",
):
    '''Stage that contains a step function that runs an EMR Job.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application_id: builtins.str,
        execution_role_arn: builtins.str,
        job_driver: typing.Mapping[builtins.str, typing.Any],
        job_execution_status_check_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        start_job_run_props: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs EMRServerlessJobStage.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param application_id: EMR Serverless Application Id.
        :param execution_role_arn: EMR Execution Role Arn.
        :param job_driver: The job driver for the job run. This is a Tagged Union structure. Only one of the following top level keys can be set: 'sparkSubmit', 'hive'
        :param job_execution_status_check_period: Duration to wait between polling job status. Defaults to 30 seconds.
        :param start_job_run_props: Additional properties to pass to 'emrserverless:StartJobRun'. https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_StartJobRun.html
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cbec3de2f6cc9565e6ad8777b9c24ec8039d2679d0b58ae0f8a78bb7c12d9c3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EMRServerlessJobStageProps(
            application_id=application_id,
            execution_role_arn=execution_role_arn,
            job_driver=job_driver,
            job_execution_status_check_period=job_execution_status_check_period,
            start_job_run_props=start_job_run_props,
            additional_role_policy_statements=additional_role_policy_statements,
            alarms_enabled=alarms_enabled,
            definition=definition,
            definition_file=definition_file,
            state_machine_failed_executions_alarm_evaluation_periods=state_machine_failed_executions_alarm_evaluation_periods,
            state_machine_failed_executions_alarm_threshold=state_machine_failed_executions_alarm_threshold,
            state_machine_input=state_machine_input,
            state_machine_name=state_machine_name,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''State machine.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="eventPattern")
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        '''Output event pattern of the stage.

        Event pattern describes the structure of output event(s) produced by this stage.
        Event Rules use event patterns to select events and route them to targets.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern], jsii.get(self, "eventPattern"))

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Input targets for the stage.

        Targets are used by Event Rules to describe what should be invoked when a rule matches an event.
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], jsii.get(self, "targets"))


class GlueTransformStage(
    StateMachineStage,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.GlueTransformStage",
):
    '''Stage that contains a step function that runs Glue job, and a Glue crawler afterwards.

    If the Glue job or crawler names are not supplied, then they are created.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        crawler_allow_failure: typing.Optional[builtins.bool] = None,
        crawler_name: typing.Optional[builtins.str] = None,
        crawler_props: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawlerProps, typing.Dict[builtins.str, typing.Any]]] = None,
        crawler_role: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        job_name: typing.Optional[builtins.str] = None,
        job_props: typing.Optional[typing.Union[GlueFactoryProps, typing.Dict[builtins.str, typing.Any]]] = None,
        job_run_args: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_retry_backoff_rate: typing.Optional[jsii.Number] = None,
        state_machine_retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        state_machine_retry_max_attempts: typing.Optional[jsii.Number] = None,
        targets: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.TargetsProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs ``GlueTransformStage``.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param crawler_allow_failure: Argument to allow stepfunction success for crawler failures/execption like Glue.CrawlerRunningException. Default: true
        :param crawler_name: The name of a preexisting Glue crawler to run. If None, a Glue crawler is created.
        :param crawler_props: Properties for the Glue Crawler.
        :param crawler_role: The crawler execution role.
        :param database_name: The name of the database in which the crawler's output is stored.
        :param job_name: The name of a preexisting Glue job to run. If None, a Glue job is created.
        :param job_props: Additional Glue job properties. For complete list of properties refer to CDK Documentation
        :param job_run_args: The input arguments to the Glue job.
        :param state_machine_retry_backoff_rate: Multiplication for how much longer the wait interval gets on every retry. Default: 2
        :param state_machine_retry_interval: How many seconds to wait initially before retrying. Default: cdk.Duration.seconds(1)
        :param state_machine_retry_max_attempts: How many times to retry this particular error. Default: 3
        :param targets: A collection of targets to crawl.
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ddc56c43fee5e5dc6737d945cf18cb6800a5b74340125036ae173083ba761f2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GlueTransformStageProps(
            crawler_allow_failure=crawler_allow_failure,
            crawler_name=crawler_name,
            crawler_props=crawler_props,
            crawler_role=crawler_role,
            database_name=database_name,
            job_name=job_name,
            job_props=job_props,
            job_run_args=job_run_args,
            state_machine_retry_backoff_rate=state_machine_retry_backoff_rate,
            state_machine_retry_interval=state_machine_retry_interval,
            state_machine_retry_max_attempts=state_machine_retry_max_attempts,
            targets=targets,
            additional_role_policy_statements=additional_role_policy_statements,
            alarms_enabled=alarms_enabled,
            definition=definition,
            definition_file=definition_file,
            state_machine_failed_executions_alarm_evaluation_periods=state_machine_failed_executions_alarm_evaluation_periods,
            state_machine_failed_executions_alarm_threshold=state_machine_failed_executions_alarm_threshold,
            state_machine_input=state_machine_input,
            state_machine_name=state_machine_name,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="definition")
    def definition(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.IChainable:
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.IChainable, jsii.get(self, "definition"))

    @builtins.property
    @jsii.member(jsii_name="glueJob")
    def glue_job(self) -> _aws_cdk_aws_glue_alpha_ce674d29.IJob:
        return typing.cast(_aws_cdk_aws_glue_alpha_ce674d29.IJob, jsii.get(self, "glueJob"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''State machine.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="crawler")
    def crawler(self) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnCrawler]:
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnCrawler], jsii.get(self, "crawler"))

    @builtins.property
    @jsii.member(jsii_name="crawlerName")
    def crawler_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "crawlerName"))

    @builtins.property
    @jsii.member(jsii_name="eventPattern")
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        '''Output event pattern of the stage.

        Event pattern describes the structure of output event(s) produced by this stage.
        Event Rules use event patterns to select events and route them to targets.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern], jsii.get(self, "eventPattern"))

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Input targets for the stage.

        Targets are used by Event Rules to describe what should be invoked when a rule matches an event.
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], jsii.get(self, "targets"))


class MWAATriggerDagsStage(
    StateMachineStage,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.MWAATriggerDagsStage",
):
    '''Stage that contains a step function that runs a Managed Apache Airflow (MWAA) dag or set of dags .'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        mwaa_environment_name: builtins.str,
        dag_path: typing.Optional[builtins.str] = None,
        dags: typing.Optional[typing.Sequence[builtins.str]] = None,
        status_check_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs MWAATriggerDagsStage.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param mwaa_environment_name: Name of airflow environment.
        :param dag_path: Path to array of dag id's to check.
        :param dags: Name of dag(s) to trigger.
        :param status_check_period: Time to wait between execution status checks. Default: aws_cdk.Duration.seconds(15)
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f0213661be18de8fe8fd12f50692a50182df1c8f22c50ad38963d7b78d944a0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MWAATriggerDagsStageProps(
            mwaa_environment_name=mwaa_environment_name,
            dag_path=dag_path,
            dags=dags,
            status_check_period=status_check_period,
            additional_role_policy_statements=additional_role_policy_statements,
            alarms_enabled=alarms_enabled,
            definition=definition,
            definition_file=definition_file,
            state_machine_failed_executions_alarm_evaluation_periods=state_machine_failed_executions_alarm_evaluation_periods,
            state_machine_failed_executions_alarm_threshold=state_machine_failed_executions_alarm_threshold,
            state_machine_input=state_machine_input,
            state_machine_name=state_machine_name,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="mwaaEnvironmentName")
    def mwaa_environment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mwaaEnvironmentName"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''State machine.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="eventPattern")
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        '''Output event pattern of the stage.

        Event pattern describes the structure of output event(s) produced by this stage.
        Event Rules use event patterns to select events and route them to targets.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern], jsii.get(self, "eventPattern"))

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Input targets for the stage.

        Targets are used by Event Rules to describe what should be invoked when a rule matches an event.
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], jsii.get(self, "targets"))


class RedshiftDataApiStage(
    StateMachineStage,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.RedshiftDataApiStage",
):
    '''Stage that contains a step function that executes Redshift Data API statements.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        redshift_cluster_identifier: builtins.str,
        sql_statements: typing.Sequence[builtins.str],
        database_name: typing.Optional[builtins.str] = None,
        database_user: typing.Optional[builtins.str] = None,
        polling_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
        definition_file: typing.Optional[builtins.str] = None,
        state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
        state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
        state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs ``RedshiftDataApiStage``.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param redshift_cluster_identifier: Identifier of the Redshift cluster.
        :param sql_statements: List of SQL statements to execute.
        :param database_name: Name of the database in Redshift. Default: "dev"
        :param database_user: Database user. Default: "awsuser"
        :param polling_time: Waiting time between checking whether the statements have finished executing. Default: cdk.Duration.seconds(15)
        :param additional_role_policy_statements: Additional IAM policy statements to add to the state machine role.
        :param alarms_enabled: Enable/Disable all alarms in the stage. Default: true
        :param definition: Steps for the state machine. Can either be provided as 'sfn.IChainable' or a JSON string.
        :param definition_file: File containing a JSON definition for the state machine.
        :param state_machine_failed_executions_alarm_evaluation_periods: The number of periods over which data is compared to the specified threshold. Default: 1
        :param state_machine_failed_executions_alarm_threshold: The number of failed state machine executions before triggering CW alarm. Default: 1
        :param state_machine_input: Input of the state machine.
        :param state_machine_name: Name of the state machine.
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e1a2de894e37c9f2da01cc73a49a2d2fe9ec89a86ba3d42531baaa26002a1a7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedshiftDataApiStageProps(
            redshift_cluster_identifier=redshift_cluster_identifier,
            sql_statements=sql_statements,
            database_name=database_name,
            database_user=database_user,
            polling_time=polling_time,
            additional_role_policy_statements=additional_role_policy_statements,
            alarms_enabled=alarms_enabled,
            definition=definition,
            definition_file=definition_file,
            state_machine_failed_executions_alarm_evaluation_periods=state_machine_failed_executions_alarm_evaluation_periods,
            state_machine_failed_executions_alarm_threshold=state_machine_failed_executions_alarm_threshold,
            state_machine_input=state_machine_input,
            state_machine_name=state_machine_name,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''State machine.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="eventBridgeEventPath")
    def event_bridge_event_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventBridgeEventPath"))

    @builtins.property
    @jsii.member(jsii_name="eventPattern")
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        '''Output event pattern of the stage.

        Event pattern describes the structure of output event(s) produced by this stage.
        Event Rules use event patterns to select events and route them to targets.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern], jsii.get(self, "eventPattern"))

    @builtins.property
    @jsii.member(jsii_name="stateMachineInput")
    def state_machine_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], jsii.get(self, "stateMachineInput"))

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Input targets for the stage.

        Targets are used by Event Rules to describe what should be invoked when a rule matches an event.
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], jsii.get(self, "targets"))


class SnsSqsToLambdaStage(
    SqsToLambdaStage,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-ddk-core.SnsSqsToLambdaStage",
):
    '''Stage implements an SNS Topic connected to an Amazon SQS queue and an AWS Lambda function, with an optional DLQ.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        disable_default_topic_policy: typing.Optional[builtins.bool] = None,
        filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_ceddda9d.SubscriptionFilter]] = None,
        raw_message_delivery: typing.Optional[builtins.bool] = None,
        sns_dlq_enabled: typing.Optional[builtins.bool] = None,
        sns_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        sns_topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
        batch_size: typing.Optional[jsii.Number] = None,
        dlq_enabled: typing.Optional[builtins.bool] = None,
        lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
        lambda_function_props: typing.Optional[typing.Union[SqsToLambdaStageFunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        max_batching_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        message_group_id: typing.Optional[builtins.str] = None,
        sqs_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
        sqs_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs ``SnsSqsToLambdaStage``.

        :param scope: Scope within which this construct is defined.
        :param id: Identifier of the stage.
        :param disable_default_topic_policy: Whether to disable the default topic policy generated by SnsFactory. Default: false
        :param filter_policy: The filter policy. Default: - all messages are delivered
        :param raw_message_delivery: The message to the queue is the same as it was sent to the topic. If false, the message will be wrapped in an SNS envelope. Default: false
        :param sns_dlq_enabled: Queue to be used as dead letter queue. If not passed no dead letter queue is enabled. Default: - No dead letter queue enabled.
        :param sns_topic: Preexisting SNS Topic to use in stage. If not provided, a new one will be created.
        :param sns_topic_props: Properties for the SNS Topic that will be created by this construct (if ``snsTopic`` is not provided).
        :param batch_size: The maximum number of records retrieved from the event source at the function invocation time. Default: 10
        :param dlq_enabled: Determines if DLQ is enabled. Default: false
        :param lambda_function: Preexisting Lambda Function to use in stage. If not provided, a new function will be created.
        :param lambda_function_props: Properties for the Lambda Function that will be created by this construct (if ``lambdaFunction`` is not provided).
        :param max_batching_window: The maximum amount of time to gather records before invoking the function. Valid Range: Minimum value of 0 minutes, maximum value of 5 minutes. Default: - no batching window.
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: 1
        :param message_group_id: Message Group ID for messages sent to this queue. Required for FIFO queues.
        :param sqs_queue: Preexisting SQS Queue to use in stage. If not provided, a new queue will be created.
        :param sqs_queue_props: Properties for the SQS Queue that will be created by this construct (if ``sqsQueue`` is not provided).
        :param alarms_enabled: Enable/Disable all alarms in a DataStage. Default: true
        :param description: Description of the stage.
        :param name: Name of the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1f6169c1775457f18465db8ac58b6e948ab3cee732db9fb369eb57e96e8b7ef)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SnsToLambdaStageProps(
            disable_default_topic_policy=disable_default_topic_policy,
            filter_policy=filter_policy,
            raw_message_delivery=raw_message_delivery,
            sns_dlq_enabled=sns_dlq_enabled,
            sns_topic=sns_topic,
            sns_topic_props=sns_topic_props,
            batch_size=batch_size,
            dlq_enabled=dlq_enabled,
            lambda_function=lambda_function,
            lambda_function_props=lambda_function_props,
            max_batching_window=max_batching_window,
            max_receive_count=max_receive_count,
            message_group_id=message_group_id,
            sqs_queue=sqs_queue,
            sqs_queue_props=sqs_queue_props,
            alarms_enabled=alarms_enabled,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="topic")
    def topic(self) -> _aws_cdk_aws_sns_ceddda9d.ITopic:
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.ITopic, jsii.get(self, "topic"))

    @builtins.property
    @jsii.member(jsii_name="eventPattern")
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern]:
        '''Output event pattern of the stage.

        Event pattern describes the structure of output event(s) produced by this stage.
        Event Rules use event patterns to select events and route them to targets.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventPattern], jsii.get(self, "eventPattern"))

    @builtins.property
    @jsii.member(jsii_name="snsDeadLetterQueue")
    def sns_dead_letter_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue]:
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue], jsii.get(self, "snsDeadLetterQueue"))

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Input targets for the stage.

        Targets are used by Event Rules to describe what should be invoked when a rule matches an event.
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], jsii.get(self, "targets"))


@jsii.data_type(
    jsii_type="aws-ddk-core.SnsToLambdaStageProps",
    jsii_struct_bases=[SqsToLambdaStageProps],
    name_mapping={
        "description": "description",
        "name": "name",
        "alarms_enabled": "alarmsEnabled",
        "batch_size": "batchSize",
        "dlq_enabled": "dlqEnabled",
        "lambda_function": "lambdaFunction",
        "lambda_function_props": "lambdaFunctionProps",
        "max_batching_window": "maxBatchingWindow",
        "max_receive_count": "maxReceiveCount",
        "message_group_id": "messageGroupId",
        "sqs_queue": "sqsQueue",
        "sqs_queue_props": "sqsQueueProps",
        "disable_default_topic_policy": "disableDefaultTopicPolicy",
        "filter_policy": "filterPolicy",
        "raw_message_delivery": "rawMessageDelivery",
        "sns_dlq_enabled": "snsDlqEnabled",
        "sns_topic": "snsTopic",
        "sns_topic_props": "snsTopicProps",
    },
)
class SnsToLambdaStageProps(SqsToLambdaStageProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        alarms_enabled: typing.Optional[builtins.bool] = None,
        batch_size: typing.Optional[jsii.Number] = None,
        dlq_enabled: typing.Optional[builtins.bool] = None,
        lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
        lambda_function_props: typing.Optional[typing.Union[SqsToLambdaStageFunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        max_batching_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        message_group_id: typing.Optional[builtins.str] = None,
        sqs_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
        sqs_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
        disable_default_topic_policy: typing.Optional[builtins.bool] = None,
        filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_ceddda9d.SubscriptionFilter]] = None,
        raw_message_delivery: typing.Optional[builtins.bool] = None,
        sns_dlq_enabled: typing.Optional[builtins.bool] = None,
        sns_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        sns_topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for ``SnsSqsToLambdaStage``.

        :param description: Description of the stage.
        :param name: Name of the stage.
        :param alarms_enabled: Enable/Disable all alarms in a DataStage. Default: true
        :param batch_size: The maximum number of records retrieved from the event source at the function invocation time. Default: 10
        :param dlq_enabled: Determines if DLQ is enabled. Default: false
        :param lambda_function: Preexisting Lambda Function to use in stage. If not provided, a new function will be created.
        :param lambda_function_props: Properties for the Lambda Function that will be created by this construct (if ``lambdaFunction`` is not provided).
        :param max_batching_window: The maximum amount of time to gather records before invoking the function. Valid Range: Minimum value of 0 minutes, maximum value of 5 minutes. Default: - no batching window.
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: 1
        :param message_group_id: Message Group ID for messages sent to this queue. Required for FIFO queues.
        :param sqs_queue: Preexisting SQS Queue to use in stage. If not provided, a new queue will be created.
        :param sqs_queue_props: Properties for the SQS Queue that will be created by this construct (if ``sqsQueue`` is not provided).
        :param disable_default_topic_policy: Whether to disable the default topic policy generated by SnsFactory. Default: false
        :param filter_policy: The filter policy. Default: - all messages are delivered
        :param raw_message_delivery: The message to the queue is the same as it was sent to the topic. If false, the message will be wrapped in an SNS envelope. Default: false
        :param sns_dlq_enabled: Queue to be used as dead letter queue. If not passed no dead letter queue is enabled. Default: - No dead letter queue enabled.
        :param sns_topic: Preexisting SNS Topic to use in stage. If not provided, a new one will be created.
        :param sns_topic_props: Properties for the SNS Topic that will be created by this construct (if ``snsTopic`` is not provided).
        '''
        if isinstance(lambda_function_props, dict):
            lambda_function_props = SqsToLambdaStageFunctionProps(**lambda_function_props)
        if isinstance(sqs_queue_props, dict):
            sqs_queue_props = _aws_cdk_aws_sqs_ceddda9d.QueueProps(**sqs_queue_props)
        if isinstance(sns_topic_props, dict):
            sns_topic_props = _aws_cdk_aws_sns_ceddda9d.TopicProps(**sns_topic_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1ced712cbd6acd872556813dd7192431ee7539b2ab066fa0aafd950cc7268b0)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument alarms_enabled", value=alarms_enabled, expected_type=type_hints["alarms_enabled"])
            check_type(argname="argument batch_size", value=batch_size, expected_type=type_hints["batch_size"])
            check_type(argname="argument dlq_enabled", value=dlq_enabled, expected_type=type_hints["dlq_enabled"])
            check_type(argname="argument lambda_function", value=lambda_function, expected_type=type_hints["lambda_function"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
            check_type(argname="argument max_batching_window", value=max_batching_window, expected_type=type_hints["max_batching_window"])
            check_type(argname="argument max_receive_count", value=max_receive_count, expected_type=type_hints["max_receive_count"])
            check_type(argname="argument message_group_id", value=message_group_id, expected_type=type_hints["message_group_id"])
            check_type(argname="argument sqs_queue", value=sqs_queue, expected_type=type_hints["sqs_queue"])
            check_type(argname="argument sqs_queue_props", value=sqs_queue_props, expected_type=type_hints["sqs_queue_props"])
            check_type(argname="argument disable_default_topic_policy", value=disable_default_topic_policy, expected_type=type_hints["disable_default_topic_policy"])
            check_type(argname="argument filter_policy", value=filter_policy, expected_type=type_hints["filter_policy"])
            check_type(argname="argument raw_message_delivery", value=raw_message_delivery, expected_type=type_hints["raw_message_delivery"])
            check_type(argname="argument sns_dlq_enabled", value=sns_dlq_enabled, expected_type=type_hints["sns_dlq_enabled"])
            check_type(argname="argument sns_topic", value=sns_topic, expected_type=type_hints["sns_topic"])
            check_type(argname="argument sns_topic_props", value=sns_topic_props, expected_type=type_hints["sns_topic_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if alarms_enabled is not None:
            self._values["alarms_enabled"] = alarms_enabled
        if batch_size is not None:
            self._values["batch_size"] = batch_size
        if dlq_enabled is not None:
            self._values["dlq_enabled"] = dlq_enabled
        if lambda_function is not None:
            self._values["lambda_function"] = lambda_function
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if max_batching_window is not None:
            self._values["max_batching_window"] = max_batching_window
        if max_receive_count is not None:
            self._values["max_receive_count"] = max_receive_count
        if message_group_id is not None:
            self._values["message_group_id"] = message_group_id
        if sqs_queue is not None:
            self._values["sqs_queue"] = sqs_queue
        if sqs_queue_props is not None:
            self._values["sqs_queue_props"] = sqs_queue_props
        if disable_default_topic_policy is not None:
            self._values["disable_default_topic_policy"] = disable_default_topic_policy
        if filter_policy is not None:
            self._values["filter_policy"] = filter_policy
        if raw_message_delivery is not None:
            self._values["raw_message_delivery"] = raw_message_delivery
        if sns_dlq_enabled is not None:
            self._values["sns_dlq_enabled"] = sns_dlq_enabled
        if sns_topic is not None:
            self._values["sns_topic"] = sns_topic
        if sns_topic_props is not None:
            self._values["sns_topic_props"] = sns_topic_props

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the stage.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the stage.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alarms_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable/Disable all alarms in a DataStage.

        :default: true
        '''
        result = self._values.get("alarms_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def batch_size(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of records retrieved from the event source at the function invocation time.

        :default: 10
        '''
        result = self._values.get("batch_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dlq_enabled(self) -> typing.Optional[builtins.bool]:
        '''Determines if DLQ is enabled.

        :default: false
        '''
        result = self._values.get("dlq_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lambda_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''Preexisting Lambda Function to use in stage.

        If not provided, a new function will be created.
        '''
        result = self._values.get("lambda_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], result)

    @builtins.property
    def lambda_function_props(self) -> typing.Optional[SqsToLambdaStageFunctionProps]:
        '''Properties for the Lambda Function that will be created by this construct (if ``lambdaFunction`` is not provided).'''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[SqsToLambdaStageFunctionProps], result)

    @builtins.property
    def max_batching_window(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The maximum amount of time to gather records before invoking the function.

        Valid Range: Minimum value of 0 minutes, maximum value of 5 minutes.
        Default: - no batching window.
        '''
        result = self._values.get("max_batching_window")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def max_receive_count(self) -> typing.Optional[jsii.Number]:
        '''The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue.

        :default: 1
        '''
        result = self._values.get("max_receive_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def message_group_id(self) -> typing.Optional[builtins.str]:
        '''Message Group ID for messages sent to this queue.

        Required for FIFO queues.
        '''
        result = self._values.get("message_group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sqs_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue]:
        '''Preexisting SQS Queue to use in stage.

        If not provided, a new queue will be created.
        '''
        result = self._values.get("sqs_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue], result)

    @builtins.property
    def sqs_queue_props(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps]:
        '''Properties for the SQS Queue that will be created by this construct (if ``sqsQueue`` is not provided).'''
        result = self._values.get("sqs_queue_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps], result)

    @builtins.property
    def disable_default_topic_policy(self) -> typing.Optional[builtins.bool]:
        '''Whether to disable the default topic policy generated by SnsFactory.

        :default: false

        :see: SnsFactory.secureSnsTopicPolicy
        '''
        result = self._values.get("disable_default_topic_policy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def filter_policy(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_ceddda9d.SubscriptionFilter]]:
        '''The filter policy.

        :default: - all messages are delivered
        '''
        result = self._values.get("filter_policy")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_ceddda9d.SubscriptionFilter]], result)

    @builtins.property
    def raw_message_delivery(self) -> typing.Optional[builtins.bool]:
        '''The message to the queue is the same as it was sent to the topic.

        If false, the message will be wrapped in an SNS envelope.

        :default: false
        '''
        result = self._values.get("raw_message_delivery")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sns_dlq_enabled(self) -> typing.Optional[builtins.bool]:
        '''Queue to be used as dead letter queue.

        If not passed no dead letter queue is enabled.

        :default: - No dead letter queue enabled.
        '''
        result = self._values.get("sns_dlq_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sns_topic(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''Preexisting SNS Topic to use in stage.

        If not provided, a new one will be created.
        '''
        result = self._values.get("sns_topic")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], result)

    @builtins.property
    def sns_topic_props(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.TopicProps]:
        '''Properties for the SNS Topic that will be created by this construct (if ``snsTopic`` is not provided).'''
        result = self._values.get("sns_topic_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.TopicProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnsToLambdaStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AddApplicationStageProps",
    "AddApplicationWaveProps",
    "AddCustomStageProps",
    "AddNotificationsProps",
    "AddRuleProps",
    "AddSecurityLintStageProps",
    "AddStageProps",
    "AddTestStageProps",
    "AdditionalPipelineProps",
    "AlarmProps",
    "AppFlowIngestionStage",
    "AppFlowIngestionStageProps",
    "AthenaSQLStage",
    "AthenaToSQLStageProps",
    "BaseStack",
    "BaseStackProps",
    "CICDActions",
    "CICDPipelineStack",
    "CICDPipelineStackProps",
    "CodeArtifactPublishActionProps",
    "CodeCommitSourceActionProps",
    "Configuration",
    "Configurator",
    "CreateStateMachineResult",
    "DataBrewTransformStage",
    "DataBrewTransformStageProps",
    "DataPipeline",
    "DataPipelineProps",
    "DataStage",
    "DataStageProps",
    "DeliveryStreamProps",
    "EMRServerlessCluster",
    "EMRServerlessClusterProps",
    "EMRServerlessJobStage",
    "EMRServerlessJobStageProps",
    "EnvironmentConfiguration",
    "EventStage",
    "EventStageProps",
    "FirehoseToS3Stage",
    "FirehoseToS3StageProps",
    "GetConfigProps",
    "GetEnvConfigProps",
    "GetEnvironmentProps",
    "GetSynthActionProps",
    "GetTagsProps",
    "GlueFactory",
    "GlueFactoryProps",
    "GlueJobType",
    "GlueTransformStage",
    "GlueTransformStageProps",
    "KmsFactory",
    "MWAAEnvironment",
    "MWAAEnvironmentProps",
    "MWAALambdasResult",
    "MWAATriggerDagsStage",
    "MWAATriggerDagsStageProps",
    "PermissionsBoundaryProps",
    "RedshiftDataApiStage",
    "RedshiftDataApiStageProps",
    "S3EventStage",
    "S3EventStageProps",
    "S3Factory",
    "SnsFactory",
    "SnsSqsToLambdaStage",
    "SnsToLambdaStageProps",
    "SourceActionProps",
    "SqsToLambdaStage",
    "SqsToLambdaStageFunctionProps",
    "SqsToLambdaStageProps",
    "Stage",
    "StageProps",
    "StateMachineStage",
    "StateMachineStageProps",
    "SynthActionProps",
]

publication.publish()

def _typecheckingstub__b76c36dbcfdd4e997564efc9be54eb407b35cd3e027b00901b31d379e392170e(
    *,
    stage: _aws_cdk_ceddda9d.Stage,
    stage_id: builtins.str,
    manual_approvals: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c5ca54834b066a96cdaae8f32086d4638af32527e6bdd7356e96d6b16db8c0d(
    *,
    stage_id: builtins.str,
    stages: typing.Sequence[_aws_cdk_ceddda9d.Stage],
    manual_approvals: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8660c7ffe37e5e521438a6f05e109d7d73960491ec724c71005fa435cb1ba0cb(
    *,
    stage_name: builtins.str,
    steps: typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6b36a0552668c2be6f5870fa1fc235676fcd1d8e1633ffdcd8fe2ab50a5eb9c(
    *,
    notification_rule: typing.Optional[_aws_cdk_aws_codestarnotifications_ceddda9d.NotificationRule] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc4d3cd99b8129cd1e9e86879e1aa4a9e7d0340f69bb169e136c78c563e397f5(
    *,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    event_targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    id: typing.Optional[builtins.str] = None,
    override_rule: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule] = None,
    rule_name: typing.Optional[builtins.str] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5c6a426f2b47035ddfb61265fb0fc5f914c183c57db8be19fd6917fe3755000(
    *,
    cfn_nag_fail_build: typing.Optional[builtins.bool] = None,
    cloud_assembly_file_set: typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer] = None,
    stage_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c40909713474fb0ac5879649d02b6b9b99cca8e07cc03cfb0ee3a2161cabd53f(
    *,
    stage: Stage,
    override_rule: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule] = None,
    rule_name: typing.Optional[builtins.str] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    skip_rule: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0efd164879f28724d26fec5d40738d32540d827f1e7d46271d569f72a3a0a21f(
    *,
    cloud_assembly_file_set: typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer] = None,
    commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    stage_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34c4dbaccc767dfa14746a2df4a90bdbf9d6318afb10cc0e8809c95f4447414b(
    *,
    asset_publishing_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cli_version: typing.Optional[builtins.str] = None,
    code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    code_pipeline: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Pipeline] = None,
    docker_credentials: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.DockerCredential]] = None,
    docker_enabled_for_self_mutation: typing.Optional[builtins.bool] = None,
    docker_enabled_for_synth: typing.Optional[builtins.bool] = None,
    publish_assets_in_parallel: typing.Optional[builtins.bool] = None,
    reuse_cross_region_support_stacks: typing.Optional[builtins.bool] = None,
    self_mutation: typing.Optional[builtins.bool] = None,
    self_mutation_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    synth_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9739513f93590856f8f02851ab5bfe24bf3c845f3e37410565b3668ac8406da2(
    *,
    metric: _aws_cdk_aws_cloudwatch_ceddda9d.IMetric,
    comparison_operator: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__403bc1fd4d529dd1acdcfdf6824076a7e78329d131f442981f447f8f5298a7cc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    config: typing.Optional[typing.Union[builtins.str, typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    environment_id: typing.Optional[builtins.str] = None,
    permissions_boundary_arn: typing.Optional[builtins.str] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c52c78b6e97cce4b370cb75d9552fff81495ba02218c70f1c8947488c2c0604a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    environment_id: typing.Optional[builtins.str] = None,
    prefix: typing.Optional[builtins.str] = None,
    qualifier: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2efe5dde2538acae1f48243a64a4ddfc2bc79e8400b2883ddf4986fbd5984c8(
    exported_value: typing.Any,
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a429ca722d1fec889b8120d065d6c339e922faac9a9e70454e565500ff82514c(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    config: typing.Optional[typing.Union[builtins.str, typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    environment_id: typing.Optional[builtins.str] = None,
    permissions_boundary_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fab9ea5d8746e6c137eb1d92124b75da65dab030241ebf0002427b6ad8676aa2(
    code_pipeline_source: _aws_cdk_pipelines_ceddda9d.CodePipelineSource,
    stage_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebe600cfab48179494151cd33416082a904aa73df681b93f5266545008838275(
    file_set_producer: _aws_cdk_pipelines_ceddda9d.IFileSetProducer,
    stage_name: typing.Optional[builtins.str] = None,
    fail_build: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__203dfc08c6a839aacb072ea162bb03ae398d33f465cc8723ee83f36c65bf9fc8(
    partition: builtins.str,
    region: builtins.str,
    account: builtins.str,
    codeartifact_repository: builtins.str,
    codeartifact_domain: builtins.str,
    codeartifact_domain_owner: builtins.str,
    code_pipeline_source: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource] = None,
    role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__299e24a53c04aec79676a22aae09e979fe6ffa8af8ec8306445500237732a145(
    scope: _constructs_77d1e7e8.Construct,
    *,
    branch: builtins.str,
    repository_name: builtins.str,
    props: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.ConnectionSourceOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__906b3057114921fd5b8c18404d27778ac3f64ce364e27565682c6ab1bac71b7b(
    file_set_producer: _aws_cdk_pipelines_ceddda9d.IFileSetProducer,
    commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    stage_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a4f7374970c6409060af558e7802348870a4c4a3b9f9232e789f1488d18fb90(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cdk_language: typing.Optional[builtins.str] = None,
    pipeline_name: typing.Optional[builtins.str] = None,
    config: typing.Optional[typing.Union[builtins.str, typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    environment_id: typing.Optional[builtins.str] = None,
    permissions_boundary_arn: typing.Optional[builtins.str] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0068433bd751f33d982df797ea7caafaf7cffac6096fcfa31b631eb939dd331b(
    value: typing.Optional[_aws_cdk_aws_codestarnotifications_ceddda9d.NotificationRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e242ec0edda32ab650513e5c858717f596009d201ebe6c35d192b13bb37b46e(
    value: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipeline],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdd6e87a9d4eea532d3b53339bd619a881413d8b48bab8ceb6116633e65f946d(
    value: typing.Optional[_aws_cdk_aws_kms_ceddda9d.CfnKey],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19397f9a8bd0b90a5f185ea4729b0b19930bbfb902f228f2537c616170569bf6(
    value: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae2239ce5199560ebc5f2e8f3ab6392af34c4678da2fdeb67265c0f37277507b(
    value: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildStep],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a92abb1f3b57ec36ef721160ab799be2851ede5d3e872162fc75be713f4d3293(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    config: typing.Optional[typing.Union[builtins.str, typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    environment_id: typing.Optional[builtins.str] = None,
    permissions_boundary_arn: typing.Optional[builtins.str] = None,
    cdk_language: typing.Optional[builtins.str] = None,
    pipeline_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c35f21eb6e1a4595459d5a4102a340db464f6d6da23770e16d40eca5d3e00623(
    *,
    account: builtins.str,
    codeartifact_domain: builtins.str,
    codeartifact_domain_owner: builtins.str,
    codeartifact_repository: builtins.str,
    partition: builtins.str,
    region: builtins.str,
    code_pipeline_source: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource] = None,
    role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8379be0808b59cd840396438fecd2826772ffc3dbcfeaf5175ccf01b988d69b(
    *,
    branch: builtins.str,
    repository_name: builtins.str,
    props: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.ConnectionSourceOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daeed9e6cb5e50c39b922933d297c173f25183423bf700dfd9f8b0fe3765c923(
    *,
    environments: typing.Mapping[builtins.str, typing.Union[EnvironmentConfiguration, typing.Dict[builtins.str, typing.Any]]],
    account: typing.Optional[builtins.str] = None,
    bootstrap: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ddk_bootstrap_config_key: typing.Optional[builtins.str] = None,
    props: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    region: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83dd06108e5a02547d07299060f92123340b3d7ec7e9e6f36a8e28ce02b22a22(
    scope: _constructs_77d1e7e8.Construct,
    config: typing.Union[builtins.str, typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]],
    environment_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce369044fa737e8a329b15db41cbef0ecf3e52cea663d9bd55b6edfe486a7705(
    attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ebebaeeabeb2e14afe10bb65476a72e653389f44163949f819c5b260fc48e7c(
    scope: _constructs_77d1e7e8.Construct,
    tags: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a42d01fb82a6fe17fa9b9b89a21fb52b88b8267a8d48f866ab150cb834952324(
    *,
    event_pattern: typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]],
    state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
    targets: typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__020d69ac62c8be050bbf68165b37eefae84c4185726ff175a8444e0c59df78df(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0261b3bfb9d75b19f131b94fdac46b066b26e0543adf83caf2f9ff8436e7fc80(
    notifications_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__946287dcda6fcab40d64fc9e8f72a5917de6ace9c417f850f53a1418c864067d(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef7997fe1d9215e0814459fdbbb95740e62a7f0437cd0df0dcd43ac255b163e4(
    *,
    delivery_stream_name: typing.Optional[builtins.str] = None,
    destinations: typing.Optional[typing.Sequence[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.IDestination]] = None,
    encryption: typing.Optional[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.StreamEncryption] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    source_stream: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.IStream] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83d66a5f4ea6335b061a6877ac3664b7458c10cb62db78fcee7fdf475a19fee5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    additional_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
    vpc_cidr: typing.Optional[builtins.str] = None,
    vpc_id: typing.Optional[builtins.str] = None,
    release_label: builtins.str,
    type: builtins.str,
    architecture: typing.Optional[builtins.str] = None,
    auto_start_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStartConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    auto_stop_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStopConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    image_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ImageConfigurationInputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    initial_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InitialCapacityConfigKeyValuePairProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    interactive_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InteractiveConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    maximum_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MaximumAllowedResourcesProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    monitoring_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MonitoringConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    name: typing.Optional[builtins.str] = None,
    network_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    runtime_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ConfigurationObjectProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    scheduler_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.SchedulerConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    worker_type_specifications: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Mapping[builtins.str, typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.WorkerTypeSpecificationInputProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__864be4d07f911163bb991815f5a8c0561cfd97d707e687ef07552b1d38bb82d2(
    scope: _constructs_77d1e7e8.Construct,
    resource_name: builtins.str,
    vpc_cidr: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dff46b98beafa0af6fc125923b2225092c53114f275e10e2732de3f4d3cd2573(
    *,
    release_label: builtins.str,
    type: builtins.str,
    architecture: typing.Optional[builtins.str] = None,
    auto_start_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStartConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    auto_stop_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStopConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    image_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ImageConfigurationInputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    initial_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InitialCapacityConfigKeyValuePairProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    interactive_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InteractiveConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    maximum_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MaximumAllowedResourcesProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    monitoring_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MonitoringConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    name: typing.Optional[builtins.str] = None,
    network_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    runtime_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ConfigurationObjectProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    scheduler_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.SchedulerConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    worker_type_specifications: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Mapping[builtins.str, typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.WorkerTypeSpecificationInputProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    additional_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
    vpc_cidr: typing.Optional[builtins.str] = None,
    vpc_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf306c436463dcb56197f32e9c4793604595ef2ca8f42b2d72de058d5806870c(
    *,
    account: typing.Optional[builtins.str] = None,
    bootstrap: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    props: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    region: typing.Optional[builtins.str] = None,
    resources: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dba6810d9499d40d626ee84f10a13e1cade1e4a1602afa74c9dd333695965bd(
    *,
    config: typing.Optional[typing.Union[builtins.str, typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__392d4bf9e0a3416c4cbfe2cfcca884cc2b98f96b99a23a03e386497b6cfd2fef(
    *,
    environment_id: builtins.str,
    config_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1d1864ebb63e794b66b601804d8a186ccc2fe70e5c1aeea9def8ecd1ab83dde(
    *,
    config_path: typing.Optional[builtins.str] = None,
    environment_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b411e230303f93f36fe42f88f3ae59e51d4746a608fa21c8fe560bb5fe18a352(
    *,
    account: typing.Optional[builtins.str] = None,
    additional_install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    cdk_version: typing.Optional[builtins.str] = None,
    codeartifact_domain: typing.Optional[builtins.str] = None,
    codeartifact_domain_owner: typing.Optional[builtins.str] = None,
    codeartifact_repository: typing.Optional[builtins.str] = None,
    code_pipeline_source: typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer] = None,
    env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    partition: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f80411a398b3a95cafcc083fedf809e35c9f9d3c872682fa20c2c416251da930(
    *,
    config_path: typing.Optional[builtins.str] = None,
    environment_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de56c47dda07ed1c4eda1133b7152caa819140d8ea5277eaf41f2802c2c16bfd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    glue_job_properties: typing.Union[typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PythonShellJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkStreamingJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkFlexEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkFlexEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkStreamingJobProps, typing.Dict[builtins.str, typing.Any]]],
    glue_job_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4195fefbe897d7974bd882c0bba9cb93090e2d887022e38416d5ae73a33a94e6(
    *,
    glue_job_properties: typing.Union[typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PythonShellJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkStreamingJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.PySparkFlexEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkFlexEtlJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[_aws_cdk_aws_glue_alpha_ce674d29.ScalaSparkStreamingJobProps, typing.Dict[builtins.str, typing.Any]]],
    glue_job_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a14864520200528bc5a9369b081737198f4eb3e97462ea981304386c09050813(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    admins: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IPrincipal]] = None,
    alias: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    enable_key_rotation: typing.Optional[builtins.bool] = None,
    key_spec: typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeySpec] = None,
    key_usage: typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyUsage] = None,
    multi_region: typing.Optional[builtins.bool] = None,
    pending_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    rotation_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f57013032bd3f5e03e8cf2f82cc7c98b621d613c29a1e1844390ce9e164789e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    additional_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    dag_files: typing.Optional[typing.Sequence[builtins.str]] = None,
    dag_processing_logs: typing.Optional[builtins.str] = None,
    plugin_file: typing.Optional[builtins.str] = None,
    requirements_file: typing.Optional[builtins.str] = None,
    s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    scheduler_logs_level: typing.Optional[builtins.str] = None,
    task_logs_level: typing.Optional[builtins.str] = None,
    vpc_cidr: typing.Optional[builtins.str] = None,
    vpc_id: typing.Optional[builtins.str] = None,
    webserver_logs_level: typing.Optional[builtins.str] = None,
    worker_logs_level: typing.Optional[builtins.str] = None,
    name: builtins.str,
    airflow_configuration_options: typing.Any = None,
    airflow_version: typing.Optional[builtins.str] = None,
    dag_s3_path: typing.Optional[builtins.str] = None,
    endpoint_management: typing.Optional[builtins.str] = None,
    environment_class: typing.Optional[builtins.str] = None,
    execution_role_arn: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[builtins.str] = None,
    logging_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment.LoggingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    max_webservers: typing.Optional[jsii.Number] = None,
    max_workers: typing.Optional[jsii.Number] = None,
    min_webservers: typing.Optional[jsii.Number] = None,
    min_workers: typing.Optional[jsii.Number] = None,
    network_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    plugins_s3_object_version: typing.Optional[builtins.str] = None,
    plugins_s3_path: typing.Optional[builtins.str] = None,
    requirements_s3_object_version: typing.Optional[builtins.str] = None,
    requirements_s3_path: typing.Optional[builtins.str] = None,
    schedulers: typing.Optional[jsii.Number] = None,
    source_bucket_arn: typing.Optional[builtins.str] = None,
    startup_script_s3_object_version: typing.Optional[builtins.str] = None,
    startup_script_s3_path: typing.Optional[builtins.str] = None,
    tags: typing.Any = None,
    webserver_access_mode: typing.Optional[builtins.str] = None,
    weekly_maintenance_window_start: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__274336e52a6efd650b5a38d3d50c0d6df8879c749af035d91610fec06e12c9fb(
    scope: _constructs_77d1e7e8.Construct,
    environment_name: builtins.str,
    vpc_cidr: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8947f25c6bd15e846e7d13e9c335c4e41f800116e21ba100b25118382fcd659c(
    *,
    name: builtins.str,
    airflow_configuration_options: typing.Any = None,
    airflow_version: typing.Optional[builtins.str] = None,
    dag_s3_path: typing.Optional[builtins.str] = None,
    endpoint_management: typing.Optional[builtins.str] = None,
    environment_class: typing.Optional[builtins.str] = None,
    execution_role_arn: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[builtins.str] = None,
    logging_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment.LoggingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    max_webservers: typing.Optional[jsii.Number] = None,
    max_workers: typing.Optional[jsii.Number] = None,
    min_webservers: typing.Optional[jsii.Number] = None,
    min_workers: typing.Optional[jsii.Number] = None,
    network_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_mwaa_ceddda9d.CfnEnvironment.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    plugins_s3_object_version: typing.Optional[builtins.str] = None,
    plugins_s3_path: typing.Optional[builtins.str] = None,
    requirements_s3_object_version: typing.Optional[builtins.str] = None,
    requirements_s3_path: typing.Optional[builtins.str] = None,
    schedulers: typing.Optional[jsii.Number] = None,
    source_bucket_arn: typing.Optional[builtins.str] = None,
    startup_script_s3_object_version: typing.Optional[builtins.str] = None,
    startup_script_s3_path: typing.Optional[builtins.str] = None,
    tags: typing.Any = None,
    webserver_access_mode: typing.Optional[builtins.str] = None,
    weekly_maintenance_window_start: typing.Optional[builtins.str] = None,
    additional_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    dag_files: typing.Optional[typing.Sequence[builtins.str]] = None,
    dag_processing_logs: typing.Optional[builtins.str] = None,
    plugin_file: typing.Optional[builtins.str] = None,
    requirements_file: typing.Optional[builtins.str] = None,
    s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    scheduler_logs_level: typing.Optional[builtins.str] = None,
    task_logs_level: typing.Optional[builtins.str] = None,
    vpc_cidr: typing.Optional[builtins.str] = None,
    vpc_id: typing.Optional[builtins.str] = None,
    webserver_logs_level: typing.Optional[builtins.str] = None,
    worker_logs_level: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a03e72d8a80ef31dd9345bbdbea98b4abaf3d0a8612fd59523bd5d47407ab0c(
    *,
    status_lambda: _aws_cdk_aws_lambda_ceddda9d.Function,
    trigger_lambda: _aws_cdk_aws_lambda_ceddda9d.Function,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efd5392745ac5f11de7c7110e4c4c8cc4060becd6944d345396c27f2c82152b4(
    *,
    environment_id: typing.Optional[builtins.str] = None,
    prefix: typing.Optional[builtins.str] = None,
    qualifier: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__302aa44a04efd7039f32314924ad83f7735955102f1c3d6163fb082aae834c76(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    access_control: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl] = None,
    auto_delete_objects: typing.Optional[builtins.bool] = None,
    block_public_access: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess] = None,
    bucket_key_enabled: typing.Optional[builtins.bool] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    cors: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.CorsRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    encryption: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    enforce_ssl: typing.Optional[builtins.bool] = None,
    event_bridge_enabled: typing.Optional[builtins.bool] = None,
    intelligent_tiering_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    inventories: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.Inventory, typing.Dict[builtins.str, typing.Any]]]] = None,
    lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    metrics: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketMetrics, typing.Dict[builtins.str, typing.Any]]]] = None,
    minimum_tls_version: typing.Optional[jsii.Number] = None,
    notifications_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    notifications_skip_destination_validation: typing.Optional[builtins.bool] = None,
    object_lock_default_retention: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention] = None,
    object_lock_enabled: typing.Optional[builtins.bool] = None,
    object_ownership: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership] = None,
    public_read_access: typing.Optional[builtins.bool] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replication_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.ReplicationRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    server_access_logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    server_access_logs_prefix: typing.Optional[builtins.str] = None,
    target_object_key_format: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat] = None,
    transfer_acceleration: typing.Optional[builtins.bool] = None,
    transition_default_minimum_object_size: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize] = None,
    versioned: typing.Optional[builtins.bool] = None,
    website_error_document: typing.Optional[builtins.str] = None,
    website_index_document: typing.Optional[builtins.str] = None,
    website_redirect: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.RedirectTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    website_routing_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.RoutingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__576a40c037c0f9a1e8953e9d1b17a1026f7d596ac5fc54fc43e0d213874fae25(
    topic: _aws_cdk_aws_sns_ceddda9d.ITopic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c722ae4d9bf55cce29be798641c0fc2edce1bd6666919da164ce1643888b11e(
    *,
    repository_name: builtins.str,
    branch: typing.Optional[builtins.str] = None,
    source_action: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodePipelineSource] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd35d3f7ab025a947f003bfa8401771bc19ba3bee2d5d3483d2a11a867543e9b(
    *,
    max_event_age: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    on_failure: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination] = None,
    on_success: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IDestination] = None,
    retry_attempts: typing.Optional[jsii.Number] = None,
    adot_instrumentation: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.AdotInstrumentationConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    allow_public_subnet: typing.Optional[builtins.bool] = None,
    application_log_level: typing.Optional[builtins.str] = None,
    application_log_level_v2: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ApplicationLogLevel] = None,
    architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
    code_signing_config: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ICodeSigningConfig] = None,
    current_version_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.VersionOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
    dead_letter_queue_enabled: typing.Optional[builtins.bool] = None,
    dead_letter_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    description: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ephemeral_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    events: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.IEventSource]] = None,
    filesystem: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FileSystem] = None,
    function_name: typing.Optional[builtins.str] = None,
    initial_policy: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    insights_version: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LambdaInsightsVersion] = None,
    ipv6_allowed_for_dual_stack: typing.Optional[builtins.bool] = None,
    layers: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]] = None,
    log_format: typing.Optional[builtins.str] = None,
    logging_format: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LoggingFormat] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    log_retention_retry_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.LogRetentionRetryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    log_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    memory_size: typing.Optional[jsii.Number] = None,
    params_and_secrets: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ParamsAndSecretsLayerVersion] = None,
    profiling: typing.Optional[builtins.bool] = None,
    profiling_group: typing.Optional[_aws_cdk_aws_codeguruprofiler_ceddda9d.IProfilingGroup] = None,
    recursive_loop: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RecursiveLoop] = None,
    reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    runtime_management_mode: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.RuntimeManagementMode] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    snap_start: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SnapStartConf] = None,
    system_log_level: typing.Optional[builtins.str] = None,
    system_log_level_v2: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.SystemLogLevel] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    tracing: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Tracing] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    code: _aws_cdk_aws_lambda_ceddda9d.Code,
    handler: builtins.str,
    runtime: _aws_cdk_aws_lambda_ceddda9d.Runtime,
    errors_alarm_threshold: typing.Optional[jsii.Number] = None,
    errors_comparison_operator: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator] = None,
    errors_evaluation_periods: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9cf7c3474ce139a45c8e31d476f0b548b9db19082dbea4dffb9287504da5dff(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e854dfb73af2b1e5b672ba3ec79ee122851867f8bde404e9918340757b3847c(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5069a8477e1d868a51858f29afe4a12917625d0a7370bc4090fd23bf809c081c(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05acfa3cda54a17101814d614a246f97dc36de4bf27ef87f72f7aa4824dd7b35(
    *,
    additional_install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    cdk_language_command_line_arguments: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    cdk_version: typing.Optional[builtins.str] = None,
    codeartifact_domain: typing.Optional[builtins.str] = None,
    codeartifact_domain_owner: typing.Optional[builtins.str] = None,
    codeartifact_repository: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    synth_action: typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildStep] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50f57d5c758f4bb8a7385b25c9dd1756786a7af562ac0cf743837ff675065839(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    destination_flow_config: typing.Optional[typing.Union[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    flow_execution_status_check_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    flow_name: typing.Optional[builtins.str] = None,
    flow_tasks: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    source_flow_config: typing.Optional[typing.Union[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d02b2a3868910a4789cbcba2028e07a331d2da507e4b4c951dd7801d735bc0ac(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    catalog_name: typing.Optional[builtins.str] = None,
    database_name: typing.Optional[builtins.str] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    encryption_option: typing.Optional[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.EncryptionOption] = None,
    output_location: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.Location, typing.Dict[builtins.str, typing.Any]]] = None,
    parallel: typing.Optional[builtins.bool] = None,
    query_string: typing.Optional[typing.Sequence[builtins.str]] = None,
    query_string_path: typing.Optional[builtins.str] = None,
    work_group: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6be6b9ec4e805f427307a7bc1c743a3f56ffd52c0cc37a1436d75ce69e31b9f(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    create_job: typing.Optional[builtins.bool] = None,
    database_outputs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.DatabaseOutputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    data_catalog_outputs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.DataCatalogOutputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    dataset_name: typing.Optional[builtins.str] = None,
    encryption_key_arn: typing.Optional[builtins.str] = None,
    encryption_mode: typing.Optional[builtins.str] = None,
    job_name: typing.Optional[builtins.str] = None,
    job_role_arn: typing.Optional[builtins.str] = None,
    job_sample: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.JobSampleProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    job_type: typing.Optional[builtins.str] = None,
    log_subscription: typing.Optional[builtins.str] = None,
    max_capacity: typing.Optional[jsii.Number] = None,
    max_retries: typing.Optional[jsii.Number] = None,
    output_location: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.OutputLocationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    outputs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.OutputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    profile_configuration: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.ProfileConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    project_name: typing.Optional[builtins.str] = None,
    recipe: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.RecipeProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    timeout: typing.Optional[jsii.Number] = None,
    validation_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.ValidationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7ee0133925b96b521f696b544f087847c2e6916f79bbdcf76306ed73653fdb2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfe170c2325021dad043fac92cbbedf46c28aacb0956794521a87dbad31593a0(
    id: builtins.str,
    *,
    metric: _aws_cdk_aws_cloudwatch_ceddda9d.IMetric,
    comparison_operator: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cf78e5b7c077cc8d8a6b8227060c5d2b68df15e3f29e358244b75ef0b897e42(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a74bc867d821b2a380e6cc61db61d700e291094dae87fe77909819ed40f25b02(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    application_id: builtins.str,
    execution_role_arn: builtins.str,
    job_driver: typing.Mapping[builtins.str, typing.Any],
    job_execution_status_check_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    start_job_run_props: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41f4bcf520b1f5e4739a71110428c14cbff5ea45be37a68ea1fe04dbffd91d83(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2768fcf39322e444b8b05e9cfa0508e071c34b9e8a29e28fc79130506d7aeb6(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f9217104050cf03ef7cf7519808ce659edfe6c1ba00722ea6601239921cfd56(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    data_output_prefix: typing.Optional[builtins.str] = None,
    data_stream: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream] = None,
    data_stream_enabled: typing.Optional[builtins.bool] = None,
    delivery_stream_data_freshness_errors_alarm_threshold: typing.Optional[jsii.Number] = None,
    delivery_stream_data_freshness_errors_evaluation_periods: typing.Optional[jsii.Number] = None,
    firehose_delivery_stream: typing.Optional[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.DeliveryStream] = None,
    firehose_delivery_stream_props: typing.Optional[typing.Union[DeliveryStreamProps, typing.Dict[builtins.str, typing.Any]]] = None,
    kinesis_firehose_destinations_s3_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_destinations_alpha_8ee8dbdc.S3BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    s3_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__701f035bba059b01929f2b8055755baf96f72f5089bc32da86d2dc3cacf0f767(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    data_output_prefix: typing.Optional[builtins.str] = None,
    data_stream: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream] = None,
    data_stream_enabled: typing.Optional[builtins.bool] = None,
    delivery_stream_data_freshness_errors_alarm_threshold: typing.Optional[jsii.Number] = None,
    delivery_stream_data_freshness_errors_evaluation_periods: typing.Optional[jsii.Number] = None,
    firehose_delivery_stream: typing.Optional[_aws_cdk_aws_kinesisfirehose_alpha_30daaf29.DeliveryStream] = None,
    firehose_delivery_stream_props: typing.Optional[typing.Union[DeliveryStreamProps, typing.Dict[builtins.str, typing.Any]]] = None,
    kinesis_firehose_destinations_s3_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_destinations_alpha_8ee8dbdc.S3BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    s3_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36c864b97313236b09b597808a1574a4f4d21024bac872f4e182edbd9a3d0175(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    crawler_allow_failure: typing.Optional[builtins.bool] = None,
    crawler_name: typing.Optional[builtins.str] = None,
    crawler_props: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawlerProps, typing.Dict[builtins.str, typing.Any]]] = None,
    crawler_role: typing.Optional[builtins.str] = None,
    database_name: typing.Optional[builtins.str] = None,
    job_name: typing.Optional[builtins.str] = None,
    job_props: typing.Optional[typing.Union[GlueFactoryProps, typing.Dict[builtins.str, typing.Any]]] = None,
    job_run_args: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_retry_backoff_rate: typing.Optional[jsii.Number] = None,
    state_machine_retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    state_machine_retry_max_attempts: typing.Optional[jsii.Number] = None,
    targets: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.TargetsProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22752f7fca368ed1e29dd71501fbd74daab00450e10e80bb5c02b1233ef9c8f5(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    mwaa_environment_name: builtins.str,
    dag_path: typing.Optional[builtins.str] = None,
    dags: typing.Optional[typing.Sequence[builtins.str]] = None,
    status_check_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__defbc9333f2b8b3e2d55373f9b0155e5f6e83609e9153dc24f619d747ca4f133(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    redshift_cluster_identifier: builtins.str,
    sql_statements: typing.Sequence[builtins.str],
    database_name: typing.Optional[builtins.str] = None,
    database_user: typing.Optional[builtins.str] = None,
    polling_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faeff4d3ae690cf668837c5bb7641744355445bfe3e6990816e841afad5a577f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket: typing.Union[_aws_cdk_aws_s3_ceddda9d.IBucket, typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]],
    event_names: typing.Sequence[builtins.str],
    key_prefix: typing.Optional[typing.Union[builtins.str, typing.Sequence[builtins.str]]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b66fa30f9df5c5a39526206778107c9f4992a0d357e41d5469d45e647a206a90(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    bucket: typing.Union[_aws_cdk_aws_s3_ceddda9d.IBucket, typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]],
    event_names: typing.Sequence[builtins.str],
    key_prefix: typing.Optional[typing.Union[builtins.str, typing.Sequence[builtins.str]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5be1a85b67aa2deae08f66dcc56eb002282a0b357ba91df9339c1c9e2cb7401(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    batch_size: typing.Optional[jsii.Number] = None,
    dlq_enabled: typing.Optional[builtins.bool] = None,
    lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    lambda_function_props: typing.Optional[typing.Union[SqsToLambdaStageFunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    max_batching_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    max_receive_count: typing.Optional[jsii.Number] = None,
    message_group_id: typing.Optional[builtins.str] = None,
    sqs_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
    sqs_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ea408fc3fa64f721e1e8e8f5dba2b0b6340914a77963785a7642a5943b0a04a(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    batch_size: typing.Optional[jsii.Number] = None,
    dlq_enabled: typing.Optional[builtins.bool] = None,
    lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    lambda_function_props: typing.Optional[typing.Union[SqsToLambdaStageFunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    max_batching_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    max_receive_count: typing.Optional[jsii.Number] = None,
    message_group_id: typing.Optional[builtins.str] = None,
    sqs_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
    sqs_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9ccc4da0d6d8eb11cda39b2839889ebd93235f90bbfbdd93a92a3f816c9fd60(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75fdc83ac05ea2b4078c2c89fa4beb028f1353a28c899b42364d275a692f3594(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    destination_flow_config: typing.Optional[typing.Union[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    flow_execution_status_check_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    flow_name: typing.Optional[builtins.str] = None,
    flow_tasks: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    source_flow_config: typing.Optional[typing.Union[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51d1732123dc8ece0c4c19240b905f56cb50227d150f624d8b798a82b65cbe29(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    catalog_name: typing.Optional[builtins.str] = None,
    database_name: typing.Optional[builtins.str] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    encryption_option: typing.Optional[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.EncryptionOption] = None,
    output_location: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.Location, typing.Dict[builtins.str, typing.Any]]] = None,
    parallel: typing.Optional[builtins.bool] = None,
    query_string: typing.Optional[typing.Sequence[builtins.str]] = None,
    query_string_path: typing.Optional[builtins.str] = None,
    work_group: typing.Optional[builtins.str] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9214d4641d831e11d83d601cf5e13ef25bd3d55977b689c3cefd7aaa9fb0fb5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    create_job: typing.Optional[builtins.bool] = None,
    database_outputs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.DatabaseOutputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    data_catalog_outputs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.DataCatalogOutputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    dataset_name: typing.Optional[builtins.str] = None,
    encryption_key_arn: typing.Optional[builtins.str] = None,
    encryption_mode: typing.Optional[builtins.str] = None,
    job_name: typing.Optional[builtins.str] = None,
    job_role_arn: typing.Optional[builtins.str] = None,
    job_sample: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.JobSampleProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    job_type: typing.Optional[builtins.str] = None,
    log_subscription: typing.Optional[builtins.str] = None,
    max_capacity: typing.Optional[jsii.Number] = None,
    max_retries: typing.Optional[jsii.Number] = None,
    output_location: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.OutputLocationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    outputs: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.OutputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    profile_configuration: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.ProfileConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    project_name: typing.Optional[builtins.str] = None,
    recipe: typing.Optional[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.RecipeProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    timeout: typing.Optional[jsii.Number] = None,
    validation_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_databrew_ceddda9d.CfnJob.ValidationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cbec3de2f6cc9565e6ad8777b9c24ec8039d2679d0b58ae0f8a78bb7c12d9c3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application_id: builtins.str,
    execution_role_arn: builtins.str,
    job_driver: typing.Mapping[builtins.str, typing.Any],
    job_execution_status_check_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    start_job_run_props: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ddc56c43fee5e5dc6737d945cf18cb6800a5b74340125036ae173083ba761f2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    crawler_allow_failure: typing.Optional[builtins.bool] = None,
    crawler_name: typing.Optional[builtins.str] = None,
    crawler_props: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawlerProps, typing.Dict[builtins.str, typing.Any]]] = None,
    crawler_role: typing.Optional[builtins.str] = None,
    database_name: typing.Optional[builtins.str] = None,
    job_name: typing.Optional[builtins.str] = None,
    job_props: typing.Optional[typing.Union[GlueFactoryProps, typing.Dict[builtins.str, typing.Any]]] = None,
    job_run_args: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_retry_backoff_rate: typing.Optional[jsii.Number] = None,
    state_machine_retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    state_machine_retry_max_attempts: typing.Optional[jsii.Number] = None,
    targets: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.TargetsProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f0213661be18de8fe8fd12f50692a50182df1c8f22c50ad38963d7b78d944a0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    mwaa_environment_name: builtins.str,
    dag_path: typing.Optional[builtins.str] = None,
    dags: typing.Optional[typing.Sequence[builtins.str]] = None,
    status_check_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e1a2de894e37c9f2da01cc73a49a2d2fe9ec89a86ba3d42531baaa26002a1a7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    redshift_cluster_identifier: builtins.str,
    sql_statements: typing.Sequence[builtins.str],
    database_name: typing.Optional[builtins.str] = None,
    database_user: typing.Optional[builtins.str] = None,
    polling_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    additional_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    definition: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]] = None,
    definition_file: typing.Optional[builtins.str] = None,
    state_machine_failed_executions_alarm_evaluation_periods: typing.Optional[jsii.Number] = None,
    state_machine_failed_executions_alarm_threshold: typing.Optional[jsii.Number] = None,
    state_machine_input: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1f6169c1775457f18465db8ac58b6e948ab3cee732db9fb369eb57e96e8b7ef(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    disable_default_topic_policy: typing.Optional[builtins.bool] = None,
    filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_ceddda9d.SubscriptionFilter]] = None,
    raw_message_delivery: typing.Optional[builtins.bool] = None,
    sns_dlq_enabled: typing.Optional[builtins.bool] = None,
    sns_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    sns_topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
    batch_size: typing.Optional[jsii.Number] = None,
    dlq_enabled: typing.Optional[builtins.bool] = None,
    lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    lambda_function_props: typing.Optional[typing.Union[SqsToLambdaStageFunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    max_batching_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    max_receive_count: typing.Optional[jsii.Number] = None,
    message_group_id: typing.Optional[builtins.str] = None,
    sqs_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
    sqs_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1ced712cbd6acd872556813dd7192431ee7539b2ab066fa0aafd950cc7268b0(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    alarms_enabled: typing.Optional[builtins.bool] = None,
    batch_size: typing.Optional[jsii.Number] = None,
    dlq_enabled: typing.Optional[builtins.bool] = None,
    lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    lambda_function_props: typing.Optional[typing.Union[SqsToLambdaStageFunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    max_batching_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    max_receive_count: typing.Optional[jsii.Number] = None,
    message_group_id: typing.Optional[builtins.str] = None,
    sqs_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
    sqs_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    disable_default_topic_policy: typing.Optional[builtins.bool] = None,
    filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_ceddda9d.SubscriptionFilter]] = None,
    raw_message_delivery: typing.Optional[builtins.bool] = None,
    sns_dlq_enabled: typing.Optional[builtins.bool] = None,
    sns_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    sns_topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
