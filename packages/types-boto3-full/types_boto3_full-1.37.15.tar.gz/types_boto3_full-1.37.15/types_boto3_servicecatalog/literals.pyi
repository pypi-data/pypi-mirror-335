"""
Type annotations for servicecatalog service literal definitions.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_servicecatalog/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from types_boto3_servicecatalog.literals import AccessLevelFilterKeyType

    data: AccessLevelFilterKeyType = "Account"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = (
    "AccessLevelFilterKeyType",
    "AccessStatusType",
    "ChangeActionType",
    "CopyOptionType",
    "CopyProductStatusType",
    "DescribePortfolioShareTypeType",
    "EngineWorkflowStatusType",
    "EvaluationTypeType",
    "LastSyncStatusType",
    "ListAcceptedPortfolioSharesPaginatorName",
    "ListConstraintsForPortfolioPaginatorName",
    "ListLaunchPathsPaginatorName",
    "ListOrganizationPortfolioAccessPaginatorName",
    "ListPortfoliosForProductPaginatorName",
    "ListPortfoliosPaginatorName",
    "ListPrincipalsForPortfolioPaginatorName",
    "ListProvisionedProductPlansPaginatorName",
    "ListProvisioningArtifactsForServiceActionPaginatorName",
    "ListRecordHistoryPaginatorName",
    "ListResourcesForTagOptionPaginatorName",
    "ListServiceActionsForProvisioningArtifactPaginatorName",
    "ListServiceActionsPaginatorName",
    "ListTagOptionsPaginatorName",
    "OrganizationNodeTypeType",
    "PaginatorName",
    "PortfolioShareTypeType",
    "PrincipalTypeType",
    "ProductSourceType",
    "ProductTypeType",
    "ProductViewFilterByType",
    "ProductViewSortByType",
    "PropertyKeyType",
    "ProvisionedProductPlanStatusType",
    "ProvisionedProductPlanTypeType",
    "ProvisionedProductStatusType",
    "ProvisionedProductViewFilterByType",
    "ProvisioningArtifactGuidanceType",
    "ProvisioningArtifactPropertyNameType",
    "ProvisioningArtifactTypeType",
    "RecordStatusType",
    "RegionName",
    "ReplacementType",
    "RequiresRecreationType",
    "ResourceAttributeType",
    "ResourceServiceName",
    "ScanProvisionedProductsPaginatorName",
    "SearchProductsAsAdminPaginatorName",
    "ServiceActionAssociationErrorCodeType",
    "ServiceActionDefinitionKeyType",
    "ServiceActionDefinitionTypeType",
    "ServiceCatalogServiceName",
    "ServiceName",
    "ShareStatusType",
    "SortOrderType",
    "SourceTypeType",
    "StackInstanceStatusType",
    "StackSetOperationTypeType",
    "StatusType",
)

AccessLevelFilterKeyType = Literal["Account", "Role", "User"]
AccessStatusType = Literal["DISABLED", "ENABLED", "UNDER_CHANGE"]
ChangeActionType = Literal["ADD", "MODIFY", "REMOVE"]
CopyOptionType = Literal["CopyTags"]
CopyProductStatusType = Literal["FAILED", "IN_PROGRESS", "SUCCEEDED"]
DescribePortfolioShareTypeType = Literal[
    "ACCOUNT", "ORGANIZATION", "ORGANIZATIONAL_UNIT", "ORGANIZATION_MEMBER_ACCOUNT"
]
EngineWorkflowStatusType = Literal["FAILED", "SUCCEEDED"]
EvaluationTypeType = Literal["DYNAMIC", "STATIC"]
LastSyncStatusType = Literal["FAILED", "SUCCEEDED"]
ListAcceptedPortfolioSharesPaginatorName = Literal["list_accepted_portfolio_shares"]
ListConstraintsForPortfolioPaginatorName = Literal["list_constraints_for_portfolio"]
ListLaunchPathsPaginatorName = Literal["list_launch_paths"]
ListOrganizationPortfolioAccessPaginatorName = Literal["list_organization_portfolio_access"]
ListPortfoliosForProductPaginatorName = Literal["list_portfolios_for_product"]
ListPortfoliosPaginatorName = Literal["list_portfolios"]
ListPrincipalsForPortfolioPaginatorName = Literal["list_principals_for_portfolio"]
ListProvisionedProductPlansPaginatorName = Literal["list_provisioned_product_plans"]
ListProvisioningArtifactsForServiceActionPaginatorName = Literal[
    "list_provisioning_artifacts_for_service_action"
]
ListRecordHistoryPaginatorName = Literal["list_record_history"]
ListResourcesForTagOptionPaginatorName = Literal["list_resources_for_tag_option"]
ListServiceActionsForProvisioningArtifactPaginatorName = Literal[
    "list_service_actions_for_provisioning_artifact"
]
ListServiceActionsPaginatorName = Literal["list_service_actions"]
ListTagOptionsPaginatorName = Literal["list_tag_options"]
OrganizationNodeTypeType = Literal["ACCOUNT", "ORGANIZATION", "ORGANIZATIONAL_UNIT"]
PortfolioShareTypeType = Literal["AWS_ORGANIZATIONS", "AWS_SERVICECATALOG", "IMPORTED"]
PrincipalTypeType = Literal["IAM", "IAM_PATTERN"]
ProductSourceType = Literal["ACCOUNT"]
ProductTypeType = Literal[
    "CLOUD_FORMATION_TEMPLATE",
    "EXTERNAL",
    "MARKETPLACE",
    "TERRAFORM_CLOUD",
    "TERRAFORM_OPEN_SOURCE",
]
ProductViewFilterByType = Literal["FullTextSearch", "Owner", "ProductType", "SourceProductId"]
ProductViewSortByType = Literal["CreationDate", "Title", "VersionCount"]
PropertyKeyType = Literal["LAUNCH_ROLE", "OWNER"]
ProvisionedProductPlanStatusType = Literal[
    "CREATE_FAILED",
    "CREATE_IN_PROGRESS",
    "CREATE_SUCCESS",
    "EXECUTE_FAILED",
    "EXECUTE_IN_PROGRESS",
    "EXECUTE_SUCCESS",
]
ProvisionedProductPlanTypeType = Literal["CLOUDFORMATION"]
ProvisionedProductStatusType = Literal[
    "AVAILABLE", "ERROR", "PLAN_IN_PROGRESS", "TAINTED", "UNDER_CHANGE"
]
ProvisionedProductViewFilterByType = Literal["SearchQuery"]
ProvisioningArtifactGuidanceType = Literal["DEFAULT", "DEPRECATED"]
ProvisioningArtifactPropertyNameType = Literal["Id"]
ProvisioningArtifactTypeType = Literal[
    "CLOUD_FORMATION_TEMPLATE",
    "EXTERNAL",
    "MARKETPLACE_AMI",
    "MARKETPLACE_CAR",
    "TERRAFORM_CLOUD",
    "TERRAFORM_OPEN_SOURCE",
]
RecordStatusType = Literal["CREATED", "FAILED", "IN_PROGRESS", "IN_PROGRESS_IN_ERROR", "SUCCEEDED"]
ReplacementType = Literal["CONDITIONAL", "FALSE", "TRUE"]
RequiresRecreationType = Literal["ALWAYS", "CONDITIONALLY", "NEVER"]
ResourceAttributeType = Literal[
    "CREATIONPOLICY", "DELETIONPOLICY", "METADATA", "PROPERTIES", "TAGS", "UPDATEPOLICY"
]
ScanProvisionedProductsPaginatorName = Literal["scan_provisioned_products"]
SearchProductsAsAdminPaginatorName = Literal["search_products_as_admin"]
ServiceActionAssociationErrorCodeType = Literal[
    "DUPLICATE_RESOURCE",
    "INTERNAL_FAILURE",
    "INVALID_PARAMETER",
    "LIMIT_EXCEEDED",
    "RESOURCE_NOT_FOUND",
    "THROTTLING",
]
ServiceActionDefinitionKeyType = Literal["AssumeRole", "Name", "Parameters", "Version"]
ServiceActionDefinitionTypeType = Literal["SSM_AUTOMATION"]
ShareStatusType = Literal[
    "COMPLETED", "COMPLETED_WITH_ERRORS", "ERROR", "IN_PROGRESS", "NOT_STARTED"
]
SortOrderType = Literal["ASCENDING", "DESCENDING"]
SourceTypeType = Literal["CODESTAR"]
StackInstanceStatusType = Literal["CURRENT", "INOPERABLE", "OUTDATED"]
StackSetOperationTypeType = Literal["CREATE", "DELETE", "UPDATE"]
StatusType = Literal["AVAILABLE", "CREATING", "FAILED"]
ServiceCatalogServiceName = Literal["servicecatalog"]
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
    "list_accepted_portfolio_shares",
    "list_constraints_for_portfolio",
    "list_launch_paths",
    "list_organization_portfolio_access",
    "list_portfolios",
    "list_portfolios_for_product",
    "list_principals_for_portfolio",
    "list_provisioned_product_plans",
    "list_provisioning_artifacts_for_service_action",
    "list_record_history",
    "list_resources_for_tag_option",
    "list_service_actions",
    "list_service_actions_for_provisioning_artifact",
    "list_tag_options",
    "scan_provisioned_products",
    "search_products_as_admin",
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
    "ca-central-1",
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
