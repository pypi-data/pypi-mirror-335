"""
Type annotations for s3control service literal definitions.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_s3control/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from types_boto3_s3control.literals import AsyncOperationNameType

    data: AsyncOperationNameType = "CreateMultiRegionAccessPoint"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "AsyncOperationNameType",
    "BucketCannedACLType",
    "BucketLocationConstraintType",
    "BucketVersioningStatusType",
    "DeleteMarkerReplicationStatusType",
    "ExistingObjectReplicationStatusType",
    "ExpirationStatusType",
    "FormatType",
    "GeneratedManifestFormatType",
    "GranteeTypeType",
    "JobManifestFieldNameType",
    "JobManifestFormatType",
    "JobReportFormatType",
    "JobReportScopeType",
    "JobStatusType",
    "ListAccessPointsForObjectLambdaPaginatorName",
    "ListCallerAccessGrantsPaginatorName",
    "MFADeleteStatusType",
    "MFADeleteType",
    "MetricsStatusType",
    "MultiRegionAccessPointStatusType",
    "NetworkOriginType",
    "ObjectLambdaAccessPointAliasStatusType",
    "ObjectLambdaAllowedFeatureType",
    "ObjectLambdaTransformationConfigurationActionType",
    "OperationNameType",
    "OutputSchemaVersionType",
    "OwnerOverrideType",
    "PaginatorName",
    "PermissionType",
    "PrivilegeType",
    "RegionName",
    "ReplicaModificationsStatusType",
    "ReplicationRuleStatusType",
    "ReplicationStatusType",
    "ReplicationStorageClassType",
    "ReplicationTimeStatusType",
    "RequestedJobStatusType",
    "ResourceServiceName",
    "S3CannedAccessControlListType",
    "S3ChecksumAlgorithmType",
    "S3ControlServiceName",
    "S3GlacierJobTierType",
    "S3GranteeTypeIdentifierType",
    "S3MetadataDirectiveType",
    "S3ObjectLockLegalHoldStatusType",
    "S3ObjectLockModeType",
    "S3ObjectLockRetentionModeType",
    "S3PermissionType",
    "S3PrefixTypeType",
    "S3SSEAlgorithmType",
    "S3StorageClassType",
    "ServiceName",
    "SseKmsEncryptedObjectsStatusType",
    "TransitionStorageClassType",
)


AsyncOperationNameType = Literal[
    "CreateMultiRegionAccessPoint",
    "DeleteMultiRegionAccessPoint",
    "PutMultiRegionAccessPointPolicy",
]
BucketCannedACLType = Literal["authenticated-read", "private", "public-read", "public-read-write"]
BucketLocationConstraintType = Literal[
    "EU",
    "ap-northeast-1",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "cn-north-1",
    "eu-central-1",
    "eu-west-1",
    "sa-east-1",
    "us-west-1",
    "us-west-2",
]
BucketVersioningStatusType = Literal["Enabled", "Suspended"]
DeleteMarkerReplicationStatusType = Literal["Disabled", "Enabled"]
ExistingObjectReplicationStatusType = Literal["Disabled", "Enabled"]
ExpirationStatusType = Literal["Disabled", "Enabled"]
FormatType = Literal["CSV", "Parquet"]
GeneratedManifestFormatType = Literal["S3InventoryReport_CSV_20211130"]
GranteeTypeType = Literal["DIRECTORY_GROUP", "DIRECTORY_USER", "IAM"]
JobManifestFieldNameType = Literal["Bucket", "Ignore", "Key", "VersionId"]
JobManifestFormatType = Literal["S3BatchOperations_CSV_20180820", "S3InventoryReport_CSV_20161130"]
JobReportFormatType = Literal["Report_CSV_20180820"]
JobReportScopeType = Literal["AllTasks", "FailedTasksOnly"]
JobStatusType = Literal[
    "Active",
    "Cancelled",
    "Cancelling",
    "Complete",
    "Completing",
    "Failed",
    "Failing",
    "New",
    "Paused",
    "Pausing",
    "Preparing",
    "Ready",
    "Suspended",
]
ListAccessPointsForObjectLambdaPaginatorName = Literal["list_access_points_for_object_lambda"]
ListCallerAccessGrantsPaginatorName = Literal["list_caller_access_grants"]
MFADeleteStatusType = Literal["Disabled", "Enabled"]
MFADeleteType = Literal["Disabled", "Enabled"]
MetricsStatusType = Literal["Disabled", "Enabled"]
MultiRegionAccessPointStatusType = Literal[
    "CREATING",
    "DELETING",
    "INCONSISTENT_ACROSS_REGIONS",
    "PARTIALLY_CREATED",
    "PARTIALLY_DELETED",
    "READY",
]
NetworkOriginType = Literal["Internet", "VPC"]
ObjectLambdaAccessPointAliasStatusType = Literal["PROVISIONING", "READY"]
ObjectLambdaAllowedFeatureType = Literal[
    "GetObject-PartNumber", "GetObject-Range", "HeadObject-PartNumber", "HeadObject-Range"
]
ObjectLambdaTransformationConfigurationActionType = Literal[
    "GetObject", "HeadObject", "ListObjects", "ListObjectsV2"
]
OperationNameType = Literal[
    "LambdaInvoke",
    "S3DeleteObjectTagging",
    "S3InitiateRestoreObject",
    "S3PutObjectAcl",
    "S3PutObjectCopy",
    "S3PutObjectLegalHold",
    "S3PutObjectRetention",
    "S3PutObjectTagging",
    "S3ReplicateObject",
]
OutputSchemaVersionType = Literal["V_1"]
OwnerOverrideType = Literal["Destination"]
PermissionType = Literal["READ", "READWRITE", "WRITE"]
PrivilegeType = Literal["Default", "Minimal"]
ReplicaModificationsStatusType = Literal["Disabled", "Enabled"]
ReplicationRuleStatusType = Literal["Disabled", "Enabled"]
ReplicationStatusType = Literal["COMPLETED", "FAILED", "NONE", "REPLICA"]
ReplicationStorageClassType = Literal[
    "DEEP_ARCHIVE",
    "GLACIER",
    "GLACIER_IR",
    "INTELLIGENT_TIERING",
    "ONEZONE_IA",
    "OUTPOSTS",
    "REDUCED_REDUNDANCY",
    "STANDARD",
    "STANDARD_IA",
]
ReplicationTimeStatusType = Literal["Disabled", "Enabled"]
RequestedJobStatusType = Literal["Cancelled", "Ready"]
S3CannedAccessControlListType = Literal[
    "authenticated-read",
    "aws-exec-read",
    "bucket-owner-full-control",
    "bucket-owner-read",
    "private",
    "public-read",
    "public-read-write",
]
S3ChecksumAlgorithmType = Literal["CRC32", "CRC32C", "CRC64NVME", "SHA1", "SHA256"]
S3GlacierJobTierType = Literal["BULK", "STANDARD"]
S3GranteeTypeIdentifierType = Literal["emailAddress", "id", "uri"]
S3MetadataDirectiveType = Literal["COPY", "REPLACE"]
S3ObjectLockLegalHoldStatusType = Literal["OFF", "ON"]
S3ObjectLockModeType = Literal["COMPLIANCE", "GOVERNANCE"]
S3ObjectLockRetentionModeType = Literal["COMPLIANCE", "GOVERNANCE"]
S3PermissionType = Literal["FULL_CONTROL", "READ", "READ_ACP", "WRITE", "WRITE_ACP"]
S3PrefixTypeType = Literal["Object"]
S3SSEAlgorithmType = Literal["AES256", "KMS"]
S3StorageClassType = Literal[
    "DEEP_ARCHIVE",
    "GLACIER",
    "GLACIER_IR",
    "INTELLIGENT_TIERING",
    "ONEZONE_IA",
    "STANDARD",
    "STANDARD_IA",
]
SseKmsEncryptedObjectsStatusType = Literal["Disabled", "Enabled"]
TransitionStorageClassType = Literal[
    "DEEP_ARCHIVE", "GLACIER", "INTELLIGENT_TIERING", "ONEZONE_IA", "STANDARD_IA"
]
S3ControlServiceName = Literal["s3control"]
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
PaginatorName = Literal["list_access_points_for_object_lambda", "list_caller_access_grants"]
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
    "sa-east-1",
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
]
