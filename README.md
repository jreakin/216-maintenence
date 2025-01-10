# 216 App Draft

## Overview

The 216 App is a comprehensive software solution for 216 Maintenance, a company that handles maintenance work for Starbucks. The application includes features for user access, task management, inventory management, billing, admin/office staff dashboard, and scheduling. The software uses APIs built in Python and has front-end interfaces for MacOS, iOS, and VisionOS.

## User Access

The application supports four user roles with different access levels and permissions:

- **Super Admin**: Has the highest level of access and control over the application.
- **Office Admin**: Manages tasks, inventory, and billing.
- **Dispatcher**: Assigns tasks to employees and manages schedules.
- **Employee**: Accesses daily task sheets, notifications, and inventory checklists.

The application uses a role-based access control (RBAC) system to manage user roles and permissions. The RBAC system ensures that users can only access the features and data relevant to their roles. User roles and permissions are defined and managed in the backend API built in Python. The frontend interfaces for MacOS, iOS, and VisionOS enforce these roles and permissions to ensure a consistent user experience.

## Task Management

The task management system includes the following features:

- **Location Field**: Each task has a location field, which can standardize or verify the address to ensure it's correct. The application uses the Google Maps API and USPS Address Verification API for address verification.
- **Cost Fields**: Each task has an estimated cost field and a final cost field.
- **Status Levels**: The task management system supports multiple status levels to track the progress of each task.
- **Task Estimates**: Each task can produce its own estimate individually if necessary, or be added to a draft proposal or estimate if one is open.
- **Daily Task Sheets**: Each task can be added to an employee's daily task sheet, with push notifications on their devices. The task should pop up on their notification center upon arriving.
- **Drive Time Tracking**: The application uses the Google Maps API to track drive time to/from each location automatically.
- **Task Structure**: The task structure is Client > Locations > Tasks for Location > Types of tasks.
- **Machine Learning Integration**: The application uses machine learning models to analyze task descriptions and details, identify similar tasks, and predict the parts needed for a task. Employees have a checklist to confirm they have the necessary components before leaving a warehouse.
- **Task Prioritization and Deadlines**: Tasks can be assigned priority levels (e.g., high, medium, low) and include a deadline field to ensure timely completion. Notifications and reminders are implemented for approaching deadlines.
- **Task Dependencies and Subtasks**: Tasks can have dependencies, where certain tasks must be completed before others can begin. Tasks can also be broken down into smaller subtasks. A visual representation of task dependencies and subtasks is provided to help users understand the relationships between tasks.
- **Task Comments and Attachments**: Users can add comments to tasks for better communication and collaboration. Files, images, and documents can be attached to tasks, providing additional context and information. A version history for comments and attachments is implemented to track changes and updates over time.

## Inventory Management

The inventory management system includes the following features:

- **Inventory by Location/Warehouses**: The inventory is broken out by location/warehouses to manage stock levels at different sites.
- **Receipt and Purchase Order Scanning**: The application has a feature to scan receipts from stores or purchase orders and automatically ingest that information into the inventory system. The system uses the Google Cloud Vision API, Amazon Textract, and Microsoft Azure Cognitive Services - Computer Vision API for receipt scanning.
- **Task Allocation**: Inventory is allocated to each task based on the parts needed. This ensures that the necessary components are available for task completion.
- **Order List Generation**: If tasks require materials that are not available in the inventory, the system generates an order list from the required vendor.
- **Task Linkage**: Each item on the inventory list is linked to a task, allowing office staff to view the task and understand why the item is needed.
- **Inventory Forecasting and Alerts**: The system implements inventory forecasting to predict future inventory needs based on historical data and trends. Alerts for low stock levels notify office staff when inventory is running low.
- **Vendor Management**: The system integrates a vendor management system to keep track of suppliers and their contact information. Office staff can manage vendor relationships and view past orders and transactions. The system can automatically generate purchase orders and send them to vendors when inventory levels are low.
- **Inventory Audit and Reporting**: The system includes an inventory audit feature to regularly check and verify inventory levels. Detailed inventory reports, including stock levels, usage history, and discrepancies, are provided. Office staff can schedule and perform inventory audits and track the results in the system.

