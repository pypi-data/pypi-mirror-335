"""
Type annotations for transcribe service literal definitions.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_transcribe/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from types_boto3_transcribe.literals import BaseModelNameType

    data: BaseModelNameType = "NarrowBand"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "BaseModelNameType",
    "CLMLanguageCodeType",
    "CallAnalyticsFeatureType",
    "CallAnalyticsJobStatusType",
    "CallAnalyticsSkippedReasonCodeType",
    "InputTypeType",
    "LanguageCodeType",
    "MediaFormatType",
    "MedicalContentIdentificationTypeType",
    "MedicalScribeJobStatusType",
    "MedicalScribeLanguageCodeType",
    "MedicalScribeNoteTemplateType",
    "MedicalScribeParticipantRoleType",
    "ModelStatusType",
    "OutputLocationTypeType",
    "ParticipantRoleType",
    "PiiEntityTypeType",
    "RedactionOutputType",
    "RedactionTypeType",
    "RegionName",
    "ResourceServiceName",
    "SentimentValueType",
    "ServiceName",
    "SpecialtyType",
    "SubtitleFormatType",
    "ToxicityCategoryType",
    "TranscribeServiceServiceName",
    "TranscriptFilterTypeType",
    "TranscriptionJobStatusType",
    "TypeType",
    "VocabularyFilterMethodType",
    "VocabularyStateType",
)


BaseModelNameType = Literal["NarrowBand", "WideBand"]
CLMLanguageCodeType = Literal["de-DE", "en-AU", "en-GB", "en-US", "es-US", "hi-IN", "ja-JP"]
CallAnalyticsFeatureType = Literal["GENERATIVE_SUMMARIZATION"]
CallAnalyticsJobStatusType = Literal["COMPLETED", "FAILED", "IN_PROGRESS", "QUEUED"]
CallAnalyticsSkippedReasonCodeType = Literal[
    "FAILED_SAFETY_GUIDELINES", "INSUFFICIENT_CONVERSATION_CONTENT"
]
InputTypeType = Literal["POST_CALL", "REAL_TIME"]
LanguageCodeType = Literal[
    "ab-GE",
    "af-ZA",
    "ar-AE",
    "ar-SA",
    "ast-ES",
    "az-AZ",
    "ba-RU",
    "be-BY",
    "bg-BG",
    "bn-IN",
    "bs-BA",
    "ca-ES",
    "ckb-IQ",
    "ckb-IR",
    "cs-CZ",
    "cy-WL",
    "da-DK",
    "de-CH",
    "de-DE",
    "el-GR",
    "en-AB",
    "en-AU",
    "en-GB",
    "en-IE",
    "en-IN",
    "en-NZ",
    "en-US",
    "en-WL",
    "en-ZA",
    "es-ES",
    "es-US",
    "et-ET",
    "eu-ES",
    "fa-IR",
    "fi-FI",
    "fr-CA",
    "fr-FR",
    "gl-ES",
    "gu-IN",
    "ha-NG",
    "he-IL",
    "hi-IN",
    "hr-HR",
    "hu-HU",
    "hy-AM",
    "id-ID",
    "is-IS",
    "it-IT",
    "ja-JP",
    "ka-GE",
    "kab-DZ",
    "kk-KZ",
    "kn-IN",
    "ko-KR",
    "ky-KG",
    "lg-IN",
    "lt-LT",
    "lv-LV",
    "mhr-RU",
    "mi-NZ",
    "mk-MK",
    "ml-IN",
    "mn-MN",
    "mr-IN",
    "ms-MY",
    "mt-MT",
    "nl-NL",
    "no-NO",
    "or-IN",
    "pa-IN",
    "pl-PL",
    "ps-AF",
    "pt-BR",
    "pt-PT",
    "ro-RO",
    "ru-RU",
    "rw-RW",
    "si-LK",
    "sk-SK",
    "sl-SI",
    "so-SO",
    "sr-RS",
    "su-ID",
    "sv-SE",
    "sw-BI",
    "sw-KE",
    "sw-RW",
    "sw-TZ",
    "sw-UG",
    "ta-IN",
    "te-IN",
    "th-TH",
    "tl-PH",
    "tr-TR",
    "tt-RU",
    "ug-CN",
    "uk-UA",
    "uz-UZ",
    "vi-VN",
    "wo-SN",
    "zh-CN",
    "zh-TW",
    "zu-ZA",
]
MediaFormatType = Literal["amr", "flac", "m4a", "mp3", "mp4", "ogg", "wav", "webm"]
MedicalContentIdentificationTypeType = Literal["PHI"]
MedicalScribeJobStatusType = Literal["COMPLETED", "FAILED", "IN_PROGRESS", "QUEUED"]
MedicalScribeLanguageCodeType = Literal["en-US"]
MedicalScribeNoteTemplateType = Literal["GIRPP", "HISTORY_AND_PHYSICAL"]
MedicalScribeParticipantRoleType = Literal["CLINICIAN", "PATIENT"]
ModelStatusType = Literal["COMPLETED", "FAILED", "IN_PROGRESS"]
OutputLocationTypeType = Literal["CUSTOMER_BUCKET", "SERVICE_BUCKET"]
ParticipantRoleType = Literal["AGENT", "CUSTOMER"]
PiiEntityTypeType = Literal[
    "ADDRESS",
    "ALL",
    "BANK_ACCOUNT_NUMBER",
    "BANK_ROUTING",
    "CREDIT_DEBIT_CVV",
    "CREDIT_DEBIT_EXPIRY",
    "CREDIT_DEBIT_NUMBER",
    "EMAIL",
    "NAME",
    "PHONE",
    "PIN",
    "SSN",
]
RedactionOutputType = Literal["redacted", "redacted_and_unredacted"]
RedactionTypeType = Literal["PII"]
SentimentValueType = Literal["MIXED", "NEGATIVE", "NEUTRAL", "POSITIVE"]
SpecialtyType = Literal["PRIMARYCARE"]
SubtitleFormatType = Literal["srt", "vtt"]
ToxicityCategoryType = Literal["ALL"]
TranscriptFilterTypeType = Literal["EXACT"]
TranscriptionJobStatusType = Literal["COMPLETED", "FAILED", "IN_PROGRESS", "QUEUED"]
TypeType = Literal["CONVERSATION", "DICTATION"]
VocabularyFilterMethodType = Literal["mask", "remove", "tag"]
VocabularyStateType = Literal["FAILED", "PENDING", "READY"]
TranscribeServiceServiceName = Literal["transcribe"]
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
RegionName = Literal[
    "af-south-1",
    "ap-east-1",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "ca-central-1",
    "eu-central-1",
    "eu-north-1",
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
