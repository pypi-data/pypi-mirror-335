"""
Type annotations for cloudformation service literal definitions.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_cloudformation/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from types_boto3_cloudformation.literals import AccountFilterTypeType

    data: AccountFilterTypeType = "DIFFERENCE"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = (
    "AccountFilterTypeType",
    "AccountGateStatusType",
    "AttributeChangeTypeType",
    "CallAsType",
    "CapabilityType",
    "CategoryType",
    "ChangeActionType",
    "ChangeSetCreateCompleteWaiterName",
    "ChangeSetHooksStatusType",
    "ChangeSetStatusType",
    "ChangeSetTypeType",
    "ChangeSourceType",
    "ChangeTypeType",
    "CloudFormationServiceName",
    "ConcurrencyModeType",
    "DeletionModeType",
    "DeprecatedStatusType",
    "DescribeAccountLimitsPaginatorName",
    "DescribeChangeSetPaginatorName",
    "DescribeStackEventsPaginatorName",
    "DescribeStacksPaginatorName",
    "DetailedStatusType",
    "DifferenceTypeType",
    "EvaluationTypeType",
    "ExecutionStatusType",
    "GeneratedTemplateDeletionPolicyType",
    "GeneratedTemplateResourceStatusType",
    "GeneratedTemplateStatusType",
    "GeneratedTemplateUpdateReplacePolicyType",
    "HandlerErrorCodeType",
    "HookFailureModeType",
    "HookInvocationPointType",
    "HookStatusType",
    "HookTargetTypeType",
    "IdentityProviderType",
    "ListChangeSetsPaginatorName",
    "ListExportsPaginatorName",
    "ListGeneratedTemplatesPaginatorName",
    "ListHookResultsTargetTypeType",
    "ListImportsPaginatorName",
    "ListResourceScanRelatedResourcesPaginatorName",
    "ListResourceScanResourcesPaginatorName",
    "ListResourceScansPaginatorName",
    "ListStackInstancesPaginatorName",
    "ListStackRefactorActionsPaginatorName",
    "ListStackRefactorsPaginatorName",
    "ListStackResourcesPaginatorName",
    "ListStackSetOperationResultsPaginatorName",
    "ListStackSetOperationsPaginatorName",
    "ListStackSetsPaginatorName",
    "ListStacksPaginatorName",
    "ListTypesPaginatorName",
    "OnFailureType",
    "OnStackFailureType",
    "OperationResultFilterNameType",
    "OperationStatusType",
    "OrganizationStatusType",
    "PaginatorName",
    "PermissionModelsType",
    "PolicyActionType",
    "ProvisioningTypeType",
    "PublisherStatusType",
    "RegionConcurrencyTypeType",
    "RegionName",
    "RegistrationStatusType",
    "RegistryTypeType",
    "ReplacementType",
    "RequiresRecreationType",
    "ResourceAttributeType",
    "ResourceScanStatusType",
    "ResourceServiceName",
    "ResourceSignalStatusType",
    "ResourceStatusType",
    "ServiceName",
    "StackCreateCompleteWaiterName",
    "StackDeleteCompleteWaiterName",
    "StackDriftDetectionStatusType",
    "StackDriftStatusType",
    "StackExistsWaiterName",
    "StackImportCompleteWaiterName",
    "StackInstanceDetailedStatusType",
    "StackInstanceFilterNameType",
    "StackInstanceStatusType",
    "StackRefactorActionEntityType",
    "StackRefactorActionTypeType",
    "StackRefactorCreateCompleteWaiterName",
    "StackRefactorDetectionType",
    "StackRefactorExecuteCompleteWaiterName",
    "StackRefactorExecutionStatusType",
    "StackRefactorStatusType",
    "StackResourceDriftStatusType",
    "StackRollbackCompleteWaiterName",
    "StackSetDriftDetectionStatusType",
    "StackSetDriftStatusType",
    "StackSetOperationActionType",
    "StackSetOperationResultStatusType",
    "StackSetOperationStatusType",
    "StackSetStatusType",
    "StackStatusType",
    "StackUpdateCompleteWaiterName",
    "TemplateFormatType",
    "TemplateStageType",
    "ThirdPartyTypeType",
    "TypeRegistrationCompleteWaiterName",
    "TypeTestsStatusType",
    "VersionBumpType",
    "VisibilityType",
    "WaiterName",
    "WarningTypeType",
)

AccountFilterTypeType = Literal["DIFFERENCE", "INTERSECTION", "NONE", "UNION"]
AccountGateStatusType = Literal["FAILED", "SKIPPED", "SUCCEEDED"]
AttributeChangeTypeType = Literal["Add", "Modify", "Remove"]
CallAsType = Literal["DELEGATED_ADMIN", "SELF"]
CapabilityType = Literal["CAPABILITY_AUTO_EXPAND", "CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"]
CategoryType = Literal["ACTIVATED", "AWS_TYPES", "REGISTERED", "THIRD_PARTY"]
ChangeActionType = Literal["Add", "Dynamic", "Import", "Modify", "Remove"]
ChangeSetCreateCompleteWaiterName = Literal["change_set_create_complete"]
ChangeSetHooksStatusType = Literal["PLANNED", "PLANNING", "UNAVAILABLE"]
ChangeSetStatusType = Literal[
    "CREATE_COMPLETE",
    "CREATE_IN_PROGRESS",
    "CREATE_PENDING",
    "DELETE_COMPLETE",
    "DELETE_FAILED",
    "DELETE_IN_PROGRESS",
    "DELETE_PENDING",
    "FAILED",
]
ChangeSetTypeType = Literal["CREATE", "IMPORT", "UPDATE"]
ChangeSourceType = Literal[
    "Automatic",
    "DirectModification",
    "ParameterReference",
    "ResourceAttribute",
    "ResourceReference",
]
ChangeTypeType = Literal["Resource"]
ConcurrencyModeType = Literal["SOFT_FAILURE_TOLERANCE", "STRICT_FAILURE_TOLERANCE"]
DeletionModeType = Literal["FORCE_DELETE_STACK", "STANDARD"]
DeprecatedStatusType = Literal["DEPRECATED", "LIVE"]
DescribeAccountLimitsPaginatorName = Literal["describe_account_limits"]
DescribeChangeSetPaginatorName = Literal["describe_change_set"]
DescribeStackEventsPaginatorName = Literal["describe_stack_events"]
DescribeStacksPaginatorName = Literal["describe_stacks"]
DetailedStatusType = Literal["CONFIGURATION_COMPLETE", "VALIDATION_FAILED"]
DifferenceTypeType = Literal["ADD", "NOT_EQUAL", "REMOVE"]
EvaluationTypeType = Literal["Dynamic", "Static"]
ExecutionStatusType = Literal[
    "AVAILABLE",
    "EXECUTE_COMPLETE",
    "EXECUTE_FAILED",
    "EXECUTE_IN_PROGRESS",
    "OBSOLETE",
    "UNAVAILABLE",
]
GeneratedTemplateDeletionPolicyType = Literal["DELETE", "RETAIN"]
GeneratedTemplateResourceStatusType = Literal["COMPLETE", "FAILED", "IN_PROGRESS", "PENDING"]
GeneratedTemplateStatusType = Literal[
    "COMPLETE",
    "CREATE_IN_PROGRESS",
    "CREATE_PENDING",
    "DELETE_IN_PROGRESS",
    "DELETE_PENDING",
    "FAILED",
    "UPDATE_IN_PROGRESS",
    "UPDATE_PENDING",
]
GeneratedTemplateUpdateReplacePolicyType = Literal["DELETE", "RETAIN"]
HandlerErrorCodeType = Literal[
    "AccessDenied",
    "AlreadyExists",
    "GeneralServiceException",
    "HandlerInternalFailure",
    "InternalFailure",
    "InvalidCredentials",
    "InvalidRequest",
    "InvalidTypeConfiguration",
    "NetworkFailure",
    "NonCompliant",
    "NotFound",
    "NotStabilized",
    "NotUpdatable",
    "ResourceConflict",
    "ServiceInternalError",
    "ServiceLimitExceeded",
    "Throttling",
    "Unknown",
    "UnsupportedTarget",
]
HookFailureModeType = Literal["FAIL", "WARN"]
HookInvocationPointType = Literal["PRE_PROVISION"]
HookStatusType = Literal[
    "HOOK_COMPLETE_FAILED", "HOOK_COMPLETE_SUCCEEDED", "HOOK_FAILED", "HOOK_IN_PROGRESS"
]
HookTargetTypeType = Literal["RESOURCE"]
IdentityProviderType = Literal["AWS_Marketplace", "Bitbucket", "GitHub"]
ListChangeSetsPaginatorName = Literal["list_change_sets"]
ListExportsPaginatorName = Literal["list_exports"]
ListGeneratedTemplatesPaginatorName = Literal["list_generated_templates"]
ListHookResultsTargetTypeType = Literal["CHANGE_SET", "CLOUD_CONTROL", "RESOURCE", "STACK"]
ListImportsPaginatorName = Literal["list_imports"]
ListResourceScanRelatedResourcesPaginatorName = Literal["list_resource_scan_related_resources"]
ListResourceScanResourcesPaginatorName = Literal["list_resource_scan_resources"]
ListResourceScansPaginatorName = Literal["list_resource_scans"]
ListStackInstancesPaginatorName = Literal["list_stack_instances"]
ListStackRefactorActionsPaginatorName = Literal["list_stack_refactor_actions"]
ListStackRefactorsPaginatorName = Literal["list_stack_refactors"]
ListStackResourcesPaginatorName = Literal["list_stack_resources"]
ListStackSetOperationResultsPaginatorName = Literal["list_stack_set_operation_results"]
ListStackSetOperationsPaginatorName = Literal["list_stack_set_operations"]
ListStackSetsPaginatorName = Literal["list_stack_sets"]
ListStacksPaginatorName = Literal["list_stacks"]
ListTypesPaginatorName = Literal["list_types"]
OnFailureType = Literal["DELETE", "DO_NOTHING", "ROLLBACK"]
OnStackFailureType = Literal["DELETE", "DO_NOTHING", "ROLLBACK"]
OperationResultFilterNameType = Literal["OPERATION_RESULT_STATUS"]
OperationStatusType = Literal["FAILED", "IN_PROGRESS", "PENDING", "SUCCESS"]
OrganizationStatusType = Literal["DISABLED", "DISABLED_PERMANENTLY", "ENABLED"]
PermissionModelsType = Literal["SELF_MANAGED", "SERVICE_MANAGED"]
PolicyActionType = Literal[
    "Delete", "ReplaceAndDelete", "ReplaceAndRetain", "ReplaceAndSnapshot", "Retain", "Snapshot"
]
ProvisioningTypeType = Literal["FULLY_MUTABLE", "IMMUTABLE", "NON_PROVISIONABLE"]
PublisherStatusType = Literal["UNVERIFIED", "VERIFIED"]
RegionConcurrencyTypeType = Literal["PARALLEL", "SEQUENTIAL"]
RegistrationStatusType = Literal["COMPLETE", "FAILED", "IN_PROGRESS"]
RegistryTypeType = Literal["HOOK", "MODULE", "RESOURCE"]
ReplacementType = Literal["Conditional", "False", "True"]
RequiresRecreationType = Literal["Always", "Conditionally", "Never"]
ResourceAttributeType = Literal[
    "CreationPolicy",
    "DeletionPolicy",
    "Metadata",
    "Properties",
    "Tags",
    "UpdatePolicy",
    "UpdateReplacePolicy",
]
ResourceScanStatusType = Literal["COMPLETE", "EXPIRED", "FAILED", "IN_PROGRESS"]
ResourceSignalStatusType = Literal["FAILURE", "SUCCESS"]
ResourceStatusType = Literal[
    "CREATE_COMPLETE",
    "CREATE_FAILED",
    "CREATE_IN_PROGRESS",
    "DELETE_COMPLETE",
    "DELETE_FAILED",
    "DELETE_IN_PROGRESS",
    "DELETE_SKIPPED",
    "EXPORT_COMPLETE",
    "EXPORT_FAILED",
    "EXPORT_IN_PROGRESS",
    "EXPORT_ROLLBACK_COMPLETE",
    "EXPORT_ROLLBACK_FAILED",
    "EXPORT_ROLLBACK_IN_PROGRESS",
    "IMPORT_COMPLETE",
    "IMPORT_FAILED",
    "IMPORT_IN_PROGRESS",
    "IMPORT_ROLLBACK_COMPLETE",
    "IMPORT_ROLLBACK_FAILED",
    "IMPORT_ROLLBACK_IN_PROGRESS",
    "ROLLBACK_COMPLETE",
    "ROLLBACK_FAILED",
    "ROLLBACK_IN_PROGRESS",
    "UPDATE_COMPLETE",
    "UPDATE_FAILED",
    "UPDATE_IN_PROGRESS",
    "UPDATE_ROLLBACK_COMPLETE",
    "UPDATE_ROLLBACK_FAILED",
    "UPDATE_ROLLBACK_IN_PROGRESS",
]
StackCreateCompleteWaiterName = Literal["stack_create_complete"]
StackDeleteCompleteWaiterName = Literal["stack_delete_complete"]
StackDriftDetectionStatusType = Literal[
    "DETECTION_COMPLETE", "DETECTION_FAILED", "DETECTION_IN_PROGRESS"
]
StackDriftStatusType = Literal["DRIFTED", "IN_SYNC", "NOT_CHECKED", "UNKNOWN"]
StackExistsWaiterName = Literal["stack_exists"]
StackImportCompleteWaiterName = Literal["stack_import_complete"]
StackInstanceDetailedStatusType = Literal[
    "CANCELLED",
    "FAILED",
    "FAILED_IMPORT",
    "INOPERABLE",
    "PENDING",
    "RUNNING",
    "SKIPPED_SUSPENDED_ACCOUNT",
    "SUCCEEDED",
]
StackInstanceFilterNameType = Literal["DETAILED_STATUS", "DRIFT_STATUS", "LAST_OPERATION_ID"]
StackInstanceStatusType = Literal["CURRENT", "INOPERABLE", "OUTDATED"]
StackRefactorActionEntityType = Literal["RESOURCE", "STACK"]
StackRefactorActionTypeType = Literal["CREATE", "MOVE"]
StackRefactorCreateCompleteWaiterName = Literal["stack_refactor_create_complete"]
StackRefactorDetectionType = Literal["AUTO", "MANUAL"]
StackRefactorExecuteCompleteWaiterName = Literal["stack_refactor_execute_complete"]
StackRefactorExecutionStatusType = Literal[
    "AVAILABLE",
    "EXECUTE_COMPLETE",
    "EXECUTE_FAILED",
    "EXECUTE_IN_PROGRESS",
    "OBSOLETE",
    "ROLLBACK_COMPLETE",
    "ROLLBACK_FAILED",
    "ROLLBACK_IN_PROGRESS",
    "UNAVAILABLE",
]
StackRefactorStatusType = Literal[
    "CREATE_COMPLETE",
    "CREATE_FAILED",
    "CREATE_IN_PROGRESS",
    "DELETE_COMPLETE",
    "DELETE_FAILED",
    "DELETE_IN_PROGRESS",
]
StackResourceDriftStatusType = Literal["DELETED", "IN_SYNC", "MODIFIED", "NOT_CHECKED"]
StackRollbackCompleteWaiterName = Literal["stack_rollback_complete"]
StackSetDriftDetectionStatusType = Literal[
    "COMPLETED", "FAILED", "IN_PROGRESS", "PARTIAL_SUCCESS", "STOPPED"
]
StackSetDriftStatusType = Literal["DRIFTED", "IN_SYNC", "NOT_CHECKED"]
StackSetOperationActionType = Literal["CREATE", "DELETE", "DETECT_DRIFT", "UPDATE"]
StackSetOperationResultStatusType = Literal[
    "CANCELLED", "FAILED", "PENDING", "RUNNING", "SUCCEEDED"
]
StackSetOperationStatusType = Literal[
    "FAILED", "QUEUED", "RUNNING", "STOPPED", "STOPPING", "SUCCEEDED"
]
StackSetStatusType = Literal["ACTIVE", "DELETED"]
StackStatusType = Literal[
    "CREATE_COMPLETE",
    "CREATE_FAILED",
    "CREATE_IN_PROGRESS",
    "DELETE_COMPLETE",
    "DELETE_FAILED",
    "DELETE_IN_PROGRESS",
    "IMPORT_COMPLETE",
    "IMPORT_IN_PROGRESS",
    "IMPORT_ROLLBACK_COMPLETE",
    "IMPORT_ROLLBACK_FAILED",
    "IMPORT_ROLLBACK_IN_PROGRESS",
    "REVIEW_IN_PROGRESS",
    "ROLLBACK_COMPLETE",
    "ROLLBACK_FAILED",
    "ROLLBACK_IN_PROGRESS",
    "UPDATE_COMPLETE",
    "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
    "UPDATE_FAILED",
    "UPDATE_IN_PROGRESS",
    "UPDATE_ROLLBACK_COMPLETE",
    "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS",
    "UPDATE_ROLLBACK_FAILED",
    "UPDATE_ROLLBACK_IN_PROGRESS",
]
StackUpdateCompleteWaiterName = Literal["stack_update_complete"]
TemplateFormatType = Literal["JSON", "YAML"]
TemplateStageType = Literal["Original", "Processed"]
ThirdPartyTypeType = Literal["HOOK", "MODULE", "RESOURCE"]
TypeRegistrationCompleteWaiterName = Literal["type_registration_complete"]
TypeTestsStatusType = Literal["FAILED", "IN_PROGRESS", "NOT_TESTED", "PASSED"]
VersionBumpType = Literal["MAJOR", "MINOR"]
VisibilityType = Literal["PRIVATE", "PUBLIC"]
WarningTypeType = Literal[
    "MUTUALLY_EXCLUSIVE_PROPERTIES", "MUTUALLY_EXCLUSIVE_TYPES", "UNSUPPORTED_PROPERTIES"
]
CloudFormationServiceName = Literal["cloudformation"]
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
    "describe_account_limits",
    "describe_change_set",
    "describe_stack_events",
    "describe_stacks",
    "list_change_sets",
    "list_exports",
    "list_generated_templates",
    "list_imports",
    "list_resource_scan_related_resources",
    "list_resource_scan_resources",
    "list_resource_scans",
    "list_stack_instances",
    "list_stack_refactor_actions",
    "list_stack_refactors",
    "list_stack_resources",
    "list_stack_set_operation_results",
    "list_stack_set_operations",
    "list_stack_sets",
    "list_stacks",
    "list_types",
]
WaiterName = Literal[
    "change_set_create_complete",
    "stack_create_complete",
    "stack_delete_complete",
    "stack_exists",
    "stack_import_complete",
    "stack_refactor_create_complete",
    "stack_refactor_execute_complete",
    "stack_rollback_complete",
    "stack_update_complete",
    "type_registration_complete",
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