## Billing

The billing system includes the following features:

- **Aggregated Estimates and Invoices**: The system can create aggregated estimates for multiple locations on one estimate, and the same functionality for invoices to be paid.
- **Regional Cues**: The system has a cue for each region, store, manager, etc., to organize and manage billing efficiently.
- **Integration with Task Management**: The billing system is integrated with the task management system to ensure that cost estimates and final costs for each task are accurately reflected in the billing process.
- **Inventory Linkage**: Each item on the inventory list is linked to a task, allowing office staff to view the task and understand why the item is needed, which helps in generating accurate invoices.
- **User-Friendly Interface**: The billing system provides a user-friendly interface for creating, managing, and reviewing estimates and invoices.
- **Notifications and Reminders**: The system includes notifications and reminders for pending invoices and payment deadlines to ensure timely billing and payment.
- **Secure Data Handling**: The billing system implements secure data handling practices, including encryption of sensitive information and secure communication channels.
- **Audit and Reporting**: The system provides detailed billing reports and maintains an audit trail of all billing-related activities for accountability and transparency.

## Dashboard of Admins/Office Staff

The dashboard interface includes the following features:

- **Employee Tracking**: The dashboard shows who is on the clock, where they are, what tasks they've completed, and what tasks they have yet to complete for the day.
- **Live Location Data**: The dashboard includes live location data so that the office staff knows where employees are and what needs to be completed.
- **Task Dependencies and Subtasks**: The dashboard provides a visual representation of task dependencies and subtasks to help users understand the relationships between tasks.
- **Task Comments and Attachments**: Users can add comments to tasks for better communication and collaboration. Files, images, and documents can be attached to tasks, providing additional context and information. A version history for comments and attachments is implemented to track changes and updates over time.
- **Notifications and Reminders**: The dashboard includes notifications and reminders for approaching deadlines to keep employees on track.
- **Task Prioritization**: Tasks can be assigned priority levels (e.g., high, medium, low) to help employees and dispatchers focus on the most critical tasks first.
- **Task Deadlines**: The dashboard includes a deadline field for each task to ensure timely completion and to help with scheduling and planning.

## Scheduler

The scheduler includes the following features:

- **Task Analysis**: The scheduler analyzes where each employee is or the region they work out of.
- **Task List Building**: The scheduler builds out their task list according to the times it will take to complete tasks, their hours on the clock, and the proximity between tasks.
- **Auto-Fill or Propose Schedules**: The scheduler auto-fills or proposes a schedule for each employee as tasks come in from the client.
- **Statewide Company Support**: The scheduler supports a statewide company with multiple employees and warehouses across the state.
- **Auto-Assign Tasks**: The scheduler auto-assigns tasks accordingly, reducing the time to schedule tasks for office staff.
- **Drive Time Tracking**: The scheduler uses the Google Maps API to track drive time to/from each location automatically.
- **Real-Time Updates**: The scheduler provides real-time updates to the frontend interfaces for MacOS, iOS, and VisionOS.
- **Role-Based Access Control (RBAC)**: The scheduler ensures that users can only access the features and data relevant to their roles.
- **Notifications**: The scheduler sends push notifications to employees' devices to inform them of their daily task sheets and any updates.
- **Offline Support**: The scheduler implements offline support, allowing users to continue working even when they are not connected to the internet. Once the connection is restored, the scheduler synchronizes the offline data with the backend API.
- **Conflict Resolution**: The scheduler enforces data consistency rules to prevent conflicts and ensure that all platforms have the same data.
- **User-Friendly Interface**: The scheduler provides a user-friendly interface for managing schedules and task assignments.
