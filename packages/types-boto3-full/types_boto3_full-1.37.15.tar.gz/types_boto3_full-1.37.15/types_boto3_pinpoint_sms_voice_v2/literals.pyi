"""
Type annotations for pinpoint-sms-voice-v2 service literal definitions.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_pinpoint_sms_voice_v2/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from types_boto3_pinpoint_sms_voice_v2.literals import AccountAttributeNameType

    data: AccountAttributeNameType = "ACCOUNT_TIER"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = (
    "AccountAttributeNameType",
    "AccountLimitNameType",
    "AttachmentStatusType",
    "AttachmentUploadErrorReasonType",
    "ConfigurationSetFilterNameType",
    "DescribeAccountAttributesPaginatorName",
    "DescribeAccountLimitsPaginatorName",
    "DescribeConfigurationSetsPaginatorName",
    "DescribeKeywordsPaginatorName",
    "DescribeOptOutListsPaginatorName",
    "DescribeOptedOutNumbersPaginatorName",
    "DescribePhoneNumbersPaginatorName",
    "DescribePoolsPaginatorName",
    "DescribeProtectConfigurationsPaginatorName",
    "DescribeRegistrationAttachmentsPaginatorName",
    "DescribeRegistrationFieldDefinitionsPaginatorName",
    "DescribeRegistrationFieldValuesPaginatorName",
    "DescribeRegistrationSectionDefinitionsPaginatorName",
    "DescribeRegistrationTypeDefinitionsPaginatorName",
    "DescribeRegistrationVersionsPaginatorName",
    "DescribeRegistrationsPaginatorName",
    "DescribeSenderIdsPaginatorName",
    "DescribeSpendLimitsPaginatorName",
    "DescribeVerifiedDestinationNumbersPaginatorName",
    "DestinationCountryParameterKeyType",
    "EventTypeType",
    "FieldRequirementType",
    "FieldTypeType",
    "KeywordActionType",
    "KeywordFilterNameType",
    "LanguageCodeType",
    "ListPoolOriginationIdentitiesPaginatorName",
    "ListProtectConfigurationRuleSetNumberOverridesPaginatorName",
    "ListRegistrationAssociationsPaginatorName",
    "MessageFeedbackStatusType",
    "MessageTypeType",
    "NumberCapabilityType",
    "NumberStatusType",
    "NumberTypeType",
    "OptedOutFilterNameType",
    "OwnerType",
    "PaginatorName",
    "PhoneNumberFilterNameType",
    "PinpointSMSVoiceV2ServiceName",
    "PoolFilterNameType",
    "PoolOriginationIdentitiesFilterNameType",
    "PoolStatusType",
    "ProtectConfigurationFilterNameType",
    "ProtectConfigurationRuleOverrideActionType",
    "ProtectConfigurationRuleSetNumberOverrideFilterNameType",
    "ProtectStatusType",
    "RegionName",
    "RegistrationAssociationBehaviorType",
    "RegistrationAssociationFilterNameType",
    "RegistrationAttachmentFilterNameType",
    "RegistrationDisassociationBehaviorType",
    "RegistrationFilterNameType",
    "RegistrationStatusType",
    "RegistrationTypeFilterNameType",
    "RegistrationVersionFilterNameType",
    "RegistrationVersionStatusType",
    "RequestableNumberTypeType",
    "ResourceServiceName",
    "SenderIdFilterNameType",
    "ServiceName",
    "SpendLimitNameType",
    "VerificationChannelType",
    "VerificationStatusType",
    "VerifiedDestinationNumberFilterNameType",
    "VoiceIdType",
    "VoiceMessageBodyTextTypeType",
)

AccountAttributeNameType = Literal["ACCOUNT_TIER", "DEFAULT_PROTECT_CONFIGURATION_ID"]
AccountLimitNameType = Literal[
    "CONFIGURATION_SETS",
    "OPT_OUT_LISTS",
    "PHONE_NUMBERS",
    "POOLS",
    "REGISTRATIONS",
    "REGISTRATION_ATTACHMENTS",
    "SENDER_IDS",
    "VERIFIED_DESTINATION_NUMBERS",
]
AttachmentStatusType = Literal["DELETED", "UPLOAD_COMPLETE", "UPLOAD_FAILED", "UPLOAD_IN_PROGRESS"]
AttachmentUploadErrorReasonType = Literal["INTERNAL_ERROR"]
ConfigurationSetFilterNameType = Literal[
    "default-message-feedback-enabled",
    "default-message-type",
    "default-sender-id",
    "event-destination-name",
    "matching-event-types",
    "protect-configuration-id",
]
DescribeAccountAttributesPaginatorName = Literal["describe_account_attributes"]
DescribeAccountLimitsPaginatorName = Literal["describe_account_limits"]
DescribeConfigurationSetsPaginatorName = Literal["describe_configuration_sets"]
DescribeKeywordsPaginatorName = Literal["describe_keywords"]
DescribeOptOutListsPaginatorName = Literal["describe_opt_out_lists"]
DescribeOptedOutNumbersPaginatorName = Literal["describe_opted_out_numbers"]
DescribePhoneNumbersPaginatorName = Literal["describe_phone_numbers"]
DescribePoolsPaginatorName = Literal["describe_pools"]
DescribeProtectConfigurationsPaginatorName = Literal["describe_protect_configurations"]
DescribeRegistrationAttachmentsPaginatorName = Literal["describe_registration_attachments"]
DescribeRegistrationFieldDefinitionsPaginatorName = Literal[
    "describe_registration_field_definitions"
]
DescribeRegistrationFieldValuesPaginatorName = Literal["describe_registration_field_values"]
DescribeRegistrationSectionDefinitionsPaginatorName = Literal[
    "describe_registration_section_definitions"
]
DescribeRegistrationTypeDefinitionsPaginatorName = Literal["describe_registration_type_definitions"]
DescribeRegistrationVersionsPaginatorName = Literal["describe_registration_versions"]
DescribeRegistrationsPaginatorName = Literal["describe_registrations"]
DescribeSenderIdsPaginatorName = Literal["describe_sender_ids"]
DescribeSpendLimitsPaginatorName = Literal["describe_spend_limits"]
DescribeVerifiedDestinationNumbersPaginatorName = Literal["describe_verified_destination_numbers"]
DestinationCountryParameterKeyType = Literal["IN_ENTITY_ID", "IN_TEMPLATE_ID"]
EventTypeType = Literal[
    "ALL",
    "MEDIA_ALL",
    "MEDIA_BLOCKED",
    "MEDIA_CARRIER_BLOCKED",
    "MEDIA_CARRIER_UNREACHABLE",
    "MEDIA_DELIVERED",
    "MEDIA_FILE_INACCESSIBLE",
    "MEDIA_FILE_SIZE_EXCEEDED",
    "MEDIA_FILE_TYPE_UNSUPPORTED",
    "MEDIA_INVALID",
    "MEDIA_INVALID_MESSAGE",
    "MEDIA_PENDING",
    "MEDIA_QUEUED",
    "MEDIA_SPAM",
    "MEDIA_SUCCESSFUL",
    "MEDIA_TTL_EXPIRED",
    "MEDIA_UNKNOWN",
    "MEDIA_UNREACHABLE",
    "TEXT_ALL",
    "TEXT_BLOCKED",
    "TEXT_CARRIER_BLOCKED",
    "TEXT_CARRIER_UNREACHABLE",
    "TEXT_DELIVERED",
    "TEXT_INVALID",
    "TEXT_INVALID_MESSAGE",
    "TEXT_PENDING",
    "TEXT_PROTECT_BLOCKED",
    "TEXT_QUEUED",
    "TEXT_SENT",
    "TEXT_SPAM",
    "TEXT_SUCCESSFUL",
    "TEXT_TTL_EXPIRED",
    "TEXT_UNKNOWN",
    "TEXT_UNREACHABLE",
    "VOICE_ALL",
    "VOICE_ANSWERED",
    "VOICE_BUSY",
    "VOICE_COMPLETED",
    "VOICE_FAILED",
    "VOICE_INITIATED",
    "VOICE_NO_ANSWER",
    "VOICE_RINGING",
    "VOICE_TTL_EXPIRED",
]
FieldRequirementType = Literal["CONDITIONAL", "OPTIONAL", "REQUIRED"]
FieldTypeType = Literal["ATTACHMENT", "SELECT", "TEXT"]
KeywordActionType = Literal["AUTOMATIC_RESPONSE", "OPT_IN", "OPT_OUT"]
KeywordFilterNameType = Literal["keyword-action"]
LanguageCodeType = Literal[
    "DE_DE",
    "EN_GB",
    "EN_US",
    "ES_419",
    "ES_ES",
    "FR_CA",
    "FR_FR",
    "IT_IT",
    "JA_JP",
    "KO_KR",
    "PT_BR",
    "ZH_CN",
    "ZH_TW",
]
ListPoolOriginationIdentitiesPaginatorName = Literal["list_pool_origination_identities"]
ListProtectConfigurationRuleSetNumberOverridesPaginatorName = Literal[
    "list_protect_configuration_rule_set_number_overrides"
]
ListRegistrationAssociationsPaginatorName = Literal["list_registration_associations"]
MessageFeedbackStatusType = Literal["FAILED", "RECEIVED"]
MessageTypeType = Literal["PROMOTIONAL", "TRANSACTIONAL"]
NumberCapabilityType = Literal["MMS", "SMS", "VOICE"]
NumberStatusType = Literal["ACTIVE", "ASSOCIATING", "DELETED", "DISASSOCIATING", "PENDING"]
NumberTypeType = Literal["LONG_CODE", "SHORT_CODE", "SIMULATOR", "TEN_DLC", "TOLL_FREE"]
OptedOutFilterNameType = Literal["end-user-opted-out"]
OwnerType = Literal["SELF", "SHARED"]
PhoneNumberFilterNameType = Literal[
    "deletion-protection-enabled",
    "iso-country-code",
    "message-type",
    "number-capability",
    "number-type",
    "opt-out-list-name",
    "self-managed-opt-outs-enabled",
    "status",
    "two-way-channel-arn",
    "two-way-enabled",
]
PoolFilterNameType = Literal[
    "deletion-protection-enabled",
    "message-type",
    "opt-out-list-name",
    "self-managed-opt-outs-enabled",
    "shared-routes-enabled",
    "status",
    "two-way-channel-arn",
    "two-way-enabled",
]
PoolOriginationIdentitiesFilterNameType = Literal["iso-country-code", "number-capability"]
PoolStatusType = Literal["ACTIVE", "CREATING", "DELETING"]
ProtectConfigurationFilterNameType = Literal["account-default", "deletion-protection-enabled"]
ProtectConfigurationRuleOverrideActionType = Literal["ALLOW", "BLOCK"]
ProtectConfigurationRuleSetNumberOverrideFilterNameType = Literal[
    "action",
    "created-after",
    "created-before",
    "destination-phone-number-begins-with",
    "expires-after",
    "expires-before",
    "iso-country-code",
]
ProtectStatusType = Literal["ALLOW", "BLOCK"]
RegistrationAssociationBehaviorType = Literal[
    "ASSOCIATE_AFTER_COMPLETE", "ASSOCIATE_BEFORE_SUBMIT", "ASSOCIATE_ON_APPROVAL"
]
RegistrationAssociationFilterNameType = Literal["iso-country-code", "resource-type"]
RegistrationAttachmentFilterNameType = Literal["attachment-status"]
RegistrationDisassociationBehaviorType = Literal[
    "DELETE_REGISTRATION_DISASSOCIATES",
    "DISASSOCIATE_ALL_ALLOWS_DELETE_REGISTRATION",
    "DISASSOCIATE_ALL_CLOSES_REGISTRATION",
]
RegistrationFilterNameType = Literal["registration-status", "registration-type"]
RegistrationStatusType = Literal[
    "CLOSED",
    "COMPLETE",
    "CREATED",
    "DELETED",
    "PROVISIONING",
    "REQUIRES_AUTHENTICATION",
    "REQUIRES_UPDATES",
    "REVIEWING",
    "SUBMITTED",
]
RegistrationTypeFilterNameType = Literal[
    "supported-association-iso-country-code", "supported-association-resource-type"
]
RegistrationVersionFilterNameType = Literal["registration-version-status"]
RegistrationVersionStatusType = Literal[
    "APPROVED",
    "ARCHIVED",
    "DENIED",
    "DISCARDED",
    "DRAFT",
    "REQUIRES_AUTHENTICATION",
    "REVIEWING",
    "REVOKED",
    "SUBMITTED",
]
RequestableNumberTypeType = Literal["LONG_CODE", "SIMULATOR", "TEN_DLC", "TOLL_FREE"]
SenderIdFilterNameType = Literal[
    "deletion-protection-enabled", "iso-country-code", "message-type", "registered", "sender-id"
]
SpendLimitNameType = Literal[
    "MEDIA_MESSAGE_MONTHLY_SPEND_LIMIT",
    "TEXT_MESSAGE_MONTHLY_SPEND_LIMIT",
    "VOICE_MESSAGE_MONTHLY_SPEND_LIMIT",
]
VerificationChannelType = Literal["TEXT", "VOICE"]
VerificationStatusType = Literal["PENDING", "VERIFIED"]
VerifiedDestinationNumberFilterNameType = Literal["status"]
VoiceIdType = Literal[
    "AMY",
    "ASTRID",
    "BIANCA",
    "BRIAN",
    "CAMILA",
    "CARLA",
    "CARMEN",
    "CELINE",
    "CHANTAL",
    "CONCHITA",
    "CRISTIANO",
    "DORA",
    "EMMA",
    "ENRIQUE",
    "EWA",
    "FILIZ",
    "GERAINT",
    "GIORGIO",
    "GWYNETH",
    "HANS",
    "INES",
    "IVY",
    "JACEK",
    "JAN",
    "JOANNA",
    "JOEY",
    "JUSTIN",
    "KARL",
    "KENDRA",
    "KIMBERLY",
    "LEA",
    "LIV",
    "LOTTE",
    "LUCIA",
    "LUPE",
    "MADS",
    "MAJA",
    "MARLENE",
    "MATHIEU",
    "MATTHEW",
    "MAXIM",
    "MIA",
    "MIGUEL",
    "MIZUKI",
    "NAJA",
    "NICOLE",
    "PENELOPE",
    "RAVEENA",
    "RICARDO",
    "RUBEN",
    "RUSSELL",
    "SALLI",
    "SEOYEON",
    "TAKUMI",
    "TATYANA",
    "VICKI",
    "VITORIA",
    "ZEINA",
    "ZHIYU",
]
VoiceMessageBodyTextTypeType = Literal["SSML", "TEXT"]
PinpointSMSVoiceV2ServiceName = Literal["pinpoint-sms-voice-v2"]
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
    "describe_account_attributes",
    "describe_account_limits",
    "describe_configuration_sets",
    "describe_keywords",
    "describe_opt_out_lists",
    "describe_opted_out_numbers",
    "describe_phone_numbers",
    "describe_pools",
    "describe_protect_configurations",
    "describe_registration_attachments",
    "describe_registration_field_definitions",
    "describe_registration_field_values",
    "describe_registration_section_definitions",
    "describe_registration_type_definitions",
    "describe_registration_versions",
    "describe_registrations",
    "describe_sender_ids",
    "describe_spend_limits",
    "describe_verified_destination_numbers",
    "list_pool_origination_identities",
    "list_protect_configuration_rule_set_number_overrides",
    "list_registration_associations",
]
RegionName = Literal[
    "af-south-1",
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
