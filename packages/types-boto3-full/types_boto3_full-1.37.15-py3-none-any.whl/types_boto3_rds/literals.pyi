"""
Type annotations for rds service literal definitions.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_rds/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from types_boto3_rds.literals import ActivityStreamModeType

    data: ActivityStreamModeType = "async"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = (
    "ActivityStreamModeType",
    "ActivityStreamPolicyStatusType",
    "ActivityStreamStatusType",
    "ApplyMethodType",
    "AuditPolicyStateType",
    "AuthSchemeType",
    "AutomationModeType",
    "ClientPasswordAuthTypeType",
    "ClusterScalabilityTypeType",
    "CustomEngineVersionStatusType",
    "DBClusterAvailableWaiterName",
    "DBClusterDeletedWaiterName",
    "DBClusterSnapshotAvailableWaiterName",
    "DBClusterSnapshotDeletedWaiterName",
    "DBInstanceAvailableWaiterName",
    "DBInstanceDeletedWaiterName",
    "DBProxyEndpointStatusType",
    "DBProxyEndpointTargetRoleType",
    "DBProxyStatusType",
    "DBSnapshotAvailableWaiterName",
    "DBSnapshotCompletedWaiterName",
    "DBSnapshotDeletedWaiterName",
    "DatabaseInsightsModeType",
    "DescribeBlueGreenDeploymentsPaginatorName",
    "DescribeCertificatesPaginatorName",
    "DescribeDBClusterAutomatedBackupsPaginatorName",
    "DescribeDBClusterBacktracksPaginatorName",
    "DescribeDBClusterEndpointsPaginatorName",
    "DescribeDBClusterParameterGroupsPaginatorName",
    "DescribeDBClusterParametersPaginatorName",
    "DescribeDBClusterSnapshotsPaginatorName",
    "DescribeDBClustersPaginatorName",
    "DescribeDBEngineVersionsPaginatorName",
    "DescribeDBInstanceAutomatedBackupsPaginatorName",
    "DescribeDBInstancesPaginatorName",
    "DescribeDBLogFilesPaginatorName",
    "DescribeDBParameterGroupsPaginatorName",
    "DescribeDBParametersPaginatorName",
    "DescribeDBProxiesPaginatorName",
    "DescribeDBProxyEndpointsPaginatorName",
    "DescribeDBProxyTargetGroupsPaginatorName",
    "DescribeDBProxyTargetsPaginatorName",
    "DescribeDBRecommendationsPaginatorName",
    "DescribeDBSecurityGroupsPaginatorName",
    "DescribeDBSnapshotTenantDatabasesPaginatorName",
    "DescribeDBSnapshotsPaginatorName",
    "DescribeDBSubnetGroupsPaginatorName",
    "DescribeEngineDefaultClusterParametersPaginatorName",
    "DescribeEngineDefaultParametersPaginatorName",
    "DescribeEventSubscriptionsPaginatorName",
    "DescribeEventsPaginatorName",
    "DescribeExportTasksPaginatorName",
    "DescribeGlobalClustersPaginatorName",
    "DescribeIntegrationsPaginatorName",
    "DescribeOptionGroupOptionsPaginatorName",
    "DescribeOptionGroupsPaginatorName",
    "DescribeOrderableDBInstanceOptionsPaginatorName",
    "DescribePendingMaintenanceActionsPaginatorName",
    "DescribeReservedDBInstancesOfferingsPaginatorName",
    "DescribeReservedDBInstancesPaginatorName",
    "DescribeSourceRegionsPaginatorName",
    "DescribeTenantDatabasesPaginatorName",
    "DownloadDBLogFilePortionPaginatorName",
    "EngineFamilyType",
    "ExportSourceTypeType",
    "FailoverStatusType",
    "GlobalClusterMemberSynchronizationStatusType",
    "IAMAuthModeType",
    "IntegrationStatusType",
    "LimitlessDatabaseStatusType",
    "LocalWriteForwardingStatusType",
    "PaginatorName",
    "RDSServiceName",
    "RegionName",
    "ReplicaModeType",
    "ResourceServiceName",
    "ServiceName",
    "SourceTypeType",
    "TargetHealthReasonType",
    "TargetRoleType",
    "TargetStateType",
    "TargetTypeType",
    "TenantDatabaseAvailableWaiterName",
    "TenantDatabaseDeletedWaiterName",
    "WaiterName",
    "WriteForwardingStatusType",
)

ActivityStreamModeType = Literal["async", "sync"]
ActivityStreamPolicyStatusType = Literal["locked", "locking-policy", "unlocked", "unlocking-policy"]
ActivityStreamStatusType = Literal["started", "starting", "stopped", "stopping"]
ApplyMethodType = Literal["immediate", "pending-reboot"]
AuditPolicyStateType = Literal["locked", "unlocked"]
AuthSchemeType = Literal["SECRETS"]
AutomationModeType = Literal["all-paused", "full"]
ClientPasswordAuthTypeType = Literal[
    "MYSQL_CACHING_SHA2_PASSWORD",
    "MYSQL_NATIVE_PASSWORD",
    "POSTGRES_MD5",
    "POSTGRES_SCRAM_SHA_256",
    "SQL_SERVER_AUTHENTICATION",
]
ClusterScalabilityTypeType = Literal["limitless", "standard"]
CustomEngineVersionStatusType = Literal["available", "inactive", "inactive-except-restore"]
DBClusterAvailableWaiterName = Literal["db_cluster_available"]
DBClusterDeletedWaiterName = Literal["db_cluster_deleted"]
DBClusterSnapshotAvailableWaiterName = Literal["db_cluster_snapshot_available"]
DBClusterSnapshotDeletedWaiterName = Literal["db_cluster_snapshot_deleted"]
DBInstanceAvailableWaiterName = Literal["db_instance_available"]
DBInstanceDeletedWaiterName = Literal["db_instance_deleted"]
DBProxyEndpointStatusType = Literal[
    "available",
    "creating",
    "deleting",
    "incompatible-network",
    "insufficient-resource-limits",
    "modifying",
]
DBProxyEndpointTargetRoleType = Literal["READ_ONLY", "READ_WRITE"]
DBProxyStatusType = Literal[
    "available",
    "creating",
    "deleting",
    "incompatible-network",
    "insufficient-resource-limits",
    "modifying",
    "reactivating",
    "suspended",
    "suspending",
]
DBSnapshotAvailableWaiterName = Literal["db_snapshot_available"]
DBSnapshotCompletedWaiterName = Literal["db_snapshot_completed"]
DBSnapshotDeletedWaiterName = Literal["db_snapshot_deleted"]
DatabaseInsightsModeType = Literal["advanced", "standard"]
DescribeBlueGreenDeploymentsPaginatorName = Literal["describe_blue_green_deployments"]
DescribeCertificatesPaginatorName = Literal["describe_certificates"]
DescribeDBClusterAutomatedBackupsPaginatorName = Literal["describe_db_cluster_automated_backups"]
DescribeDBClusterBacktracksPaginatorName = Literal["describe_db_cluster_backtracks"]
DescribeDBClusterEndpointsPaginatorName = Literal["describe_db_cluster_endpoints"]
DescribeDBClusterParameterGroupsPaginatorName = Literal["describe_db_cluster_parameter_groups"]
DescribeDBClusterParametersPaginatorName = Literal["describe_db_cluster_parameters"]
DescribeDBClusterSnapshotsPaginatorName = Literal["describe_db_cluster_snapshots"]
DescribeDBClustersPaginatorName = Literal["describe_db_clusters"]
DescribeDBEngineVersionsPaginatorName = Literal["describe_db_engine_versions"]
DescribeDBInstanceAutomatedBackupsPaginatorName = Literal["describe_db_instance_automated_backups"]
DescribeDBInstancesPaginatorName = Literal["describe_db_instances"]
DescribeDBLogFilesPaginatorName = Literal["describe_db_log_files"]
DescribeDBParameterGroupsPaginatorName = Literal["describe_db_parameter_groups"]
DescribeDBParametersPaginatorName = Literal["describe_db_parameters"]
DescribeDBProxiesPaginatorName = Literal["describe_db_proxies"]
DescribeDBProxyEndpointsPaginatorName = Literal["describe_db_proxy_endpoints"]
DescribeDBProxyTargetGroupsPaginatorName = Literal["describe_db_proxy_target_groups"]
DescribeDBProxyTargetsPaginatorName = Literal["describe_db_proxy_targets"]
DescribeDBRecommendationsPaginatorName = Literal["describe_db_recommendations"]
DescribeDBSecurityGroupsPaginatorName = Literal["describe_db_security_groups"]
DescribeDBSnapshotTenantDatabasesPaginatorName = Literal["describe_db_snapshot_tenant_databases"]
DescribeDBSnapshotsPaginatorName = Literal["describe_db_snapshots"]
DescribeDBSubnetGroupsPaginatorName = Literal["describe_db_subnet_groups"]
DescribeEngineDefaultClusterParametersPaginatorName = Literal[
    "describe_engine_default_cluster_parameters"
]
DescribeEngineDefaultParametersPaginatorName = Literal["describe_engine_default_parameters"]
DescribeEventSubscriptionsPaginatorName = Literal["describe_event_subscriptions"]
DescribeEventsPaginatorName = Literal["describe_events"]
DescribeExportTasksPaginatorName = Literal["describe_export_tasks"]
DescribeGlobalClustersPaginatorName = Literal["describe_global_clusters"]
DescribeIntegrationsPaginatorName = Literal["describe_integrations"]
DescribeOptionGroupOptionsPaginatorName = Literal["describe_option_group_options"]
DescribeOptionGroupsPaginatorName = Literal["describe_option_groups"]
DescribeOrderableDBInstanceOptionsPaginatorName = Literal["describe_orderable_db_instance_options"]
DescribePendingMaintenanceActionsPaginatorName = Literal["describe_pending_maintenance_actions"]
DescribeReservedDBInstancesOfferingsPaginatorName = Literal[
    "describe_reserved_db_instances_offerings"
]
DescribeReservedDBInstancesPaginatorName = Literal["describe_reserved_db_instances"]
DescribeSourceRegionsPaginatorName = Literal["describe_source_regions"]
DescribeTenantDatabasesPaginatorName = Literal["describe_tenant_databases"]
DownloadDBLogFilePortionPaginatorName = Literal["download_db_log_file_portion"]
EngineFamilyType = Literal["MYSQL", "POSTGRESQL", "SQLSERVER"]
ExportSourceTypeType = Literal["CLUSTER", "SNAPSHOT"]
FailoverStatusType = Literal["cancelling", "failing-over", "pending"]
GlobalClusterMemberSynchronizationStatusType = Literal["connected", "pending-resync"]
IAMAuthModeType = Literal["DISABLED", "ENABLED", "REQUIRED"]
IntegrationStatusType = Literal[
    "active", "creating", "deleting", "failed", "modifying", "needs_attention", "syncing"
]
LimitlessDatabaseStatusType = Literal[
    "active",
    "disabled",
    "disabling",
    "enabled",
    "enabling",
    "error",
    "modifying-max-capacity",
    "not-in-use",
]
LocalWriteForwardingStatusType = Literal[
    "disabled", "disabling", "enabled", "enabling", "requested"
]
ReplicaModeType = Literal["mounted", "open-read-only"]
SourceTypeType = Literal[
    "blue-green-deployment",
    "custom-engine-version",
    "db-cluster",
    "db-cluster-snapshot",
    "db-instance",
    "db-parameter-group",
    "db-proxy",
    "db-security-group",
    "db-snapshot",
]
TargetHealthReasonType = Literal[
    "AUTH_FAILURE",
    "CONNECTION_FAILED",
    "INVALID_REPLICATION_STATE",
    "PENDING_PROXY_CAPACITY",
    "UNREACHABLE",
]
TargetRoleType = Literal["READ_ONLY", "READ_WRITE", "UNKNOWN"]
TargetStateType = Literal["AVAILABLE", "REGISTERING", "UNAVAILABLE"]
TargetTypeType = Literal["RDS_INSTANCE", "RDS_SERVERLESS_ENDPOINT", "TRACKED_CLUSTER"]
TenantDatabaseAvailableWaiterName = Literal["tenant_database_available"]
TenantDatabaseDeletedWaiterName = Literal["tenant_database_deleted"]
WriteForwardingStatusType = Literal["disabled", "disabling", "enabled", "enabling", "unknown"]
RDSServiceName = Literal["rds"]
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
    "describe_blue_green_deployments",
    "describe_certificates",
    "describe_db_cluster_automated_backups",
    "describe_db_cluster_backtracks",
    "describe_db_cluster_endpoints",
    "describe_db_cluster_parameter_groups",
    "describe_db_cluster_parameters",
    "describe_db_cluster_snapshots",
    "describe_db_clusters",
    "describe_db_engine_versions",
    "describe_db_instance_automated_backups",
    "describe_db_instances",
    "describe_db_log_files",
    "describe_db_parameter_groups",
    "describe_db_parameters",
    "describe_db_proxies",
    "describe_db_proxy_endpoints",
    "describe_db_proxy_target_groups",
    "describe_db_proxy_targets",
    "describe_db_recommendations",
    "describe_db_security_groups",
    "describe_db_snapshot_tenant_databases",
    "describe_db_snapshots",
    "describe_db_subnet_groups",
    "describe_engine_default_cluster_parameters",
    "describe_engine_default_parameters",
    "describe_event_subscriptions",
    "describe_events",
    "describe_export_tasks",
    "describe_global_clusters",
    "describe_integrations",
    "describe_option_group_options",
    "describe_option_groups",
    "describe_orderable_db_instance_options",
    "describe_pending_maintenance_actions",
    "describe_reserved_db_instances",
    "describe_reserved_db_instances_offerings",
    "describe_source_regions",
    "describe_tenant_databases",
    "download_db_log_file_portion",
]
WaiterName = Literal[
    "db_cluster_available",
    "db_cluster_deleted",
    "db_cluster_snapshot_available",
    "db_cluster_snapshot_deleted",
    "db_instance_available",
    "db_instance_deleted",
    "db_snapshot_available",
    "db_snapshot_completed",
    "db_snapshot_deleted",
    "tenant_database_available",
    "tenant_database_deleted",
]
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
