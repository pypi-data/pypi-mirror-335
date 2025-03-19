"""
Type annotations for autoscaling service literal definitions.

[Documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_autoscaling/literals/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from mypy_boto3_autoscaling.literals import AcceleratorManufacturerType

    data: AcceleratorManufacturerType = "amazon-web-services"
    ```
"""

import sys

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "AcceleratorManufacturerType",
    "AcceleratorNameType",
    "AcceleratorTypeType",
    "AutoScalingServiceName",
    "BareMetalType",
    "BurstablePerformanceType",
    "CapacityDistributionStrategyType",
    "CapacityReservationPreferenceType",
    "CpuManufacturerType",
    "DescribeAutoScalingGroupsPaginatorName",
    "DescribeAutoScalingInstancesPaginatorName",
    "DescribeLaunchConfigurationsPaginatorName",
    "DescribeLoadBalancerTargetGroupsPaginatorName",
    "DescribeLoadBalancersPaginatorName",
    "DescribeNotificationConfigurationsPaginatorName",
    "DescribePoliciesPaginatorName",
    "DescribeScalingActivitiesPaginatorName",
    "DescribeScheduledActionsPaginatorName",
    "DescribeTagsPaginatorName",
    "DescribeWarmPoolPaginatorName",
    "ImpairedZoneHealthCheckBehaviorType",
    "InstanceGenerationType",
    "InstanceMetadataEndpointStateType",
    "InstanceMetadataHttpTokensStateType",
    "InstanceRefreshStatusType",
    "LifecycleStateType",
    "LocalStorageType",
    "LocalStorageTypeType",
    "MetricStatisticType",
    "MetricTypeType",
    "PaginatorName",
    "PredefinedLoadMetricTypeType",
    "PredefinedMetricPairTypeType",
    "PredefinedScalingMetricTypeType",
    "PredictiveScalingMaxCapacityBreachBehaviorType",
    "PredictiveScalingModeType",
    "RefreshStrategyType",
    "RegionName",
    "ResourceServiceName",
    "ScaleInProtectedInstancesType",
    "ScalingActivityStatusCodeType",
    "ServiceName",
    "StandbyInstancesType",
    "WarmPoolStateType",
    "WarmPoolStatusType",
)


