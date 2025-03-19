"""
Type annotations for logs service literal definitions.

[Documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from mypy_boto3_logs.literals import AnomalyDetectorStatusType

    data: AnomalyDetectorStatusType = "ANALYZING"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "AnomalyDetectorStatusType",
    "CloudWatchLogsServiceName",
    "DataProtectionStatusType",
    "DeliveryDestinationTypeType",
    "DescribeConfigurationTemplatesPaginatorName",
    "DescribeDeliveriesPaginatorName",
    "DescribeDeliveryDestinationsPaginatorName",
    "DescribeDeliverySourcesPaginatorName",
    "DescribeDestinationsPaginatorName",
    "DescribeExportTasksPaginatorName",
    "DescribeLogGroupsPaginatorName",
    "DescribeLogStreamsPaginatorName",
    "DescribeMetricFiltersPaginatorName",
    "DescribeQueriesPaginatorName",
    "DescribeResourcePoliciesPaginatorName",
    "DescribeSubscriptionFiltersPaginatorName",
    "DistributionType",
    "EntityRejectionErrorTypeType",
    "EvaluationFrequencyType",
    "ExportTaskStatusCodeType",
    "FilterLogEventsPaginatorName",
    "FlattenedElementType",
    "IndexSourceType",
    "InheritedPropertyType",
    "IntegrationStatusType",
    "IntegrationTypeType",
    "ListAnomaliesPaginatorName",
    "ListLogAnomalyDetectorsPaginatorName",
    "ListLogGroupsForQueryPaginatorName",
    "LogGroupClassType",
    "OpenSearchResourceStatusTypeType",
    "OrderByType",
    "OutputFormatType",
    "PaginatorName",
    "PolicyTypeType",
    "QueryLanguageType",
    "QueryStatusType",
    "RegionName",
    "ResourceServiceName",
    "ScopeType",
    "ServiceName",
    "StandardUnitType",
    "StateType",
    "SuppressionStateType",
    "SuppressionTypeType",
    "SuppressionUnitType",
    "TypeType",
)


AnomalyDetectorStatusType = Literal[
    "ANALYZING", "DELETED", "FAILED", "INITIALIZING", "PAUSED", "TRAINING"
]
DataProtectionStatusType = Literal["ACTIVATED", "ARCHIVED", "DELETED", "DISABLED"]
DeliveryDestinationTypeType = Literal["CWL", "FH", "S3"]
DescribeConfigurationTemplatesPaginatorName = Literal["describe_configuration_templates"]
DescribeDeliveriesPaginatorName = Literal["describe_deliveries"]
DescribeDeliveryDestinationsPaginatorName = Literal["describe_delivery_destinations"]
DescribeDeliverySourcesPaginatorName = Literal["describe_delivery_sources"]
DescribeDestinationsPaginatorName = Literal["describe_destinations"]
DescribeExportTasksPaginatorName = Literal["describe_export_tasks"]
DescribeLogGroupsPaginatorName = Literal["describe_log_groups"]
DescribeLogStreamsPaginatorName = Literal["describe_log_streams"]
DescribeMetricFiltersPaginatorName = Literal["describe_metric_filters"]
DescribeQueriesPaginatorName = Literal["describe_queries"]
DescribeResourcePoliciesPaginatorName = Literal["describe_resource_policies"]
DescribeSubscriptionFiltersPaginatorName = Literal["describe_subscription_filters"]
DistributionType = Literal["ByLogStream", "Random"]
EntityRejectionErrorTypeType = Literal[
    "EntitySizeTooLarge",
    "InvalidAttributes",
    "InvalidEntity",
    "InvalidKeyAttributes",
    "InvalidTypeValue",
    "MissingRequiredFields",
    "UnsupportedLogGroupType",
]
EvaluationFrequencyType = Literal[
    "FIFTEEN_MIN", "FIVE_MIN", "ONE_HOUR", "ONE_MIN", "TEN_MIN", "THIRTY_MIN"
]
ExportTaskStatusCodeType = Literal[
    "CANCELLED", "COMPLETED", "FAILED", "PENDING", "PENDING_CANCEL", "RUNNING"
]
FilterLogEventsPaginatorName = Literal["filter_log_events"]
FlattenedElementType = Literal["first", "last"]
IndexSourceType = Literal["ACCOUNT", "LOG_GROUP"]
InheritedPropertyType = Literal["ACCOUNT_DATA_PROTECTION"]
IntegrationStatusType = Literal["ACTIVE", "FAILED", "PROVISIONING"]
IntegrationTypeType = Literal["OPENSEARCH"]
ListAnomaliesPaginatorName = Literal["list_anomalies"]
ListLogAnomalyDetectorsPaginatorName = Literal["list_log_anomaly_detectors"]
ListLogGroupsForQueryPaginatorName = Literal["list_log_groups_for_query"]
LogGroupClassType = Literal["INFREQUENT_ACCESS", "STANDARD"]
OpenSearchResourceStatusTypeType = Literal["ACTIVE", "ERROR", "NOT_FOUND"]
OrderByType = Literal["LastEventTime", "LogStreamName"]
OutputFormatType = Literal["json", "parquet", "plain", "raw", "w3c"]
PolicyTypeType = Literal[
    "DATA_PROTECTION_POLICY",
    "FIELD_INDEX_POLICY",
    "SUBSCRIPTION_FILTER_POLICY",
    "TRANSFORMER_POLICY",
]
QueryLanguageType = Literal["CWLI", "PPL", "SQL"]
QueryStatusType = Literal[
    "Cancelled", "Complete", "Failed", "Running", "Scheduled", "Timeout", "Unknown"
]
ScopeType = Literal["ALL"]
StandardUnitType = Literal[
    "Bits",
    "Bits/Second",
    "Bytes",
    "Bytes/Second",
    "Count",
    "Count/Second",
    "Gigabits",
    "Gigabits/Second",
    "Gigabytes",
    "Gigabytes/Second",
    "Kilobits",
    "Kilobits/Second",
    "Kilobytes",
    "Kilobytes/Second",
    "Megabits",
    "Megabits/Second",
    "Megabytes",
    "Megabytes/Second",
    "Microseconds",
    "Milliseconds",
    "None",
    "Percent",
    "Seconds",
    "Terabits",
    "Terabits/Second",
    "Terabytes",
    "Terabytes/Second",
]
StateType = Literal["Active", "Baseline", "Suppressed"]
SuppressionStateType = Literal["SUPPRESSED", "UNSUPPRESSED"]
SuppressionTypeType = Literal["INFINITE", "LIMITED"]
SuppressionUnitType = Literal["HOURS", "MINUTES", "SECONDS"]
TypeType = Literal["boolean", "double", "integer", "string"]
CloudWatchLogsServiceName = Literal["logs"]
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
    "describe_configuration_templates",
    "describe_deliveries",
    "describe_delivery_destinations",
    "describe_delivery_sources",
    "describe_destinations",
    "describe_export_tasks",
    "describe_log_groups",
    "describe_log_streams",
    "describe_metric_filters",
    "describe_queries",
    "describe_resource_policies",
    "describe_subscription_filters",
    "filter_log_events",
    "list_anomalies",
    "list_log_anomaly_detectors",
    "list_log_groups_for_query",
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
