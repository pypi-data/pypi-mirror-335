"""
Type annotations for cognito-idp service literal definitions.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_cognito_idp/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from types_boto3_cognito_idp.literals import AccountTakeoverEventActionTypeType

    data: AccountTakeoverEventActionTypeType = "BLOCK"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = (
    "AccountTakeoverEventActionTypeType",
    "AdminListGroupsForUserPaginatorName",
    "AdminListUserAuthEventsPaginatorName",
    "AdvancedSecurityEnabledModeTypeType",
    "AdvancedSecurityModeTypeType",
    "AliasAttributeTypeType",
    "AssetCategoryTypeType",
    "AssetExtensionTypeType",
    "AttributeDataTypeType",
    "AuthFactorTypeType",
    "AuthFlowTypeType",
    "ChallengeNameType",
    "ChallengeNameTypeType",
    "ChallengeResponseType",
    "CognitoIdentityProviderServiceName",
    "ColorSchemeModeTypeType",
    "CompromisedCredentialsEventActionTypeType",
    "CustomEmailSenderLambdaVersionTypeType",
    "CustomSMSSenderLambdaVersionTypeType",
    "DefaultEmailOptionTypeType",
    "DeletionProtectionTypeType",
    "DeliveryMediumTypeType",
    "DeviceRememberedStatusTypeType",
    "DomainStatusTypeType",
    "EmailSendingAccountTypeType",
    "EventFilterTypeType",
    "EventResponseTypeType",
    "EventSourceNameType",
    "EventTypeType",
    "ExplicitAuthFlowsTypeType",
    "FeedbackValueTypeType",
    "IdentityProviderTypeTypeType",
    "ListGroupsPaginatorName",
    "ListIdentityProvidersPaginatorName",
    "ListResourceServersPaginatorName",
    "ListUserPoolClientsPaginatorName",
    "ListUserPoolsPaginatorName",
    "ListUsersInGroupPaginatorName",
    "ListUsersPaginatorName",
    "LogLevelType",
    "MessageActionTypeType",
    "OAuthFlowTypeType",
    "PaginatorName",
    "PreTokenGenerationLambdaVersionTypeType",
    "PreventUserExistenceErrorTypesType",
    "RecoveryOptionNameTypeType",
    "RegionName",
    "ResourceServiceName",
    "RiskDecisionTypeType",
    "RiskLevelTypeType",
    "ServiceName",
    "StatusTypeType",
    "TimeUnitsTypeType",
    "UserImportJobStatusTypeType",
    "UserPoolMfaTypeType",
    "UserPoolTierTypeType",
    "UserStatusTypeType",
    "UserVerificationTypeType",
    "UsernameAttributeTypeType",
    "VerifiedAttributeTypeType",
    "VerifySoftwareTokenResponseTypeType",
)

AccountTakeoverEventActionTypeType = Literal[
    "BLOCK", "MFA_IF_CONFIGURED", "MFA_REQUIRED", "NO_ACTION"
]
AdminListGroupsForUserPaginatorName = Literal["admin_list_groups_for_user"]
AdminListUserAuthEventsPaginatorName = Literal["admin_list_user_auth_events"]
AdvancedSecurityEnabledModeTypeType = Literal["AUDIT", "ENFORCED"]
AdvancedSecurityModeTypeType = Literal["AUDIT", "ENFORCED", "OFF"]
AliasAttributeTypeType = Literal["email", "phone_number", "preferred_username"]
AssetCategoryTypeType = Literal[
    "AUTH_APP_GRAPHIC",
    "EMAIL_GRAPHIC",
    "FAVICON_ICO",
    "FAVICON_SVG",
    "FORM_BACKGROUND",
    "FORM_LOGO",
    "IDP_BUTTON_ICON",
    "PAGE_BACKGROUND",
    "PAGE_FOOTER_BACKGROUND",
    "PAGE_FOOTER_LOGO",
    "PAGE_HEADER_BACKGROUND",
    "PAGE_HEADER_LOGO",
    "PASSKEY_GRAPHIC",
    "PASSWORD_GRAPHIC",
    "SMS_GRAPHIC",
]
AssetExtensionTypeType = Literal["ICO", "JPEG", "PNG", "SVG", "WEBP"]
AttributeDataTypeType = Literal["Boolean", "DateTime", "Number", "String"]
AuthFactorTypeType = Literal["EMAIL_OTP", "PASSWORD", "SMS_OTP", "WEB_AUTHN"]
AuthFlowTypeType = Literal[
    "ADMIN_NO_SRP_AUTH",
    "ADMIN_USER_PASSWORD_AUTH",
    "CUSTOM_AUTH",
    "REFRESH_TOKEN",
    "REFRESH_TOKEN_AUTH",
    "USER_AUTH",
    "USER_PASSWORD_AUTH",
    "USER_SRP_AUTH",
]
ChallengeNameType = Literal["Mfa", "Password"]
ChallengeNameTypeType = Literal[
    "ADMIN_NO_SRP_AUTH",
    "CUSTOM_CHALLENGE",
    "DEVICE_PASSWORD_VERIFIER",
    "DEVICE_SRP_AUTH",
    "EMAIL_OTP",
    "MFA_SETUP",
    "NEW_PASSWORD_REQUIRED",
    "PASSWORD",
    "PASSWORD_SRP",
    "PASSWORD_VERIFIER",
    "SELECT_CHALLENGE",
    "SELECT_MFA_TYPE",
    "SMS_MFA",
    "SMS_OTP",
    "SOFTWARE_TOKEN_MFA",
    "WEB_AUTHN",
]
ChallengeResponseType = Literal["Failure", "Success"]
ColorSchemeModeTypeType = Literal["DARK", "DYNAMIC", "LIGHT"]
CompromisedCredentialsEventActionTypeType = Literal["BLOCK", "NO_ACTION"]
CustomEmailSenderLambdaVersionTypeType = Literal["V1_0"]
CustomSMSSenderLambdaVersionTypeType = Literal["V1_0"]
DefaultEmailOptionTypeType = Literal["CONFIRM_WITH_CODE", "CONFIRM_WITH_LINK"]
DeletionProtectionTypeType = Literal["ACTIVE", "INACTIVE"]
DeliveryMediumTypeType = Literal["EMAIL", "SMS"]
DeviceRememberedStatusTypeType = Literal["not_remembered", "remembered"]
DomainStatusTypeType = Literal["ACTIVE", "CREATING", "DELETING", "FAILED", "UPDATING"]
EmailSendingAccountTypeType = Literal["COGNITO_DEFAULT", "DEVELOPER"]
EventFilterTypeType = Literal["PASSWORD_CHANGE", "SIGN_IN", "SIGN_UP"]
EventResponseTypeType = Literal["Fail", "InProgress", "Pass"]
EventSourceNameType = Literal["userAuthEvents", "userNotification"]
EventTypeType = Literal["ForgotPassword", "PasswordChange", "ResendCode", "SignIn", "SignUp"]
ExplicitAuthFlowsTypeType = Literal[
    "ADMIN_NO_SRP_AUTH",
    "ALLOW_ADMIN_USER_PASSWORD_AUTH",
    "ALLOW_CUSTOM_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_USER_SRP_AUTH",
    "CUSTOM_AUTH_FLOW_ONLY",
    "USER_PASSWORD_AUTH",
]
FeedbackValueTypeType = Literal["Invalid", "Valid"]
IdentityProviderTypeTypeType = Literal[
    "Facebook", "Google", "LoginWithAmazon", "OIDC", "SAML", "SignInWithApple"
]
ListGroupsPaginatorName = Literal["list_groups"]
ListIdentityProvidersPaginatorName = Literal["list_identity_providers"]
ListResourceServersPaginatorName = Literal["list_resource_servers"]
ListUserPoolClientsPaginatorName = Literal["list_user_pool_clients"]
ListUserPoolsPaginatorName = Literal["list_user_pools"]
ListUsersInGroupPaginatorName = Literal["list_users_in_group"]
ListUsersPaginatorName = Literal["list_users"]
LogLevelType = Literal["ERROR", "INFO"]
MessageActionTypeType = Literal["RESEND", "SUPPRESS"]
OAuthFlowTypeType = Literal["client_credentials", "code", "implicit"]
PreTokenGenerationLambdaVersionTypeType = Literal["V1_0", "V2_0", "V3_0"]
PreventUserExistenceErrorTypesType = Literal["ENABLED", "LEGACY"]
RecoveryOptionNameTypeType = Literal["admin_only", "verified_email", "verified_phone_number"]
RiskDecisionTypeType = Literal["AccountTakeover", "Block", "NoRisk"]
RiskLevelTypeType = Literal["High", "Low", "Medium"]
StatusTypeType = Literal["Disabled", "Enabled"]
TimeUnitsTypeType = Literal["days", "hours", "minutes", "seconds"]
UserImportJobStatusTypeType = Literal[
    "Created", "Expired", "Failed", "InProgress", "Pending", "Stopped", "Stopping", "Succeeded"
]
UserPoolMfaTypeType = Literal["OFF", "ON", "OPTIONAL"]
UserPoolTierTypeType = Literal["ESSENTIALS", "LITE", "PLUS"]
UserStatusTypeType = Literal[
    "ARCHIVED",
    "COMPROMISED",
    "CONFIRMED",
    "EXTERNAL_PROVIDER",
    "FORCE_CHANGE_PASSWORD",
    "RESET_REQUIRED",
    "UNCONFIRMED",
    "UNKNOWN",
]
UserVerificationTypeType = Literal["preferred", "required"]
UsernameAttributeTypeType = Literal["email", "phone_number"]
VerifiedAttributeTypeType = Literal["email", "phone_number"]
VerifySoftwareTokenResponseTypeType = Literal["ERROR", "SUCCESS"]
CognitoIdentityProviderServiceName = Literal["cognito-idp"]
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
    "admin_list_groups_for_user",
    "admin_list_user_auth_events",
    "list_groups",
    "list_identity_providers",
    "list_resource_servers",
    "list_user_pool_clients",
    "list_user_pools",
    "list_users",
    "list_users_in_group",
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
