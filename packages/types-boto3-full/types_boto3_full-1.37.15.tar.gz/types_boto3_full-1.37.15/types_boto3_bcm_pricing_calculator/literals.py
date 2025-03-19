"""
Type annotations for bcm-pricing-calculator service literal definitions.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_bcm_pricing_calculator/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from types_boto3_bcm_pricing_calculator.literals import BatchCreateBillScenarioCommitmentModificationErrorCodeType

    data: BatchCreateBillScenarioCommitmentModificationErrorCodeType = "CONFLICT"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "BatchCreateBillScenarioCommitmentModificationErrorCodeType",
    "BatchCreateBillScenarioUsageModificationErrorCodeType",
    "BatchCreateWorkloadEstimateUsageCodeType",
    "BatchDeleteBillScenarioCommitmentModificationErrorCodeType",
    "BatchDeleteBillScenarioUsageModificationErrorCodeType",
    "BatchUpdateBillScenarioCommitmentModificationErrorCodeType",
    "BatchUpdateBillScenarioUsageModificationErrorCodeType",
    "BillEstimateStatusType",
    "BillScenarioStatusType",
    "BillingandCostManagementPricingCalculatorServiceName",
    "CurrencyCodeType",
    "ListBillEstimateCommitmentsPaginatorName",
    "ListBillEstimateInputCommitmentModificationsPaginatorName",
    "ListBillEstimateInputUsageModificationsPaginatorName",
    "ListBillEstimateLineItemsFilterNameType",
    "ListBillEstimateLineItemsPaginatorName",
    "ListBillEstimatesFilterNameType",
    "ListBillEstimatesPaginatorName",
    "ListBillScenarioCommitmentModificationsPaginatorName",
    "ListBillScenarioUsageModificationsPaginatorName",
    "ListBillScenariosFilterNameType",
    "ListBillScenariosPaginatorName",
    "ListUsageFilterNameType",
    "ListWorkloadEstimateUsagePaginatorName",
    "ListWorkloadEstimatesFilterNameType",
    "ListWorkloadEstimatesPaginatorName",
    "MatchOptionType",
    "PaginatorName",
    "PurchaseAgreementTypeType",
    "RateTypeType",
    "ResourceServiceName",
    "ServiceName",
    "WorkloadEstimateCostStatusType",
    "WorkloadEstimateRateTypeType",
    "WorkloadEstimateStatusType",
    "WorkloadEstimateUpdateUsageErrorCodeType",
)


BatchCreateBillScenarioCommitmentModificationErrorCodeType = Literal[
    "CONFLICT", "INTERNAL_SERVER_ERROR", "INVALID_ACCOUNT"
]
BatchCreateBillScenarioUsageModificationErrorCodeType = Literal[
    "BAD_REQUEST", "CONFLICT", "INTERNAL_SERVER_ERROR", "NOT_FOUND"
]
BatchCreateWorkloadEstimateUsageCodeType = Literal[
    "BAD_REQUEST", "CONFLICT", "INTERNAL_SERVER_ERROR", "NOT_FOUND"
]
BatchDeleteBillScenarioCommitmentModificationErrorCodeType = Literal[
    "BAD_REQUEST", "CONFLICT", "INTERNAL_SERVER_ERROR"
]
BatchDeleteBillScenarioUsageModificationErrorCodeType = Literal[
    "BAD_REQUEST", "CONFLICT", "INTERNAL_SERVER_ERROR"
]
BatchUpdateBillScenarioCommitmentModificationErrorCodeType = Literal[
    "BAD_REQUEST", "CONFLICT", "INTERNAL_SERVER_ERROR", "NOT_FOUND"
]
BatchUpdateBillScenarioUsageModificationErrorCodeType = Literal[
    "BAD_REQUEST", "CONFLICT", "INTERNAL_SERVER_ERROR", "NOT_FOUND"
]
BillEstimateStatusType = Literal["COMPLETE", "FAILED", "IN_PROGRESS"]
BillScenarioStatusType = Literal["FAILED", "LOCKED", "READY"]
CurrencyCodeType = Literal["USD"]
ListBillEstimateCommitmentsPaginatorName = Literal["list_bill_estimate_commitments"]
ListBillEstimateInputCommitmentModificationsPaginatorName = Literal[
    "list_bill_estimate_input_commitment_modifications"
]
ListBillEstimateInputUsageModificationsPaginatorName = Literal[
    "list_bill_estimate_input_usage_modifications"
]
ListBillEstimateLineItemsFilterNameType = Literal[
    "LINE_ITEM_TYPE", "LOCATION", "OPERATION", "SERVICE_CODE", "USAGE_ACCOUNT_ID", "USAGE_TYPE"
]
ListBillEstimateLineItemsPaginatorName = Literal["list_bill_estimate_line_items"]
ListBillEstimatesFilterNameType = Literal["NAME", "STATUS"]
ListBillEstimatesPaginatorName = Literal["list_bill_estimates"]
ListBillScenarioCommitmentModificationsPaginatorName = Literal[
    "list_bill_scenario_commitment_modifications"
]
ListBillScenarioUsageModificationsPaginatorName = Literal["list_bill_scenario_usage_modifications"]
ListBillScenariosFilterNameType = Literal["NAME", "STATUS"]
ListBillScenariosPaginatorName = Literal["list_bill_scenarios"]
ListUsageFilterNameType = Literal[
    "HISTORICAL_LOCATION",
    "HISTORICAL_OPERATION",
    "HISTORICAL_SERVICE_CODE",
    "HISTORICAL_USAGE_ACCOUNT_ID",
    "HISTORICAL_USAGE_TYPE",
    "LOCATION",
    "OPERATION",
    "SERVICE_CODE",
    "USAGE_ACCOUNT_ID",
    "USAGE_GROUP",
    "USAGE_TYPE",
]
ListWorkloadEstimateUsagePaginatorName = Literal["list_workload_estimate_usage"]
ListWorkloadEstimatesFilterNameType = Literal["NAME", "STATUS"]
ListWorkloadEstimatesPaginatorName = Literal["list_workload_estimates"]
MatchOptionType = Literal["CONTAINS", "EQUALS", "STARTS_WITH"]
PurchaseAgreementTypeType = Literal["RESERVED_INSTANCE", "SAVINGS_PLANS"]
RateTypeType = Literal["AFTER_DISCOUNTS", "BEFORE_DISCOUNTS"]
WorkloadEstimateCostStatusType = Literal["INVALID", "STALE", "VALID"]
WorkloadEstimateRateTypeType = Literal["AFTER_DISCOUNTS", "BEFORE_DISCOUNTS"]
WorkloadEstimateStatusType = Literal["ACTION_NEEDED", "INVALID", "UPDATING", "VALID"]
WorkloadEstimateUpdateUsageErrorCodeType = Literal[
    "BAD_REQUEST", "CONFLICT", "INTERNAL_SERVER_ERROR", "NOT_FOUND"
]
BillingandCostManagementPricingCalculatorServiceName = Literal["bcm-pricing-calculator"]
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
    "list_bill_estimate_commitments",
    "list_bill_estimate_input_commitment_modifications",
    "list_bill_estimate_input_usage_modifications",
    "list_bill_estimate_line_items",
    "list_bill_estimates",
    "list_bill_scenario_commitment_modifications",
    "list_bill_scenario_usage_modifications",
    "list_bill_scenarios",
    "list_workload_estimate_usage",
    "list_workload_estimates",
]
