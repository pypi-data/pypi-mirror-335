"""
Type annotations for gamelift service literal definitions.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_gamelift/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from types_boto3_gamelift.literals import AcceptanceTypeType

    data: AcceptanceTypeType = "ACCEPT"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "AcceptanceTypeType",
    "BackfillModeType",
    "BalancingStrategyType",
    "BuildStatusType",
    "CertificateTypeType",
    "ComparisonOperatorTypeType",
    "ComputeStatusType",
    "ComputeTypeType",
    "ContainerDependencyConditionType",
    "ContainerFleetBillingTypeType",
    "ContainerFleetLocationStatusType",
    "ContainerFleetRemoveAttributeType",
    "ContainerFleetStatusType",
    "ContainerGroupDefinitionStatusType",
    "ContainerGroupTypeType",
    "ContainerMountPointAccessLevelType",
    "ContainerOperatingSystemType",
    "DeploymentImpairmentStrategyType",
    "DeploymentProtectionStrategyType",
    "DeploymentStatusType",
    "DescribeFleetAttributesPaginatorName",
    "DescribeFleetCapacityPaginatorName",
    "DescribeFleetEventsPaginatorName",
    "DescribeFleetUtilizationPaginatorName",
    "DescribeGameServerInstancesPaginatorName",
    "DescribeGameSessionDetailsPaginatorName",
    "DescribeGameSessionQueuesPaginatorName",
    "DescribeGameSessionsPaginatorName",
    "DescribeInstancesPaginatorName",
    "DescribeMatchmakingConfigurationsPaginatorName",
    "DescribeMatchmakingRuleSetsPaginatorName",
    "DescribePlayerSessionsPaginatorName",
    "DescribeScalingPoliciesPaginatorName",
    "EC2InstanceTypeType",
    "EventCodeType",
    "FilterInstanceStatusType",
    "FleetActionType",
    "FleetStatusType",
    "FleetTypeType",
    "FlexMatchModeType",
    "GameLiftServiceName",
    "GameServerClaimStatusType",
    "GameServerGroupActionType",
    "GameServerGroupDeleteOptionType",
    "GameServerGroupInstanceTypeType",
    "GameServerGroupStatusType",
    "GameServerHealthCheckType",
    "GameServerInstanceStatusType",
    "GameServerProtectionPolicyType",
    "GameServerUtilizationStatusType",
    "GameSessionPlacementStateType",
    "GameSessionStatusReasonType",
    "GameSessionStatusType",
    "InstanceRoleCredentialsProviderType",
    "InstanceStatusType",
    "IpProtocolType",
    "ListAliasesPaginatorName",
    "ListBuildsPaginatorName",
    "ListComputeInputStatusType",
    "ListComputePaginatorName",
    "ListContainerFleetsPaginatorName",
    "ListContainerGroupDefinitionVersionsPaginatorName",
    "ListContainerGroupDefinitionsPaginatorName",
    "ListFleetDeploymentsPaginatorName",
    "ListFleetsPaginatorName",
    "ListGameServerGroupsPaginatorName",
    "ListGameServersPaginatorName",
    "ListLocationsPaginatorName",
    "ListScriptsPaginatorName",
    "LocationFilterType",
    "LocationUpdateStatusType",
    "LogDestinationType",
    "MatchmakingConfigurationStatusType",
    "MetricNameType",
    "OperatingSystemType",
    "PaginatorName",
    "PlacementFallbackStrategyType",
    "PlayerSessionCreationPolicyType",
    "PlayerSessionStatusType",
    "PolicyTypeType",
    "PriorityTypeType",
    "ProtectionPolicyType",
    "RegionName",
    "ResourceServiceName",
    "RoutingStrategyTypeType",
    "ScalingAdjustmentTypeType",
    "ScalingStatusTypeType",
    "SearchGameSessionsPaginatorName",
    "ServiceName",
    "SortOrderType",
    "TerminationModeType",
)


AcceptanceTypeType = Literal["ACCEPT", "REJECT"]
BackfillModeType = Literal["AUTOMATIC", "MANUAL"]
BalancingStrategyType = Literal["ON_DEMAND_ONLY", "SPOT_ONLY", "SPOT_PREFERRED"]
BuildStatusType = Literal["FAILED", "INITIALIZED", "READY"]
CertificateTypeType = Literal["DISABLED", "GENERATED"]
ComparisonOperatorTypeType = Literal[
    "GreaterThanOrEqualToThreshold",
    "GreaterThanThreshold",
    "LessThanOrEqualToThreshold",
    "LessThanThreshold",
]
ComputeStatusType = Literal["ACTIVE", "IMPAIRED", "PENDING", "TERMINATING"]
ComputeTypeType = Literal["ANYWHERE", "EC2"]
ContainerDependencyConditionType = Literal["COMPLETE", "HEALTHY", "START", "SUCCESS"]
ContainerFleetBillingTypeType = Literal["ON_DEMAND", "SPOT"]
ContainerFleetLocationStatusType = Literal[
    "ACTIVATING", "ACTIVE", "CREATED", "CREATING", "DELETING", "PENDING", "UPDATING"
]
ContainerFleetRemoveAttributeType = Literal["PER_INSTANCE_CONTAINER_GROUP_DEFINITION"]
ContainerFleetStatusType = Literal[
    "ACTIVATING", "ACTIVE", "CREATED", "CREATING", "DELETING", "PENDING", "UPDATING"
]
ContainerGroupDefinitionStatusType = Literal["COPYING", "FAILED", "READY"]
ContainerGroupTypeType = Literal["GAME_SERVER", "PER_INSTANCE"]
ContainerMountPointAccessLevelType = Literal["READ_AND_WRITE", "READ_ONLY"]
ContainerOperatingSystemType = Literal["AMAZON_LINUX_2023"]
DeploymentImpairmentStrategyType = Literal["MAINTAIN", "ROLLBACK"]
DeploymentProtectionStrategyType = Literal["IGNORE_PROTECTION", "WITH_PROTECTION"]
DeploymentStatusType = Literal[
    "CANCELLED",
    "COMPLETE",
    "IMPAIRED",
    "IN_PROGRESS",
    "PENDING",
    "ROLLBACK_COMPLETE",
    "ROLLBACK_IN_PROGRESS",
]
DescribeFleetAttributesPaginatorName = Literal["describe_fleet_attributes"]
DescribeFleetCapacityPaginatorName = Literal["describe_fleet_capacity"]
DescribeFleetEventsPaginatorName = Literal["describe_fleet_events"]
DescribeFleetUtilizationPaginatorName = Literal["describe_fleet_utilization"]
DescribeGameServerInstancesPaginatorName = Literal["describe_game_server_instances"]
DescribeGameSessionDetailsPaginatorName = Literal["describe_game_session_details"]
DescribeGameSessionQueuesPaginatorName = Literal["describe_game_session_queues"]
DescribeGameSessionsPaginatorName = Literal["describe_game_sessions"]
DescribeInstancesPaginatorName = Literal["describe_instances"]
DescribeMatchmakingConfigurationsPaginatorName = Literal["describe_matchmaking_configurations"]
DescribeMatchmakingRuleSetsPaginatorName = Literal["describe_matchmaking_rule_sets"]
DescribePlayerSessionsPaginatorName = Literal["describe_player_sessions"]
DescribeScalingPoliciesPaginatorName = Literal["describe_scaling_policies"]
EC2InstanceTypeType = Literal[
    "c3.2xlarge",
    "c3.4xlarge",
    "c3.8xlarge",
    "c3.large",
    "c3.xlarge",
    "c4.2xlarge",
    "c4.4xlarge",
    "c4.8xlarge",
    "c4.large",
    "c4.xlarge",
    "c5.12xlarge",
    "c5.18xlarge",
    "c5.24xlarge",
    "c5.2xlarge",
    "c5.4xlarge",
    "c5.9xlarge",
    "c5.large",
    "c5.xlarge",
    "c5a.12xlarge",
    "c5a.16xlarge",
    "c5a.24xlarge",
    "c5a.2xlarge",
    "c5a.4xlarge",
    "c5a.8xlarge",
    "c5a.large",
    "c5a.xlarge",
    "c5d.12xlarge",
    "c5d.18xlarge",
    "c5d.24xlarge",
    "c5d.2xlarge",
    "c5d.4xlarge",
    "c5d.9xlarge",
    "c5d.large",
    "c5d.xlarge",
    "c6a.12xlarge",
    "c6a.16xlarge",
    "c6a.24xlarge",
    "c6a.2xlarge",
    "c6a.4xlarge",
    "c6a.8xlarge",
    "c6a.large",
    "c6a.xlarge",
    "c6g.12xlarge",
    "c6g.16xlarge",
    "c6g.2xlarge",
    "c6g.4xlarge",
    "c6g.8xlarge",
    "c6g.large",
    "c6g.medium",
    "c6g.xlarge",
    "c6gn.12xlarge",
    "c6gn.16xlarge",
    "c6gn.2xlarge",
    "c6gn.4xlarge",
    "c6gn.8xlarge",
    "c6gn.large",
    "c6gn.medium",
    "c6gn.xlarge",
    "c6i.12xlarge",
    "c6i.16xlarge",
    "c6i.24xlarge",
    "c6i.2xlarge",
    "c6i.4xlarge",
    "c6i.8xlarge",
    "c6i.large",
    "c6i.xlarge",
    "c7g.12xlarge",
    "c7g.16xlarge",
    "c7g.2xlarge",
    "c7g.4xlarge",
    "c7g.8xlarge",
    "c7g.large",
    "c7g.medium",
    "c7g.xlarge",
    "g5g.16xlarge",
    "g5g.2xlarge",
    "g5g.4xlarge",
    "g5g.8xlarge",
    "g5g.xlarge",
    "m3.2xlarge",
    "m3.large",
    "m3.medium",
    "m3.xlarge",
    "m4.10xlarge",
    "m4.2xlarge",
    "m4.4xlarge",
    "m4.large",
    "m4.xlarge",
    "m5.12xlarge",
    "m5.16xlarge",
    "m5.24xlarge",
    "m5.2xlarge",
    "m5.4xlarge",
    "m5.8xlarge",
    "m5.large",
    "m5.xlarge",
    "m5a.12xlarge",
    "m5a.16xlarge",
    "m5a.24xlarge",
    "m5a.2xlarge",
    "m5a.4xlarge",
    "m5a.8xlarge",
    "m5a.large",
    "m5a.xlarge",
    "m6g.12xlarge",
    "m6g.16xlarge",
    "m6g.2xlarge",
    "m6g.4xlarge",
    "m6g.8xlarge",
    "m6g.large",
    "m6g.medium",
    "m6g.xlarge",
    "m7g.12xlarge",
    "m7g.16xlarge",
    "m7g.2xlarge",
    "m7g.4xlarge",
    "m7g.8xlarge",
    "m7g.large",
    "m7g.medium",
    "m7g.xlarge",
    "r3.2xlarge",
    "r3.4xlarge",
    "r3.8xlarge",
    "r3.large",
    "r3.xlarge",
    "r4.16xlarge",
    "r4.2xlarge",
    "r4.4xlarge",
    "r4.8xlarge",
    "r4.large",
    "r4.xlarge",
    "r5.12xlarge",
    "r5.16xlarge",
    "r5.24xlarge",
    "r5.2xlarge",
    "r5.4xlarge",
    "r5.8xlarge",
    "r5.large",
    "r5.xlarge",
    "r5a.12xlarge",
    "r5a.16xlarge",
    "r5a.24xlarge",
    "r5a.2xlarge",
    "r5a.4xlarge",
    "r5a.8xlarge",
    "r5a.large",
    "r5a.xlarge",
    "r5d.12xlarge",
    "r5d.16xlarge",
    "r5d.24xlarge",
    "r5d.2xlarge",
    "r5d.4xlarge",
    "r5d.8xlarge",
    "r5d.large",
    "r5d.xlarge",
    "r6g.12xlarge",
    "r6g.16xlarge",
    "r6g.2xlarge",
    "r6g.4xlarge",
    "r6g.8xlarge",
    "r6g.large",
    "r6g.medium",
    "r6g.xlarge",
    "r7g.12xlarge",
    "r7g.16xlarge",
    "r7g.2xlarge",
    "r7g.4xlarge",
    "r7g.8xlarge",
    "r7g.large",
    "r7g.medium",
    "r7g.xlarge",
    "t2.large",
    "t2.medium",
    "t2.micro",
    "t2.small",
]
EventCodeType = Literal[
    "COMPUTE_LOG_UPLOAD_FAILED",
    "FLEET_ACTIVATION_FAILED",
    "FLEET_ACTIVATION_FAILED_NO_INSTANCES",
    "FLEET_BINARY_DOWNLOAD_FAILED",
    "FLEET_CREATED",
    "FLEET_CREATION_COMPLETED_INSTALLER",
    "FLEET_CREATION_EXTRACTING_BUILD",
    "FLEET_CREATION_FAILED_INSTALLER",
    "FLEET_CREATION_RUNNING_INSTALLER",
    "FLEET_CREATION_VALIDATING_RUNTIME_CONFIG",
    "FLEET_DELETED",
    "FLEET_INITIALIZATION_FAILED",
    "FLEET_NEW_GAME_SESSION_PROTECTION_POLICY_UPDATED",
    "FLEET_SCALING_EVENT",
    "FLEET_STATE_ACTIVATING",
    "FLEET_STATE_ACTIVE",
    "FLEET_STATE_BUILDING",
    "FLEET_STATE_CREATED",
    "FLEET_STATE_CREATING",
    "FLEET_STATE_DOWNLOADING",
    "FLEET_STATE_ERROR",
    "FLEET_STATE_PENDING",
    "FLEET_STATE_UPDATING",
    "FLEET_STATE_VALIDATING",
    "FLEET_VALIDATION_EXECUTABLE_RUNTIME_FAILURE",
    "FLEET_VALIDATION_LAUNCH_PATH_NOT_FOUND",
    "FLEET_VALIDATION_TIMED_OUT",
    "FLEET_VPC_PEERING_DELETED",
    "FLEET_VPC_PEERING_FAILED",
    "FLEET_VPC_PEERING_SUCCEEDED",
    "GAME_SERVER_CONTAINER_GROUP_CRASHED",
    "GAME_SERVER_CONTAINER_GROUP_REPLACED_UNHEALTHY",
    "GAME_SESSION_ACTIVATION_TIMEOUT",
    "GENERIC_EVENT",
    "INSTANCE_INTERRUPTED",
    "INSTANCE_RECYCLED",
    "INSTANCE_REPLACED_UNHEALTHY",
    "LOCATION_STATE_ACTIVATING",
    "LOCATION_STATE_ACTIVE",
    "LOCATION_STATE_CREATED",
    "LOCATION_STATE_CREATING",
    "LOCATION_STATE_DELETED",
    "LOCATION_STATE_DELETING",
    "LOCATION_STATE_ERROR",
    "LOCATION_STATE_PENDING",
    "LOCATION_STATE_UPDATING",
    "PER_INSTANCE_CONTAINER_GROUP_CRASHED",
    "SERVER_PROCESS_CRASHED",
    "SERVER_PROCESS_FORCE_TERMINATED",
    "SERVER_PROCESS_INVALID_PATH",
    "SERVER_PROCESS_MISCONFIGURED_CONTAINER_PORT",
    "SERVER_PROCESS_PROCESS_EXIT_TIMEOUT",
    "SERVER_PROCESS_PROCESS_READY_TIMEOUT",
    "SERVER_PROCESS_SDK_INITIALIZATION_FAILED",
    "SERVER_PROCESS_SDK_INITIALIZATION_TIMEOUT",
    "SERVER_PROCESS_TERMINATED_UNHEALTHY",
]
FilterInstanceStatusType = Literal["ACTIVE", "DRAINING"]
FleetActionType = Literal["AUTO_SCALING"]
FleetStatusType = Literal[
    "ACTIVATING",
    "ACTIVE",
    "BUILDING",
    "DELETING",
    "DOWNLOADING",
    "ERROR",
    "NEW",
    "NOT_FOUND",
    "TERMINATED",
    "VALIDATING",
]
FleetTypeType = Literal["ON_DEMAND", "SPOT"]
FlexMatchModeType = Literal["STANDALONE", "WITH_QUEUE"]
GameServerClaimStatusType = Literal["CLAIMED"]
GameServerGroupActionType = Literal["REPLACE_INSTANCE_TYPES"]
GameServerGroupDeleteOptionType = Literal["FORCE_DELETE", "RETAIN", "SAFE_DELETE"]
GameServerGroupInstanceTypeType = Literal[
    "c4.2xlarge",
    "c4.4xlarge",
    "c4.8xlarge",
    "c4.large",
    "c4.xlarge",
    "c5.12xlarge",
    "c5.18xlarge",
    "c5.24xlarge",
    "c5.2xlarge",
    "c5.4xlarge",
    "c5.9xlarge",
    "c5.large",
    "c5.xlarge",
    "c5a.12xlarge",
    "c5a.16xlarge",
    "c5a.24xlarge",
    "c5a.2xlarge",
    "c5a.4xlarge",
    "c5a.8xlarge",
    "c5a.large",
    "c5a.xlarge",
    "c6g.12xlarge",
    "c6g.16xlarge",
    "c6g.2xlarge",
    "c6g.4xlarge",
    "c6g.8xlarge",
    "c6g.large",
    "c6g.medium",
    "c6g.xlarge",
    "m4.10xlarge",
    "m4.2xlarge",
    "m4.4xlarge",
    "m4.large",
    "m4.xlarge",
    "m5.12xlarge",
    "m5.16xlarge",
    "m5.24xlarge",
    "m5.2xlarge",
    "m5.4xlarge",
    "m5.8xlarge",
    "m5.large",
    "m5.xlarge",
    "m5a.12xlarge",
    "m5a.16xlarge",
    "m5a.24xlarge",
    "m5a.2xlarge",
    "m5a.4xlarge",
    "m5a.8xlarge",
    "m5a.large",
    "m5a.xlarge",
    "m6g.12xlarge",
    "m6g.16xlarge",
    "m6g.2xlarge",
    "m6g.4xlarge",
    "m6g.8xlarge",
    "m6g.large",
    "m6g.medium",
    "m6g.xlarge",
    "r4.16xlarge",
    "r4.2xlarge",
    "r4.4xlarge",
    "r4.8xlarge",
    "r4.large",
    "r4.xlarge",
    "r5.12xlarge",
    "r5.16xlarge",
    "r5.24xlarge",
    "r5.2xlarge",
    "r5.4xlarge",
    "r5.8xlarge",
    "r5.large",
    "r5.xlarge",
    "r5a.12xlarge",
    "r5a.16xlarge",
    "r5a.24xlarge",
    "r5a.2xlarge",
    "r5a.4xlarge",
    "r5a.8xlarge",
    "r5a.large",
    "r5a.xlarge",
    "r6g.12xlarge",
    "r6g.16xlarge",
    "r6g.2xlarge",
    "r6g.4xlarge",
    "r6g.8xlarge",
    "r6g.large",
    "r6g.medium",
    "r6g.xlarge",
]
GameServerGroupStatusType = Literal[
    "ACTIVATING", "ACTIVE", "DELETED", "DELETE_SCHEDULED", "DELETING", "ERROR", "NEW"
]
GameServerHealthCheckType = Literal["HEALTHY"]
GameServerInstanceStatusType = Literal["ACTIVE", "DRAINING", "SPOT_TERMINATING"]
GameServerProtectionPolicyType = Literal["FULL_PROTECTION", "NO_PROTECTION"]
GameServerUtilizationStatusType = Literal["AVAILABLE", "UTILIZED"]
GameSessionPlacementStateType = Literal["CANCELLED", "FAILED", "FULFILLED", "PENDING", "TIMED_OUT"]
GameSessionStatusReasonType = Literal[
    "FORCE_TERMINATED", "INTERRUPTED", "TRIGGERED_ON_PROCESS_TERMINATE"
]
GameSessionStatusType = Literal["ACTIVATING", "ACTIVE", "ERROR", "TERMINATED", "TERMINATING"]
InstanceRoleCredentialsProviderType = Literal["SHARED_CREDENTIAL_FILE"]
InstanceStatusType = Literal["ACTIVE", "PENDING", "TERMINATING"]
IpProtocolType = Literal["TCP", "UDP"]
ListAliasesPaginatorName = Literal["list_aliases"]
ListBuildsPaginatorName = Literal["list_builds"]
ListComputeInputStatusType = Literal["ACTIVE", "IMPAIRED"]
ListComputePaginatorName = Literal["list_compute"]
ListContainerFleetsPaginatorName = Literal["list_container_fleets"]
ListContainerGroupDefinitionVersionsPaginatorName = Literal[
    "list_container_group_definition_versions"
]
ListContainerGroupDefinitionsPaginatorName = Literal["list_container_group_definitions"]
ListFleetDeploymentsPaginatorName = Literal["list_fleet_deployments"]
ListFleetsPaginatorName = Literal["list_fleets"]
ListGameServerGroupsPaginatorName = Literal["list_game_server_groups"]
ListGameServersPaginatorName = Literal["list_game_servers"]
ListLocationsPaginatorName = Literal["list_locations"]
ListScriptsPaginatorName = Literal["list_scripts"]
LocationFilterType = Literal["AWS", "CUSTOM"]
LocationUpdateStatusType = Literal["PENDING_UPDATE"]
LogDestinationType = Literal["CLOUDWATCH", "NONE", "S3"]
MatchmakingConfigurationStatusType = Literal[
    "CANCELLED",
    "COMPLETED",
    "FAILED",
    "PLACING",
    "QUEUED",
    "REQUIRES_ACCEPTANCE",
    "SEARCHING",
    "TIMED_OUT",
]
MetricNameType = Literal[
    "ActivatingGameSessions",
    "ActiveGameSessions",
    "ActiveInstances",
    "AvailableGameSessions",
    "AvailablePlayerSessions",
    "ConcurrentActivatableGameSessions",
    "CurrentPlayerSessions",
    "IdleInstances",
    "PercentAvailableGameSessions",
    "PercentIdleInstances",
    "QueueDepth",
    "WaitTime",
]
OperatingSystemType = Literal[
    "AMAZON_LINUX", "AMAZON_LINUX_2", "AMAZON_LINUX_2023", "WINDOWS_2012", "WINDOWS_2016"
]
PlacementFallbackStrategyType = Literal["DEFAULT_AFTER_SINGLE_PASS", "NONE"]
PlayerSessionCreationPolicyType = Literal["ACCEPT_ALL", "DENY_ALL"]
PlayerSessionStatusType = Literal["ACTIVE", "COMPLETED", "RESERVED", "TIMEDOUT"]
PolicyTypeType = Literal["RuleBased", "TargetBased"]
PriorityTypeType = Literal["COST", "DESTINATION", "LATENCY", "LOCATION"]
ProtectionPolicyType = Literal["FullProtection", "NoProtection"]
RoutingStrategyTypeType = Literal["SIMPLE", "TERMINAL"]
ScalingAdjustmentTypeType = Literal["ChangeInCapacity", "ExactCapacity", "PercentChangeInCapacity"]
ScalingStatusTypeType = Literal[
    "ACTIVE", "DELETED", "DELETE_REQUESTED", "DELETING", "ERROR", "UPDATE_REQUESTED", "UPDATING"
]
SearchGameSessionsPaginatorName = Literal["search_game_sessions"]
SortOrderType = Literal["ASCENDING", "DESCENDING"]
TerminationModeType = Literal["FORCE_TERMINATE", "TRIGGER_ON_PROCESS_TERMINATE"]
GameLiftServiceName = Literal["gamelift"]
ServiceName = Literal[
    "accessanalyzer",
    "account",
    "acm",
    "acm-pca",
    "amp",
    "amplify",
    "amplifybackend",
    "amplifyuibuilder",
    "apigateway",
    "apigatewaymanagementapi",
    "apigatewayv2",
    "appconfig",
    "appconfigdata",
    "appfabric",
    "appflow",
    "appintegrations",
    "application-autoscaling",
    "application-insights",
    "application-signals",
    "applicationcostprofiler",
    "appmesh",
    "apprunner",
    "appstream",
    "appsync",
    "apptest",
    "arc-zonal-shift",
    "artifact",
    "athena",
    "auditmanager",
    "autoscaling",
    "autoscaling-plans",
    "b2bi",
    "backup",
    "backup-gateway",
    "backupsearch",
    "batch",
    "bcm-data-exports",
    "bcm-pricing-calculator",
    "bedrock",
    "bedrock-agent",
    "bedrock-agent-runtime",
    "bedrock-data-automation",
    "bedrock-data-automation-runtime",
    "bedrock-runtime",
    "billing",
    "billingconductor",
    "braket",
    "budgets",
    "ce",
    "chatbot",
    "chime",
    "chime-sdk-identity",
    "chime-sdk-media-pipelines",
    "chime-sdk-meetings",
    "chime-sdk-messaging",
    "chime-sdk-voice",
    "cleanrooms",
    "cleanroomsml",
    "cloud9",
    "cloudcontrol",
    "clouddirectory",
    "cloudformation",
    "cloudfront",
    "cloudfront-keyvaluestore",
    "cloudhsm",
    "cloudhsmv2",
    "cloudsearch",
    "cloudsearchdomain",
    "cloudtrail",
    "cloudtrail-data",
    "cloudwatch",
    "codeartifact",
    "codebuild",
    "codecatalyst",
    "codecommit",
    "codeconnections",
    "codedeploy",
    "codeguru-reviewer",
    "codeguru-security",
    "codeguruprofiler",
    "codepipeline",
    "codestar-connections",
    "codestar-notifications",
    "cognito-identity",
    "cognito-idp",
    "cognito-sync",
    "comprehend",
    "comprehendmedical",
    "compute-optimizer",
    "config",
    "connect",
    "connect-contact-lens",
    "connectcampaigns",
    "connectcampaignsv2",
    "connectcases",
    "connectparticipant",
    "controlcatalog",
    "controltower",
    "cost-optimization-hub",
    "cur",
    "customer-profiles",
    "databrew",
    "dataexchange",
    "datapipeline",
    "datasync",
    "datazone",
    "dax",
    "deadline",
    "detective",
    "devicefarm",
    "devops-guru",
    "directconnect",
    "discovery",
    "dlm",
    "dms",
    "docdb",
    "docdb-elastic",
    "drs",
    "ds",
    "ds-data",
    "dsql",
    "dynamodb",
    "dynamodbstreams",
    "ebs",
    "ec2",
    "ec2-instance-connect",
    "ecr",
    "ecr-public",
    "ecs",
    "efs",
    "eks",
    "eks-auth",
    "elasticache",
    "elasticbeanstalk",
    "elastictranscoder",
    "elb",
    "elbv2",
    "emr",
    "emr-containers",
    "emr-serverless",
    "entityresolution",
    "es",
    "events",
    "evidently",
    "finspace",
    "finspace-data",
    "firehose",
    "fis",
    "fms",
    "forecast",
    "forecastquery",
    "frauddetector",
    "freetier",
    "fsx",
    "gamelift",
    "gameliftstreams",
    "geo-maps",
    "geo-places",
    "geo-routes",
    "glacier",
    "globalaccelerator",
    "glue",
    "grafana",
    "greengrass",
    "greengrassv2",
    "groundstation",
    "guardduty",
    "health",
    "healthlake",
    "iam",
    "identitystore",
    "imagebuilder",
    "importexport",
    "inspector",
    "inspector-scan",
    "inspector2",
    "internetmonitor",
    "invoicing",
    "iot",
    "iot-data",
    "iot-jobs-data",
    "iot-managed-integrations",
    "iotanalytics",
    "iotdeviceadvisor",
    "iotevents",
    "iotevents-data",
    "iotfleethub",
    "iotfleetwise",
    "iotsecuretunneling",
    "iotsitewise",
    "iotthingsgraph",
    "iottwinmaker",
    "iotwireless",
    "ivs",
    "ivs-realtime",
    "ivschat",
    "kafka",
    "kafkaconnect",
    "kendra",
    "kendra-ranking",
    "keyspaces",
    "kinesis",
    "kinesis-video-archived-media",
    "kinesis-video-media",
    "kinesis-video-signaling",
    "kinesis-video-webrtc-storage",
    "kinesisanalytics",
    "kinesisanalyticsv2",
    "kinesisvideo",
    "kms",
    "lakeformation",
    "lambda",
    "launch-wizard",
    "lex-models",
    "lex-runtime",
    "lexv2-models",
    "lexv2-runtime",
    "license-manager",
    "license-manager-linux-subscriptions",
    "license-manager-user-subscriptions",
    "lightsail",
    "location",
    "logs",
    "lookoutequipment",
    "lookoutmetrics",
    "lookoutvision",
    "m2",
    "machinelearning",
    "macie2",
    "mailmanager",
    "managedblockchain",
    "managedblockchain-query",
    "marketplace-agreement",
    "marketplace-catalog",
    "marketplace-deployment",
    "marketplace-entitlement",
    "marketplace-reporting",
    "marketplacecommerceanalytics",
    "mediaconnect",
    "mediaconvert",
    "medialive",
    "mediapackage",
    "mediapackage-vod",
    "mediapackagev2",
    "mediastore",
    "mediastore-data",
    "mediatailor",
    "medical-imaging",
    "memorydb",
    "meteringmarketplace",
    "mgh",
    "mgn",
    "migration-hub-refactor-spaces",
    "migrationhub-config",
    "migrationhuborchestrator",
    "migrationhubstrategy",
    "mq",
    "mturk",
    "mwaa",
    "neptune",
    "neptune-graph",
    "neptunedata",
    "network-firewall",
    "networkflowmonitor",
    "networkmanager",
    "networkmonitor",
    "notifications",
    "notificationscontacts",
    "oam",
    "observabilityadmin",
    "omics",
    "opensearch",
    "opensearchserverless",
    "opsworks",
    "opsworkscm",
    "organizations",
    "osis",
    "outposts",
    "panorama",
    "partnercentral-selling",
    "payment-cryptography",
    "payment-cryptography-data",
    "pca-connector-ad",
    "pca-connector-scep",
    "pcs",
    "personalize",
    "personalize-events",
    "personalize-runtime",
    "pi",
    "pinpoint",
    "pinpoint-email",
    "pinpoint-sms-voice",
    "pinpoint-sms-voice-v2",
    "pipes",
    "polly",
    "pricing",
    "privatenetworks",
    "proton",
    "qapps",
    "qbusiness",
    "qconnect",
    "qldb",
    "qldb-session",
    "quicksight",
    "ram",
    "rbin",
    "rds",
    "rds-data",
    "redshift",
    "redshift-data",
    "redshift-serverless",
    "rekognition",
    "repostspace",
    "resiliencehub",
    "resource-explorer-2",
    "resource-groups",
    "resourcegroupstaggingapi",
    "robomaker",
    "rolesanywhere",
    "route53",
    "route53-recovery-cluster",
    "route53-recovery-control-config",
    "route53-recovery-readiness",
    "route53domains",
    "route53profiles",
    "route53resolver",
    "rum",
    "s3",
    "s3control",
    "s3outposts",
    "s3tables",
    "sagemaker",
    "sagemaker-a2i-runtime",
    "sagemaker-edge",
    "sagemaker-featurestore-runtime",
    "sagemaker-geospatial",
    "sagemaker-metrics",
    "sagemaker-runtime",
    "savingsplans",
    "scheduler",
    "schemas",
    "sdb",
    "secretsmanager",
    "security-ir",
    "securityhub",
    "securitylake",
    "serverlessrepo",
    "service-quotas",
    "servicecatalog",
    "servicecatalog-appregistry",
    "servicediscovery",
    "ses",
    "sesv2",
    "shield",
    "signer",
    "simspaceweaver",
    "sms",
    "sms-voice",
    "snow-device-management",
    "snowball",
    "sns",
    "socialmessaging",
    "sqs",
    "ssm",
    "ssm-contacts",
    "ssm-incidents",
    "ssm-quicksetup",
    "ssm-sap",
    "sso",
    "sso-admin",
    "sso-oidc",
    "stepfunctions",
    "storagegateway",
    "sts",
    "supplychain",
    "support",
    "support-app",
    "swf",
    "synthetics",
    "taxsettings",
    "textract",
    "timestream-influxdb",
    "timestream-query",
    "timestream-write",
    "tnb",
    "transcribe",
    "transfer",
    "translate",
    "trustedadvisor",
    "verifiedpermissions",
    "voice-id",
    "vpc-lattice",
    "waf",
    "waf-regional",
    "wafv2",
    "wellarchitected",
    "wisdom",
    "workdocs",
    "workmail",
    "workmailmessageflow",
    "workspaces",
    "workspaces-thin-client",
    "workspaces-web",
    "xray",
]
ResourceServiceName = Literal[
    "cloudformation",
    "cloudwatch",
    "dynamodb",
    "ec2",
    "glacier",
    "iam",
    "opsworks",
    "s3",
    "sns",
    "sqs",
]
PaginatorName = Literal[
    "describe_fleet_attributes",
    "describe_fleet_capacity",
    "describe_fleet_events",
    "describe_fleet_utilization",
    "describe_game_server_instances",
    "describe_game_session_details",
    "describe_game_session_queues",
    "describe_game_sessions",
    "describe_instances",
    "describe_matchmaking_configurations",
    "describe_matchmaking_rule_sets",
    "describe_player_sessions",
    "describe_scaling_policies",
    "list_aliases",
    "list_builds",
    "list_compute",
    "list_container_fleets",
    "list_container_group_definition_versions",
    "list_container_group_definitions",
    "list_fleet_deployments",
    "list_fleets",
    "list_game_server_groups",
    "list_game_servers",
    "list_locations",
    "list_scripts",
    "search_game_sessions",
]
RegionName = Literal[
    "af-south-1",
    "ap-east-1",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "ca-central-1",
    "eu-central-1",
    "eu-north-1",
    "eu-south-1",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "me-south-1",
    "sa-east-1",
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
]
