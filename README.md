# <ins>**amazon-odcr-monitoring**</ins>


In my previous [blog](https://aws.amazon.com/blogs/compute/automate-the-creation-of-on-demand-capacity-reservations-for-running-ec2-instances/), I discussed a solution for automating creation and operations of ODCR for existing EC2 instances. The blog included:
- Creating Capacity Reservations.
- Modifying Capacity Reservations.
- Canceling Capacity Reservation operations

that inherit your existing EC2 instances for attribute details.

We also discussed monitoring aspects of ODCR metrics using [CloudWatch](https://aws.amazon.com/cloudwatch/). CloudWatch metrics let you monitor the unused capacity in your Capacity Reservations to optimize the ODCR cost. In the blog, we focused on using one of the Capacity Reservation usage metrics' InstanceUtilization metric, which shows the percentage of reserved capacity instances currently in use. This metric is helpful for monitoring and optimizing ODCR consumption.
 
On August 1, 2024, the AWS EC2 team introduced [new Amazon CloudWatch dimensions for Amazon EC2 On-Demand Capacity Reservations](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/capacity-reservation-cw-metrics.html#capacity-reservation-dimensions). The existing CW metrics for On-Demand Capacity Reservations can now be grouped using the following new dimensions: **Availability Zone, Instance Match Criteria, Instance Type, InstancePlatform, Tenancy, or across all Capacity Reservations**. You can group the metrics by any of these dimensions within a selected region.

You can now efficiently monitor your On-Demand Capacity Reservations and identify unused capacity by setting CloudWatch alarms on CloudWatch metrics on any of these six new dimensions and the existing Capacity Reservation ID dimension. In this post, we will focus on using Capacity Reservation usage metrics' InstanceUtilization metric for On-Demand Capacity Reservations and grouped using the following new dimensions: **Availability Zone, Instance Match Criteria, Instance Type, InstancePlatform, Tenancy, or across all Capacity Reservations**.
 
 
<ins>**Across all Capacity Reservations** dimension</ins>:

Let's assume you have multiple Capacity Reservations in a region in an AWS account. You can use Capacity Reservation usage metrics' **InstanceUtilization** metric for On-Demand Capacity Reservations and grouped it with **AllCapacityReservations** dimension. You can run **by_all_capacity_reservations.py** script from here to set a CloudWatch alarm to notify you whenever the total capacity utilization across all Capacity Reservations drops to less than or equal to 75%. **Note**: You can set a threshold based on your company's usage optimization goal. Once you have a reservation you pay for it being used or unused (which are both priced the same). Customers are fine with paying this cost since it comes with guaranteed capacity. However, they seek improved reservation usage utilization to ensure their ordered capacity is actually being used.
 
#**usage with required parameters**:

#python3 by_all_capacity_reservations.py --RegionName "<AWS Region>" --EmailAdress "<Valid user email address>"
 
#**usage with required and optional parameters**:

#python3 by_all_capacity_reservations.py --RegionName "<AWS Region>" --EmailAdress "<Valid user email address>" [--Dimension "DIMENSION". Default is 'AllCapacityReservations'] [--MetricName "METRICNAME". Default is 'InstanceUtilization'] [--ComparisonOperator "COMPARISONOPERATOR". Default is 'LessThanOrEqualToThreshold'] [--Threshold "THRESHOLD". Default is 75.0] [--Protocol "PROTOCOL". Default is 'email'] [--TopicName "TOPICNAME". Default is 'ODCRAlarmTopic']
 
<ins>**Instance Type** dimension</ins>:

Once you understand the total capacity utilization from the previous alarms, if you want to monitor some large instance types usage like r7g.24xlarge, p3.16xlarge or GPU instances, you can set a CloudWatch alarm with Capacity Reservation usage metrics' **InstanceUtilization** metric for On-Demand Capacity Reservations and grouped it with **Instance Type** dimension. You can run the **by_instanceType.py** script from here to set a CloudWatch alarm to notify you whenever utilization of a specific instance type across all Capacity Reservations drops to less than or equal to 75%. **Note**: You can set a threshold per your company's usage optimization goal. Once you have a reservation you pay for it being used or unused (which are both priced the same). Customers are fine with paying this cost since it comes with guaranteed capacity. However, they seek improved reservation usage utilization to ensure their ordered capacity is actually being used.
 
#**usage with required parameters**:
 
#**usage with required parameters**:

#python3 by_instanceType.py --RegionName "<AWS Region>" --EmailAdress "<Valid user email address>" --InstanceType " <InstanceType>"
 
#**usage with required and optional parameters**:

#python3 by_instanceType.py --RegionName "<AWS Region>" --EmailAdress "<Valid user email address>" --InstanceType " <InstanceType>" [--Dimension "DIMENSION". Default is 'InstanceType'] [--MetricName "METRICNAME". Default is 'InstanceUtilization'] [--ComparisonOperator "COMPARISONOPERATOR". Default is 'LessThanOrEqualToThreshold'] [--Threshold "THRESHOLD". Default is 75.0] [--Protocol "PROTOCOL". Default is 'email'] [--TopicName "TOPICNAME". Default is 'ODCRAlarmTopic']
 
 
<ins>**Availability Zone** dimension</ins>:

Now that you have an in-depth understanding of which instance types are underutilized, if you want to narrow them down by availability zones, then you can use Capacity Reservation usage metrics' **InstanceUtilization** metric for On-Demand Capacity Reservations and grouped it with **Availability Zone** dimension. Let's assume you are running infrastructure in three availability zones; then, you can create three CloudWatch Alarms, one per AZ, by running the **by_availabiltyZone.py** script from here. This script will notify you whenever the total capacity utilization in an Availability Zone drops to less than or equal to 75%. **Note**: You can set a threshold per your company's usage optimization goal. Once you have a reservation you pay for it being used or unused (which are both priced the same). Customers are fine with paying this cost since it comes with guaranteed capacity. However, they seek improved reservation usage utilization to ensure their ordered capacity is actually being used.
 
#**usage with required parameters**:

#python3 by_availabilityZone.py --RegionName "<AWS Region>" --EmailAdress "<Valid user email address>" --AvailabilityZone " <AvailabilityZone>"
 
#**usage with required and optional parameters**:

#python3 by_availabilityZone.py --RegionName "<AWS Region>" --EmailAdress "<Valid user email address>" --AvailabilityZone " <AvailabilityZone>" [--Dimension "DIMENSION". Default is 'AvailabilityZone'] [--MetricName "METRICNAME". Default is 'InstanceUtilization'] [--ComparisonOperator "COMPARISONOPERATOR". Default is 'LessThanOrEqualToThreshold'] [--Threshold "THRESHOLD". Default is 75.0] [--Protocol "PROTOCOL". Default is 'email'] [--TopicName "TOPICNAME". Default is 'ODCRAlarmTopic']
 
<ins>**InstancePlatform** dimension</ins>:

Suppose you run instances with multiple platforms and want to be notified of instances with a specific underutilized platform. In that case, you can use Capacity Reservation usage metrics' **InstanceUtilization** metric for On-Demand Capacity Reservations and group it with the **InstancePlatform** dimension. Let's assume you have Capacity Reservations for instances with platforms such as **"Windows"** and **"Linux/UNIX"**, and you would like to be notified when Capacity Reservations with a platform of "Linux/UNIX" is underutilized. You can create a CloudWatch alarm by running the **by_platform.py** script from here. This script will notify you whenever the total Capacity Reservations for the Linux/UNIX platform instances drop to less than or equal to 75%. **Note**: You can set a threshold per your company's usage optimization goal. Once you have a reservation you pay for it being used or unused (which are both priced the same). Customers are fine with paying this cost since it comes with guaranteed capacity. However, they seek improved reservation usage utilization to ensure their ordered capacity is actually being used.
 
#**usage with required parameters**:

#python3 by_platform.py --RegionName "<AWS Region>" --EmailAdress "<Valid user email address>" --InstancePlatform "<InstancePlatform>"
 
#**usage with required and optional parameters**:

#python3 by_platform.py --RegionName "<AWS Region>" --EmailAdress "<Valid user email address>" --InstancePlatform "<InstancePlatform>" [--Dimension "DIMENSION". Default is 'Platform'] [--MetricName "METRICNAME". Default is 'InstanceUtilization'] [--ComparisonOperator "COMPARISONOPERATOR". Default is 'LessThanOrEqualToThreshold'] [--Threshold "THRESHOLD". Default is 75.0] [--Protocol "PROTOCOL". Default is 'email'] [--TopicName "TOPICNAME". Default is 'ODCRAlarmTopic']
 
#supported platforms are 'Linux/UNIX', 'Red Hat Enterprise Linux',' SUSE Linux', 'Windows', ' Windows with SQL Server Enterprise',' Windows with SQL Server Standard',' Windows with SQL Server Web',' Linux with SQL Server Standard',' Linux with SQL Server Web',' Linux with SQL Server Enterprise',' RHEL with SQL Server Standard',' RHEL with SQL Server Enterprise',' RHEL with SQL Server Web',' RHEL with HA',' RHEL with HA and SQL Server Standard',' RHEL with HA and SQL Server Enterprise',' Ubuntu Pro'
 
 
<ins>**Instance Match Criteria** dimension</ins>:

Let's assume you have multiple Capacity Reservations in a region in an AWS account with **"open"** and **"targeted"** **Instance Match Criteria** eligibility. If you want to be notified for Capacity Reservations when Instance Match Criteria with eligibility of **"open"** is underutilized, you can use Capacity Reservation usage metrics' **InstanceUtilization** metric for On-Demand Capacity Reservations and grouped it with **Instance Match Criteria** dimension by running **by_instanceMatchCriteria.py** from here. This script will notify you whenever the total capacity for the dimension of the Instance Match Criteria of "open"  drops to less than or equal to 75%. **Note**: You can set a threshold per your company's usage optimization goal. Once you have a reservation you pay for it being used or unused (which are both priced the same). Customers are fine with paying this cost since it comes with guaranteed capacity. However, they seek improved reservation usage utilization to ensure their ordered capacity is actually being used.
#**usage with required parameters**:

#python3 by_instanceMatchCriteria.py --RegionName "<AWS Region>" --EmailAdress "<Valid user email address>" --InstanceMatchCriteria "<InstanceMatchCriteria>"
 
#**usage with required and optional parameters**:

#python3 by_instanceMatchCriteria.py --RegionName "<AWS Region>" --EmailAdress "<Valid user email address>" –InstanceMatchCriteria "<InstanceMatchCriteria>" [--Dimension "DIMENSION". Default is 'InstanceMatchCriteria'] [--MetricName "METRICNAME". Default is 'InstanceUtilization'] [--ComparisonOperator "COMPARISONOPERATOR". Default is 'LessThanOrEqualToThreshold'] [--Threshold "THRESHOLD". Default is 75.0] [--Protocol "PROTOCOL". Default is 'email'] [--TopicName "TOPICNAME". Default is 'ODCRAlarmTopic']
 
#Supported Instance Match Criteria are "open" and "targeted".
 
<ins>**Tenancy** dimension</ins>:

Let's assume you have multiple Capacity Reservations in a region in an AWS account with **"default"** and **"dedicated"** Tenancy. You want to be notified when Capacity Reservations with Tenancy of **"default"** is underutilized. You can use Capacity Reservation usage metrics' ***InstanceUtilization** metric for On-Demand Capacity Reservations and group it with the **Tenancy** dimension by running **by_tenancy.py** from here. This script will notify you whenever the total capacity for the dimension of Tenancy of **"default"** drops to less than or equal to 75%. Note: You can set a threshold per your company's usage optimization goal. Once you have a reservation you pay for it being used or unused (which are both priced the same). Customers are fine with paying this cost since it comes with guaranteed capacity. However, they seek improved reservation usage utilization to ensure their ordered capacity is actually being used.
 
 
#**usage with required parameters**:

#python3 by_tenancy.py --RegionName "<AWS Region>" --EmailAdress "<Valid user email address>" --Tenancy "<Tenancy>"
 
#**usage with required and optional parameters**:

#python3 by_tenancy.py --RegionName "<AWS Region>" --EmailAdress "<Valid user email address>" --Tenancy "<Tenancy>" [--Dimension "DIMENSION". Default is 'Tenancy'] [--MetricName "METRICNAME". Default is 'InstanceUtilization'] [--ComparisonOperator "COMPARISONOPERATOR". Default is 'LessThanOrEqualToThreshold'] [--Threshold "THRESHOLD". Default is 75.0] [--Protocol "PROTOCOL". Default is 'email'] [--TopicName "TOPICNAME". Default is 'ODCRAlarmTopic']
 
#supported Tenancy are "default" and "dedicated".


