"""
Type annotations for ce service literal definitions.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_ce/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from types_boto3_ce.literals import AccountScopeType

    data: AccountScopeType = "LINKED"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = (
    "AccountScopeType",
    "AnalysisStatusType",
    "AnalysisTypeType",
    "AnomalyFeedbackTypeType",
    "AnomalySubscriptionFrequencyType",
    "ApproximationDimensionType",
    "ContextType",
    "CostAllocationTagBackfillStatusType",
    "CostAllocationTagStatusType",
    "CostAllocationTagTypeType",
    "CostCategoryInheritedValueDimensionNameType",
    "CostCategoryRuleTypeType",
    "CostCategoryRuleVersionType",
    "CostCategorySplitChargeMethodType",
    "CostCategorySplitChargeRuleParameterTypeType",
    "CostCategoryStatusComponentType",
    "CostCategoryStatusType",
    "CostExplorerServiceName",
    "DimensionType",
    "ErrorCodeType",
    "FindingReasonCodeType",
    "GenerationStatusType",
    "GranularityType",
    "GroupDefinitionTypeType",
    "LookbackPeriodInDaysType",
    "MatchOptionType",
    "MetricType",
    "MonitorDimensionType",
    "MonitorTypeType",
    "NumericOperatorType",
    "OfferingClassType",
    "PaymentOptionType",
    "PlatformDifferenceType",
    "RecommendationTargetType",
    "ResourceServiceName",
    "RightsizingTypeType",
    "SavingsPlansDataTypeType",
    "ServiceName",
    "SortOrderType",
    "SubscriberStatusType",
    "SubscriberTypeType",
    "SupportedSavingsPlansTypeType",
    "TermInYearsType",
)

AccountScopeType = Literal["LINKED", "PAYER"]
AnalysisStatusType = Literal["FAILED", "PROCESSING", "SUCCEEDED"]
AnalysisTypeType = Literal["CUSTOM_COMMITMENT", "MAX_SAVINGS"]
AnomalyFeedbackTypeType = Literal["NO", "PLANNED_ACTIVITY", "YES"]
AnomalySubscriptionFrequencyType = Literal["DAILY", "IMMEDIATE", "WEEKLY"]
ApproximationDimensionType = Literal["RESOURCE", "SERVICE"]
ContextType = Literal["COST_AND_USAGE", "RESERVATIONS", "SAVINGS_PLANS"]
CostAllocationTagBackfillStatusType = Literal["FAILED", "PROCESSING", "SUCCEEDED"]
CostAllocationTagStatusType = Literal["Active", "Inactive"]
CostAllocationTagTypeType = Literal["AWSGenerated", "UserDefined"]
CostCategoryInheritedValueDimensionNameType = Literal["LINKED_ACCOUNT_NAME", "TAG"]
CostCategoryRuleTypeType = Literal["INHERITED_VALUE", "REGULAR"]
CostCategoryRuleVersionType = Literal["CostCategoryExpression.v1"]
CostCategorySplitChargeMethodType = Literal["EVEN", "FIXED", "PROPORTIONAL"]
CostCategorySplitChargeRuleParameterTypeType = Literal["ALLOCATION_PERCENTAGES"]
CostCategoryStatusComponentType = Literal["COST_EXPLORER"]
CostCategoryStatusType = Literal["APPLIED", "PROCESSING"]
DimensionType = Literal[
    "AGREEMENT_END_DATE_TIME_AFTER",
    "AGREEMENT_END_DATE_TIME_BEFORE",
    "ANOMALY_TOTAL_IMPACT_ABSOLUTE",
    "ANOMALY_TOTAL_IMPACT_PERCENTAGE",
    "AZ",
    "BILLING_ENTITY",
    "CACHE_ENGINE",
    "DATABASE_ENGINE",
    "DEPLOYMENT_OPTION",
    "INSTANCE_TYPE",
    "INSTANCE_TYPE_FAMILY",
    "INVOICING_ENTITY",
    "LEGAL_ENTITY_NAME",
    "LINKED_ACCOUNT",
    "LINKED_ACCOUNT_NAME",
    "OPERATING_SYSTEM",
    "OPERATION",
    "PAYMENT_OPTION",
    "PLATFORM",
    "PURCHASE_TYPE",
    "RECORD_TYPE",
    "REGION",
    "RESERVATION_ID",
    "RESOURCE_ID",
    "RIGHTSIZING_TYPE",
    "SAVINGS_PLANS_TYPE",
    "SAVINGS_PLAN_ARN",
    "SCOPE",
    "SERVICE",
    "SERVICE_CODE",
    "SUBSCRIPTION_ID",
    "TENANCY",
    "USAGE_TYPE",
    "USAGE_TYPE_GROUP",
]
ErrorCodeType = Literal[
    "INTERNAL_FAILURE",
    "INVALID_ACCOUNT_ID",
    "INVALID_SAVINGS_PLANS_TO_ADD",
    "INVALID_SAVINGS_PLANS_TO_EXCLUDE",
    "NO_USAGE_FOUND",
]
FindingReasonCodeType = Literal[
    "CPU_OVER_PROVISIONED",
    "CPU_UNDER_PROVISIONED",
    "DISK_IOPS_OVER_PROVISIONED",
    "DISK_IOPS_UNDER_PROVISIONED",
    "DISK_THROUGHPUT_OVER_PROVISIONED",
    "DISK_THROUGHPUT_UNDER_PROVISIONED",
    "EBS_IOPS_OVER_PROVISIONED",
    "EBS_IOPS_UNDER_PROVISIONED",
    "EBS_THROUGHPUT_OVER_PROVISIONED",
    "EBS_THROUGHPUT_UNDER_PROVISIONED",
    "MEMORY_OVER_PROVISIONED",
    "MEMORY_UNDER_PROVISIONED",
    "NETWORK_BANDWIDTH_OVER_PROVISIONED",
    "NETWORK_BANDWIDTH_UNDER_PROVISIONED",
    "NETWORK_PPS_OVER_PROVISIONED",
    "NETWORK_PPS_UNDER_PROVISIONED",
]
GenerationStatusType = Literal["FAILED", "PROCESSING", "SUCCEEDED"]
GranularityType = Literal["DAILY", "HOURLY", "MONTHLY"]
GroupDefinitionTypeType = Literal["COST_CATEGORY", "DIMENSION", "TAG"]
LookbackPeriodInDaysType = Literal["SEVEN_DAYS", "SIXTY_DAYS", "THIRTY_DAYS"]
MatchOptionType = Literal[
    "ABSENT",
    "CASE_INSENSITIVE",
    "CASE_SENSITIVE",
    "CONTAINS",
    "ENDS_WITH",
    "EQUALS",
    "GREATER_THAN_OR_EQUAL",
    "STARTS_WITH",
]
MetricType = Literal[
    "AMORTIZED_COST",
    "BLENDED_COST",
    "NET_AMORTIZED_COST",
    "NET_UNBLENDED_COST",
    "NORMALIZED_USAGE_AMOUNT",
    "UNBLENDED_COST",
    "USAGE_QUANTITY",
]
MonitorDimensionType = Literal["SERVICE"]
MonitorTypeType = Literal["CUSTOM", "DIMENSIONAL"]
NumericOperatorType = Literal[
    "BETWEEN", "EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL"
]
OfferingClassType = Literal["CONVERTIBLE", "STANDARD"]
PaymentOptionType = Literal[
    "ALL_UPFRONT",
    "HEAVY_UTILIZATION",
    "LIGHT_UTILIZATION",
    "MEDIUM_UTILIZATION",
    "NO_UPFRONT",
    "PARTIAL_UPFRONT",
]
PlatformDifferenceType = Literal[
    "HYPERVISOR",
    "INSTANCE_STORE_AVAILABILITY",
    "NETWORK_INTERFACE",
    "STORAGE_INTERFACE",
    "VIRTUALIZATION_TYPE",
]
RecommendationTargetType = Literal["CROSS_INSTANCE_FAMILY", "SAME_INSTANCE_FAMILY"]
RightsizingTypeType = Literal["MODIFY", "TERMINATE"]
SavingsPlansDataTypeType = Literal["AMORTIZED_COMMITMENT", "ATTRIBUTES", "SAVINGS", "UTILIZATION"]
SortOrderType = Literal["ASCENDING", "DESCENDING"]
SubscriberStatusType = Literal["CONFIRMED", "DECLINED"]
SubscriberTypeType = Literal["EMAIL", "SNS"]
SupportedSavingsPlansTypeType = Literal["COMPUTE_SP", "EC2_INSTANCE_SP", "SAGEMAKER_SP"]
TermInYearsType = Literal["ONE_YEAR", "THREE_YEARS"]
CostExplorerServiceName = Literal["ce"]
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
