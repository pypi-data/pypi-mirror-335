"""
Type annotations for iotwireless service literal definitions.

[Documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_iotwireless/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from mypy_boto3_iotwireless.literals import AggregationPeriodType

    data: AggregationPeriodType = "OneDay"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "AggregationPeriodType",
    "ApplicationConfigTypeType",
    "BatteryLevelType",
    "ConnectionStatusType",
    "DeviceProfileTypeType",
    "DeviceStateType",
    "DimensionNameType",
    "DlClassType",
    "DownlinkModeType",
    "EventNotificationPartnerTypeType",
    "EventNotificationResourceTypeType",
    "EventNotificationTopicStatusType",
    "EventType",
    "ExpressionTypeType",
    "FuotaDeviceStatusType",
    "FuotaTaskEventType",
    "FuotaTaskStatusType",
    "FuotaTaskTypeType",
    "IdentifierTypeType",
    "ImportTaskStatusType",
    "IoTWirelessServiceName",
    "LogLevelType",
    "MessageTypeType",
    "MetricNameType",
    "MetricQueryStatusType",
    "MulticastFrameInfoType",
    "OnboardStatusType",
    "PartnerTypeType",
    "PositionConfigurationFecType",
    "PositionConfigurationStatusType",
    "PositionResourceTypeType",
    "PositionSolverProviderType",
    "PositionSolverTypeType",
    "PositioningConfigStatusType",
    "RegionName",
    "ResourceServiceName",
    "ServiceName",
    "SigningAlgType",
    "SummaryMetricConfigurationStatusType",
    "SupportedRfRegionType",
    "WirelessDeviceEventType",
    "WirelessDeviceFrameInfoType",
    "WirelessDeviceIdTypeType",
    "WirelessDeviceSidewalkStatusType",
    "WirelessDeviceTypeType",
    "WirelessGatewayEventType",
    "WirelessGatewayIdTypeType",
    "WirelessGatewayServiceTypeType",
    "WirelessGatewayTaskDefinitionTypeType",
    "WirelessGatewayTaskStatusType",
    "WirelessGatewayTypeType",
)


AggregationPeriodType = Literal["OneDay", "OneHour", "OneWeek"]
ApplicationConfigTypeType = Literal["SemtechGeolocation"]
BatteryLevelType = Literal["critical", "low", "normal"]
ConnectionStatusType = Literal["Connected", "Disconnected"]
DeviceProfileTypeType = Literal["LoRaWAN", "Sidewalk"]
DeviceStateType = Literal[
    "Provisioned", "RegisteredNotSeen", "RegisteredReachable", "RegisteredUnreachable"
]
DimensionNameType = Literal["DeviceId", "GatewayId"]
DlClassType = Literal["ClassB", "ClassC"]
DownlinkModeType = Literal["CONCURRENT", "SEQUENTIAL", "USING_UPLINK_GATEWAY"]
EventNotificationPartnerTypeType = Literal["Sidewalk"]
EventNotificationResourceTypeType = Literal[
    "FuotaTask", "SidewalkAccount", "WirelessDevice", "WirelessGateway"
]
EventNotificationTopicStatusType = Literal["Disabled", "Enabled"]
EventType = Literal["ack", "discovered", "lost", "nack", "passthrough"]
ExpressionTypeType = Literal["MqttTopic", "RuleName"]
FuotaDeviceStatusType = Literal[
    "Device_exist_in_conflict_fuota_task",
    "FragAlgo_unsupported",
    "FragIndex_unsupported",
    "Initial",
    "MICError",
    "MemoryError",
    "MissingFrag",
    "Not_enough_memory",
    "Package_Not_Supported",
    "SessionCnt_replay",
    "Successful",
    "Wrong_descriptor",
]
FuotaTaskEventType = Literal["Fuota"]
FuotaTaskStatusType = Literal[
    "Delete_Waiting", "FuotaDone", "FuotaSession_Waiting", "In_FuotaSession", "Pending"
]
FuotaTaskTypeType = Literal["LoRaWAN"]
IdentifierTypeType = Literal[
    "DevEui",
    "FuotaTaskId",
    "GatewayEui",
    "PartnerAccountId",
    "WirelessDeviceId",
    "WirelessGatewayId",
]
ImportTaskStatusType = Literal[
    "COMPLETE", "DELETING", "FAILED", "INITIALIZED", "INITIALIZING", "PENDING"
]
LogLevelType = Literal["DISABLED", "ERROR", "INFO"]
MessageTypeType = Literal[
    "CUSTOM_COMMAND_ID_GET",
    "CUSTOM_COMMAND_ID_NOTIFY",
    "CUSTOM_COMMAND_ID_RESP",
    "CUSTOM_COMMAND_ID_SET",
]
MetricNameType = Literal[
    "AwsAccountActiveDeviceCount",
    "AwsAccountActiveGatewayCount",
    "AwsAccountDeviceCount",
    "AwsAccountDownlinkCount",
    "AwsAccountGatewayCount",
    "AwsAccountJoinAcceptCount",
    "AwsAccountJoinRequestCount",
    "AwsAccountRoamingDownlinkCount",
    "AwsAccountRoamingUplinkCount",
    "AwsAccountUplinkCount",
    "AwsAccountUplinkLostCount",
    "AwsAccountUplinkLostRate",
    "DeviceDownlinkCount",
    "DeviceJoinAcceptCount",
    "DeviceJoinRequestCount",
    "DeviceRSSI",
    "DeviceRoamingDownlinkCount",
    "DeviceRoamingRSSI",
    "DeviceRoamingSNR",
    "DeviceRoamingUplinkCount",
    "DeviceSNR",
    "DeviceUplinkCount",
    "DeviceUplinkLostCount",
    "DeviceUplinkLostRate",
    "GatewayDownTime",
    "GatewayDownlinkCount",
    "GatewayJoinAcceptCount",
    "GatewayJoinRequestCount",
    "GatewayRSSI",
    "GatewaySNR",
    "GatewayUpTime",
    "GatewayUplinkCount",
]
MetricQueryStatusType = Literal["Failed", "Succeeded"]
MulticastFrameInfoType = Literal["DISABLED", "ENABLED"]
OnboardStatusType = Literal["FAILED", "INITIALIZED", "ONBOARDED", "PENDING"]
PartnerTypeType = Literal["Sidewalk"]
PositionConfigurationFecType = Literal["NONE", "ROSE"]
PositionConfigurationStatusType = Literal["Disabled", "Enabled"]
PositionResourceTypeType = Literal["WirelessDevice", "WirelessGateway"]
PositionSolverProviderType = Literal["Semtech"]
PositionSolverTypeType = Literal["GNSS"]
PositioningConfigStatusType = Literal["Disabled", "Enabled"]
SigningAlgType = Literal["Ed25519", "P256r1"]
SummaryMetricConfigurationStatusType = Literal["Disabled", "Enabled"]
SupportedRfRegionType = Literal[
    "AS923-1",
    "AS923-2",
    "AS923-3",
    "AS923-4",
    "AU915",
    "CN470",
    "CN779",
    "EU433",
    "EU868",
    "IN865",
    "KR920",
    "RU864",
    "US915",
]
WirelessDeviceEventType = Literal["Downlink_Data", "Join", "Registration", "Rejoin", "Uplink_Data"]
WirelessDeviceFrameInfoType = Literal["DISABLED", "ENABLED"]
WirelessDeviceIdTypeType = Literal[
    "DevEui", "SidewalkManufacturingSn", "ThingName", "WirelessDeviceId"
]
WirelessDeviceSidewalkStatusType = Literal["ACTIVATED", "PROVISIONED", "REGISTERED", "UNKNOWN"]
WirelessDeviceTypeType = Literal["LoRaWAN", "Sidewalk"]
WirelessGatewayEventType = Literal["CUPS_Request", "Certificate"]
WirelessGatewayIdTypeType = Literal["GatewayEui", "ThingName", "WirelessGatewayId"]
WirelessGatewayServiceTypeType = Literal["CUPS", "LNS"]
WirelessGatewayTaskDefinitionTypeType = Literal["UPDATE"]
WirelessGatewayTaskStatusType = Literal[
    "COMPLETED", "FAILED", "FIRST_RETRY", "IN_PROGRESS", "PENDING", "SECOND_RETRY"
]
WirelessGatewayTypeType = Literal["LoRaWAN"]
IoTWirelessServiceName = Literal["iotwireless"]
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
    "ap-northeast-1",
    "ap-southeast-2",
    "eu-central-1",
    "eu-west-1",
    "sa-east-1",
    "us-east-1",
    "us-west-2",
]