AcceleratorManufacturerType = Literal["amazon-web-services", "amd", "nvidia", "xilinx"]
AcceleratorNameType = Literal["a100", "k80", "m60", "radeon-pro-v520", "t4", "v100", "vu9p"]
AcceleratorTypeType = Literal["fpga", "gpu", "inference"]
BareMetalType = Literal["excluded", "included", "required"]
BurstablePerformanceType = Literal["excluded", "included", "required"]
CapacityDistributionStrategyType = Literal["balanced-best-effort", "balanced-only"]
CapacityReservationPreferenceType = Literal[
    "capacity-reservations-first", "capacity-reservations-only", "default", "none"
]
CpuManufacturerType = Literal["amazon-web-services", "amd", "intel"]
DescribeAutoScalingGroupsPaginatorName = Literal["describe_auto_scaling_groups"]
DescribeAutoScalingInstancesPaginatorName = Literal["describe_auto_scaling_instances"]
DescribeLaunchConfigurationsPaginatorName = Literal["describe_launch_configurations"]
DescribeLoadBalancerTargetGroupsPaginatorName = Literal["describe_load_balancer_target_groups"]
DescribeLoadBalancersPaginatorName = Literal["describe_load_balancers"]
DescribeNotificationConfigurationsPaginatorName = Literal["describe_notification_configurations"]
DescribePoliciesPaginatorName = Literal["describe_policies"]
DescribeScalingActivitiesPaginatorName = Literal["describe_scaling_activities"]
DescribeScheduledActionsPaginatorName = Literal["describe_scheduled_actions"]
DescribeTagsPaginatorName = Literal["describe_tags"]
DescribeWarmPoolPaginatorName = Literal["describe_warm_pool"]
ImpairedZoneHealthCheckBehaviorType = Literal["IgnoreUnhealthy", "ReplaceUnhealthy"]
InstanceGenerationType = Literal["current", "previous"]
InstanceMetadataEndpointStateType = Literal["disabled", "enabled"]
InstanceMetadataHttpTokensStateType = Literal["optional", "required"]
InstanceRefreshStatusType = Literal[
    "Baking",
    "Cancelled",
    "Cancelling",
    "Failed",
    "InProgress",
    "Pending",
    "RollbackFailed",
    "RollbackInProgress",
    "RollbackSuccessful",
    "Successful",
]
LifecycleStateType = Literal[
    "Detached",
    "Detaching",
    "EnteringStandby",
    "InService",
    "Pending",
    "Pending:Proceed",
    "Pending:Wait",
    "Quarantined",
    "Standby",
    "Terminated",
    "Terminating",
    "Terminating:Proceed",
    "Terminating:Wait",
    "Warmed:Hibernated",
    "Warmed:Pending",
    "Warmed:Pending:Proceed",
    "Warmed:Pending:Wait",
    "Warmed:Running",
    "Warmed:Stopped",
    "Warmed:Terminated",
    "Warmed:Terminating",
    "Warmed:Terminating:Proceed",
    "Warmed:Terminating:Wait",
]
LocalStorageType = Literal["excluded", "included", "required"]
LocalStorageTypeType = Literal["hdd", "ssd"]
MetricStatisticType = Literal["Average", "Maximum", "Minimum", "SampleCount", "Sum"]
MetricTypeType = Literal[
    "ALBRequestCountPerTarget",
    "ASGAverageCPUUtilization",
    "ASGAverageNetworkIn",
    "ASGAverageNetworkOut",
]
PredefinedLoadMetricTypeType = Literal[
    "ALBTargetGroupRequestCount",
    "ASGTotalCPUUtilization",
    "ASGTotalNetworkIn",
    "ASGTotalNetworkOut",
]
PredefinedMetricPairTypeType = Literal[
    "ALBRequestCount", "ASGCPUUtilization", "ASGNetworkIn", "ASGNetworkOut"
]
PredefinedScalingMetricTypeType = Literal[
    "ALBRequestCountPerTarget",
    "ASGAverageCPUUtilization",
    "ASGAverageNetworkIn",
    "ASGAverageNetworkOut",
]
PredictiveScalingMaxCapacityBreachBehaviorType = Literal["HonorMaxCapacity", "IncreaseMaxCapacity"]
PredictiveScalingModeType = Literal["ForecastAndScale", "ForecastOnly"]
RefreshStrategyType = Literal["Rolling"]
ScaleInProtectedInstancesType = Literal["Ignore", "Refresh", "Wait"]
ScalingActivityStatusCodeType = Literal[
    "Cancelled",
    "Failed",
    "InProgress",
    "MidLifecycleAction",
    "PendingSpotBidPlacement",
    "PreInService",
    "Successful",
    "WaitingForConnectionDraining",
    "WaitingForELBConnectionDraining",
    "WaitingForInstanceId",
    "WaitingForInstanceWarmup",
    "WaitingForSpotInstanceId",
    "WaitingForSpotInstanceRequestId",
]
StandbyInstancesType = Literal["Ignore", "Terminate", "Wait"]
WarmPoolStateType = Literal["Hibernated", "Running", "Stopped"]
WarmPoolStatusType = Literal["PendingDelete"]
AutoScalingServiceName = Literal["autoscaling"]
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
    "describe_auto_scaling_groups",
    "describe_auto_scaling_instances",
    "describe_launch_configurations",
    "describe_load_balancer_target_groups",
    "describe_load_balancers",
    "describe_notification_configurations",
    "describe_policies",
    "describe_scaling_activities",
    "describe_scheduled_actions",
    "describe_tags",
    "describe_warm_pool",
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
