"""
Type annotations for ecs service literal definitions.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_ecs/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from types_boto3_ecs.literals import AgentUpdateStatusType

    data: AgentUpdateStatusType = "FAILED"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "AgentUpdateStatusType",
    "ApplicationProtocolType",
    "AssignPublicIpType",
    "AvailabilityZoneRebalancingType",
    "CPUArchitectureType",
    "CapacityProviderFieldType",
    "CapacityProviderStatusType",
    "CapacityProviderUpdateStatusType",
    "ClusterFieldType",
    "ClusterSettingNameType",
    "CompatibilityType",
    "ConnectivityType",
    "ContainerConditionType",
    "ContainerInstanceFieldType",
    "ContainerInstanceStatusType",
    "DeploymentControllerTypeType",
    "DeploymentRolloutStateType",
    "DesiredStatusType",
    "DeviceCgroupPermissionType",
    "EBSResourceTypeType",
    "ECSServiceName",
    "EFSAuthorizationConfigIAMType",
    "EFSTransitEncryptionType",
    "EnvironmentFileTypeType",
    "ExecuteCommandLoggingType",
    "FirelensConfigurationTypeType",
    "HealthStatusType",
    "InstanceHealthCheckStateType",
    "InstanceHealthCheckTypeType",
    "IpcModeType",
    "LaunchTypeType",
    "ListAccountSettingsPaginatorName",
    "ListAttributesPaginatorName",
    "ListClustersPaginatorName",
    "ListContainerInstancesPaginatorName",
    "ListServicesByNamespacePaginatorName",
    "ListServicesPaginatorName",
    "ListTaskDefinitionFamiliesPaginatorName",
    "ListTaskDefinitionsPaginatorName",
    "ListTasksPaginatorName",
    "LogDriverType",
    "ManagedAgentNameType",
    "ManagedDrainingType",
    "ManagedScalingStatusType",
    "ManagedTerminationProtectionType",
    "NetworkModeType",
    "OSFamilyType",
    "PaginatorName",
    "PidModeType",
    "PlacementConstraintTypeType",
    "PlacementStrategyTypeType",
    "PlatformDeviceTypeType",
    "PropagateTagsType",
    "ProxyConfigurationTypeType",
    "RegionName",
    "ResourceServiceName",
    "ResourceTypeType",
    "ScaleUnitType",
    "SchedulingStrategyType",
    "ScopeType",
    "ServiceDeploymentRollbackMonitorsStatusType",
    "ServiceDeploymentStatusType",
    "ServiceFieldType",
    "ServiceName",
    "ServicesInactiveWaiterName",
    "ServicesStableWaiterName",
    "SettingNameType",
    "SettingTypeType",
    "SortOrderType",
    "StabilityStatusType",
    "TargetTypeType",
    "TaskDefinitionFamilyStatusType",
    "TaskDefinitionFieldType",
    "TaskDefinitionPlacementConstraintTypeType",
    "TaskDefinitionStatusType",
    "TaskFieldType",
    "TaskFilesystemTypeType",
    "TaskSetFieldType",
    "TaskStopCodeType",
    "TasksRunningWaiterName",
    "TasksStoppedWaiterName",
    "TransportProtocolType",
    "UlimitNameType",
    "VersionConsistencyType",
    "WaiterName",
)


AgentUpdateStatusType = Literal["FAILED", "PENDING", "STAGED", "STAGING", "UPDATED", "UPDATING"]
ApplicationProtocolType = Literal["grpc", "http", "http2"]
AssignPublicIpType = Literal["DISABLED", "ENABLED"]
AvailabilityZoneRebalancingType = Literal["DISABLED", "ENABLED"]
CPUArchitectureType = Literal["ARM64", "X86_64"]
CapacityProviderFieldType = Literal["TAGS"]
CapacityProviderStatusType = Literal["ACTIVE", "INACTIVE"]
CapacityProviderUpdateStatusType = Literal[
    "DELETE_COMPLETE",
    "DELETE_FAILED",
    "DELETE_IN_PROGRESS",
    "UPDATE_COMPLETE",
    "UPDATE_FAILED",
    "UPDATE_IN_PROGRESS",
]
ClusterFieldType = Literal["ATTACHMENTS", "CONFIGURATIONS", "SETTINGS", "STATISTICS", "TAGS"]
ClusterSettingNameType = Literal["containerInsights"]
CompatibilityType = Literal["EC2", "EXTERNAL", "FARGATE"]
ConnectivityType = Literal["CONNECTED", "DISCONNECTED"]
ContainerConditionType = Literal["COMPLETE", "HEALTHY", "START", "SUCCESS"]
ContainerInstanceFieldType = Literal["CONTAINER_INSTANCE_HEALTH", "TAGS"]
ContainerInstanceStatusType = Literal[
    "ACTIVE", "DEREGISTERING", "DRAINING", "REGISTERING", "REGISTRATION_FAILED"
]
DeploymentControllerTypeType = Literal["CODE_DEPLOY", "ECS", "EXTERNAL"]
DeploymentRolloutStateType = Literal["COMPLETED", "FAILED", "IN_PROGRESS"]
DesiredStatusType = Literal["PENDING", "RUNNING", "STOPPED"]
DeviceCgroupPermissionType = Literal["mknod", "read", "write"]
EBSResourceTypeType = Literal["volume"]
EFSAuthorizationConfigIAMType = Literal["DISABLED", "ENABLED"]
EFSTransitEncryptionType = Literal["DISABLED", "ENABLED"]
EnvironmentFileTypeType = Literal["s3"]
ExecuteCommandLoggingType = Literal["DEFAULT", "NONE", "OVERRIDE"]
FirelensConfigurationTypeType = Literal["fluentbit", "fluentd"]
HealthStatusType = Literal["HEALTHY", "UNHEALTHY", "UNKNOWN"]
InstanceHealthCheckStateType = Literal["IMPAIRED", "INITIALIZING", "INSUFFICIENT_DATA", "OK"]
InstanceHealthCheckTypeType = Literal["CONTAINER_RUNTIME"]
IpcModeType = Literal["host", "none", "task"]
LaunchTypeType = Literal["EC2", "EXTERNAL", "FARGATE"]
ListAccountSettingsPaginatorName = Literal["list_account_settings"]
ListAttributesPaginatorName = Literal["list_attributes"]
ListClustersPaginatorName = Literal["list_clusters"]
ListContainerInstancesPaginatorName = Literal["list_container_instances"]
ListServicesByNamespacePaginatorName = Literal["list_services_by_namespace"]
ListServicesPaginatorName = Literal["list_services"]
ListTaskDefinitionFamiliesPaginatorName = Literal["list_task_definition_families"]
ListTaskDefinitionsPaginatorName = Literal["list_task_definitions"]
ListTasksPaginatorName = Literal["list_tasks"]
LogDriverType = Literal[
    "awsfirelens", "awslogs", "fluentd", "gelf", "journald", "json-file", "splunk", "syslog"
]
ManagedAgentNameType = Literal["ExecuteCommandAgent"]
ManagedDrainingType = Literal["DISABLED", "ENABLED"]
ManagedScalingStatusType = Literal["DISABLED", "ENABLED"]
ManagedTerminationProtectionType = Literal["DISABLED", "ENABLED"]
NetworkModeType = Literal["awsvpc", "bridge", "host", "none"]
OSFamilyType = Literal[
    "LINUX",
    "WINDOWS_SERVER_2004_CORE",
    "WINDOWS_SERVER_2016_FULL",
    "WINDOWS_SERVER_2019_CORE",
    "WINDOWS_SERVER_2019_FULL",
    "WINDOWS_SERVER_2022_CORE",
    "WINDOWS_SERVER_2022_FULL",
    "WINDOWS_SERVER_20H2_CORE",
]
PidModeType = Literal["host", "task"]
PlacementConstraintTypeType = Literal["distinctInstance", "memberOf"]
PlacementStrategyTypeType = Literal["binpack", "random", "spread"]
PlatformDeviceTypeType = Literal["GPU"]
PropagateTagsType = Literal["NONE", "SERVICE", "TASK_DEFINITION"]
ProxyConfigurationTypeType = Literal["APPMESH"]
ResourceTypeType = Literal["GPU", "InferenceAccelerator"]
ScaleUnitType = Literal["PERCENT"]
SchedulingStrategyType = Literal["DAEMON", "REPLICA"]
ScopeType = Literal["shared", "task"]
ServiceDeploymentRollbackMonitorsStatusType = Literal[
    "DISABLED", "MONITORING", "MONITORING_COMPLETE", "TRIGGERED"
]
ServiceDeploymentStatusType = Literal[
    "IN_PROGRESS",
    "PENDING",
    "ROLLBACK_FAILED",
    "ROLLBACK_IN_PROGRESS",
    "ROLLBACK_SUCCESSFUL",
    "STOPPED",
    "STOP_REQUESTED",
    "SUCCESSFUL",
]
ServiceFieldType = Literal["TAGS"]
ServicesInactiveWaiterName = Literal["services_inactive"]
ServicesStableWaiterName = Literal["services_stable"]
SettingNameType = Literal[
    "awsvpcTrunking",
    "containerInsights",
    "containerInstanceLongArnFormat",
    "fargateFIPSMode",
    "fargateTaskRetirementWaitPeriod",
    "guardDutyActivate",
    "serviceLongArnFormat",
    "tagResourceAuthorization",
    "taskLongArnFormat",
]
SettingTypeType = Literal["aws_managed", "user"]
SortOrderType = Literal["ASC", "DESC"]
StabilityStatusType = Literal["STABILIZING", "STEADY_STATE"]
TargetTypeType = Literal["container-instance"]
TaskDefinitionFamilyStatusType = Literal["ACTIVE", "ALL", "INACTIVE"]
TaskDefinitionFieldType = Literal["TAGS"]
TaskDefinitionPlacementConstraintTypeType = Literal["memberOf"]
TaskDefinitionStatusType = Literal["ACTIVE", "DELETE_IN_PROGRESS", "INACTIVE"]
TaskFieldType = Literal["TAGS"]
TaskFilesystemTypeType = Literal["ext3", "ext4", "ntfs", "xfs"]
TaskSetFieldType = Literal["TAGS"]
TaskStopCodeType = Literal[
    "EssentialContainerExited",
    "ServiceSchedulerInitiated",
    "SpotInterruption",
    "TaskFailedToStart",
    "TerminationNotice",
    "UserInitiated",
]
TasksRunningWaiterName = Literal["tasks_running"]
TasksStoppedWaiterName = Literal["tasks_stopped"]
TransportProtocolType = Literal["tcp", "udp"]
UlimitNameType = Literal[
    "core",
    "cpu",
    "data",
    "fsize",
    "locks",
    "memlock",
    "msgqueue",
    "nice",
    "nofile",
    "nproc",
    "rss",
    "rtprio",
    "rttime",
    "sigpending",
    "stack",
]
VersionConsistencyType = Literal["disabled", "enabled"]
ECSServiceName = Literal["ecs"]
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
    "list_account_settings",
    "list_attributes",
    "list_clusters",
    "list_container_instances",
    "list_services",
    "list_services_by_namespace",
    "list_task_definition_families",
    "list_task_definitions",
    "list_tasks",
]
WaiterName = Literal["services_inactive", "services_stable", "tasks_running", "tasks_stopped"]
RegionName = Literal[
    "af-south-1",
    "ap-east-1",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ap-south-1",
    "ap-south-2",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-southeast-3",
    "ap-southeast-4",
    "ap-southeast-5",
    "ap-southeast-7",
    "ca-central-1",
    "ca-west-1",
    "eu-central-1",
    "eu-central-2",
    "eu-north-1",
    "eu-south-1",
    "eu-south-2",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "il-central-1",
    "me-central-1",
    "me-south-1",
    "mx-central-1",
    "sa-east-1",
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
]
