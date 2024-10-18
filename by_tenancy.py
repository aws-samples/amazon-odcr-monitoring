import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import EndpointConnectionError
import argparse
import logging
import sys
import re

### creating a log file for the code 
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')

file_handler = logging.FileHandler('by_tenancy.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Initialize boto3 clients
cloudwatch_client = boto3.client('cloudwatch')

def sns_topic_exists(topic_name,RegionName):
    """
    Check if an SNS topic with the specified name exists.

    :param topic_name: The name of the SNS topic.
    :return: The ARN of the topic if it exists, None otherwise.
    """
    sns_client = boto3.client('sns',region_name=RegionName)

    # List all SNS topics
    try:
        paginator = sns_client.get_paginator('list_topics')
        for page in paginator.paginate():
            for topic in page['Topics']:
                arn = topic['TopicArn']
                # Check if the topic name matches the desired topic
                if arn.split(':')[-1] == topic_name:
                    return arn
        return None
    except ClientError as e:
        logger.error(f"An error occurred: {e}.")
        return None

#create SNS Alarm for ODCR
def createODCRAlarmTopic(topic_name,RegionName):
    sns = boto3.client('sns', region_name=RegionName)
    try:
        response = sns.create_topic(
        Name=topic_name,
        Attributes={
            'DisplayName': 'ODCRAlarm'
        },
        )
        return response['TopicArn']
    except ClientError as e:
        logger.error(f"Failed to create the SNS topic: {e}.")
        return None


#Subscribe to an SNS Topic

def subscribe_to_sns(topic_arn,protocol, endpoint,RegionName):
    """
    Subscribe to an SNS topic.

    :param topic_arn: The ARN of the SNS topic.
    :param protocol: The protocol for the endpoint ('email', 'sms', 'http', 'https', 'application', or 'lambda').
    :param endpoint: The endpoint that receives notifications (email address, phone number, URL, etc.).
    :return: Subscription ARN if successful.
    """
    # Create an SNS client
    sns_client = boto3.client('sns',region_name=RegionName)

    try:
        # Subscribe to the SNS topic
        response = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol=protocol,
            Endpoint=endpoint
        )
        
        # Return the Subscription ARN from the response
        logger.info(f"Subscribed to the SNS topic: {response['SubscriptionArn']}.")
        return response['SubscriptionArn']
    except EndpointConnectionError as e:
        logger.error(f"Exiting.....Failed to connect to the endpoint: {e}.")
        # Here you could retry the connection, log the error, or handle it in another appropriate way.
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error subscribing to SNS topic: {e}.")
        return None

def is_valid_email(email):
    """
    Validate the email address using regular expression.
    
    :param email: The email address to validate.
    :return: True if the email address is valid, False otherwise.
    """
    # Define the regular expression pattern for a valid email address
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Match the email against the regex pattern
    if re.match(email_regex, email):
        return True
    else:
        return False

# creates an alarm for InstanceUtilization CW metric with by_tenancy dimension and if SNS topic not created in a region, it will create one.
def createCWAlarm(topic_name,Dimension,MetricName,RegionName,EmailAddress,Protocol,ComparisonOperator,Threshold,Tenancy):
    cw = boto3.client('cloudwatch', region_name=RegionName)

    # Check if the topic exists
    topic_arn = sns_topic_exists(topic_name,RegionName)

    if topic_arn:
        logger.info(f"The SNS topic '{topic_name}' already exists with ARN: {topic_arn}.") 
        logger.info(f"Please ensure you have subscribed to the SNS Topic {topic_arn}.")
    else:
        logger.info(f"The SNS topic '{topic_name}' does not exist. Creating it now...")
        topic_arn = createODCRAlarmTopic(topic_name,RegionName)
        subscribe_to_sns(topic_arn,Protocol, EmailAddress,RegionName)
        logger.info(f'Please ensure you have subscribed to the SNS Topic {topic_arn}.')
    response = cw.put_metric_alarm(
        AlarmName=f'ODCRAlarm-{MetricName}-{Dimension}-{Tenancy}',
        AlarmActions=[
        topic_arn,
        ],
        MetricName= MetricName,
        Dimensions=[
        {
            'Name': 'Tenancy',
            'Value': Tenancy
        },
    ],
        Namespace='AWS/EC2CapacityReservations',
        Statistic='Average',
        Period=300,
        EvaluationPeriods=1,
        DatapointsToAlarm=1,
        Threshold=Threshold,
        ComparisonOperator=ComparisonOperator,
    )


def main():
    #adding argparser
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Create a CloudWatch Alarm with specified parameters.")

    # Adding arguments
    parser.add_argument(
        '--RegionName', 
        type=str, 
        required=True,  # This makes the argument required
        help="The AWS region name where the CloudWatch alarm should be created. Example'us-east-1'."
    )

    parser.add_argument(
        '--Dimension', 
        type=str, 
        default='Tenancy', 
        help="The dimension for the CloudWatch alarm. Default is 'Tenancy'."
    )

    parser.add_argument(
        '--MetricName', 
        type=str, 
        default='InstanceUtilization', 
        help="The metric name for the CloudWatch alarm. Default is 'InstanceUtilization'."
    )

    parser.add_argument(
        '--EmailAddress', 
        type=str, 
        required=True,  # This makes the argument required
        help="The email address to receive notifications. Example: 'user@example.com'."
    )
    parser.add_argument(
        '--ComparisonOperator',
        type=str,
        default='LessThanOrEqualToThreshold',
        help="The comparison operator for the CloudWatch alarm. Default is 'LessThanOrEqualToThreshold'."
    )
    parser.add_argument(
        '--Threshold',
        type=float,
        default=75.0,
        help="The threshold value for the CloudWatch alarm. Default is 75.0."
    )
    parser.add_argument(
        '--Protocol',
        type=str,
        default='email',
        help="The protocol for the SNS subscription. Default is 'email'."
    )

    parser.add_argument(
        '--Tenancy',
        type=str,
        required=True,  # This makes the argument required
        help="The tenancy for the CloudWatch alarm. Example: 'default'. Supported Tenancy are 'default', 'dedicated' "
    )
    parser.add_argument(
        '--TopicName',
        type=str,
        default='ODCRAlarmTopic',
        help="The name of the SNS topic. Default is 'ODCRAlarmTopic'."
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    if not is_valid_email(args.EmailAddress):
        logger.error(f"Invalid email address provided {args.EmailAddress}")
        sys.exit(1)

    # Assigning the parsed arguments to variables
    topicName = args.TopicName
    regionName = args.RegionName
    dimension = args.Dimension
    metricName = args.MetricName
    emailAddress = args.EmailAddress
    protocol = args.Protocol
    comparisonOperator = args.ComparisonOperator
    threshold = args.Threshold
    Tenancy = args.Tenancy
    logger.info(f"Creating CloudWatch Alarm for the {metricName} with {dimension} dimension in the {regionName} region.")
    createCWAlarm(topicName, dimension, metricName, regionName, emailAddress, protocol, comparisonOperator, threshold, Tenancy)  
    logger.info(f"Successfully created CloudWatch Alarm for the {metricName} with {dimension} dimension in the {regionName} region.")

if __name__ == "__main__":
    main()
