from enum import Enum

class EmailProvider(str, Enum):
    SMTP = 'smtp'
    SENDGRID = 'sendgrid'

class SettingType(str, Enum):
    EMAIL = 'email'
    SECURITY = 'security'
    KYC = 'kyc'
    COMMISSION = 'commission'

class SettingStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    PENDING = 'pending'

class ContentType(str, Enum):
    TEXT = 'text'
    HTML = 'html'

class BaseEmailVariables:
    """Base variables available for all system emails"""
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    ID = "id"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    LOCATION = "location"
    CP_URL = "cp_url"
    CRM_URL = "crm_url"

    CP_LOGIN_LINK = "cp_login_link"
    CRM_LOGIN_LINK = "crm_login_link"

    # Customer related
    CUSTOMER_NAME = "customer_name"
    CUSTOMER_EMAIL = "customer_email"
    CUSTOMER_PHONE = "customer_phone"
    CUSTOMER_ADDRESS = "customer_address"
    CUSTOMER_CITY = "customer_city"
    CUSTOMER_STATE = "customer_state"
    CUSTOMER_ZIP = "customer_zip"
    CUSTOMER_COUNTRY = "customer_country"
    CUSTOMER_ID = "customer_id"
    CUSTOMER_FIRST_NAME = "customer_first_name"
    CUSTOMER_LAST_NAME = "customer_last_name"
    CUSTOMER_CRM_LINK = "customer_crm_link"
    # User related
    USER_NAME = "user_name"  # Full name of the user
    USER_EMAIL = "user_email"  # Email address of the user
    USER_FIRST_NAME = "user_first_name"  # First name of the user
    USER_LAST_NAME = "user_last_name"  # Last name of the user
    # Company related
    COMPANY_NAME = "company_name"  # Name of the company
    COMPANY_ADDRESS = "company_address"  # Company address
    COMPANY_PHONE = "company_phone"  # Company phone number
    COMPANY_EMAIL = "company_email"  # Company email address
    COMPANY_WEBSITE = "company_website"  # Company website URL
    APP_NAME = "app_name"  # Name of the application
    APP_URL = "app_url"  # Base URL of the application
    CURRENT_DATE = "current_date"  # Current date
    CURRENT_TIME = "current_time"  # Current time
    SUPPORT_EMAIL = "support_email"  # Support email address
    LOGO_URL = "logo_url"  # URL to company logo

    # Common
    TICKET_NUMBER = "ticket_number"  # Ticket number
    TICKET_URL = "ticket_url"  # Ticket URL
    FEEDBACK_LINK = "feedback_link"  # Feedback link
    VERIFICATION_LINK = "verification_link"  # Verification link
    EXPIRY_TIME = "expiry_time"  # Expiry time
    CODE = "code"  # Code
    REASON = "reason"  # Reason
    STATUS = "status"  # Status
    SEVERITY = "severity"  # Severity
    ACTION_REQUIRED = "action_required"  # Action required
    ACTION_URL = "action_url"  # Action URL

    @classmethod
    def get_all_variables(cls) -> list:
        """Get all base variables as a list"""
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]

    @classmethod
    def get_variable_descriptions(cls) -> dict:
        """Get descriptions for all base variables"""
        return {
            cls.CP_URL: "URL to the CP",
            cls.CRM_URL: "URL to the CRM",
            cls.CRM_LOGIN_LINK: "Login link for the CRM",
            cls.CP_LOGIN_LINK: "Login link for the CP",
            cls.NAME: "Full name of the receiver (customer or user, can be used when both details are not required)",
            cls.EMAIL: "Email address of the receiver (customer or user, can be used when both details are not required)",
            cls.PHONE: "Phone number of the receiver (customer or user, can be used when both details are not required)",
            cls.ID: "ID of the receiver (customer or user, can be used when both details are not required)",
            cls.FIRST_NAME: "First name of the receiver (customer or user, can be used when both details are not required)",
            cls.LAST_NAME: "Last name of the receiver (customer or user, can be used when both details are not required)",
            cls.LOCATION: "Location of the receiver (customer or user, can be used when both details are not required)",
            cls.CUSTOMER_NAME: "Full name of the customer",
            cls.CUSTOMER_ID: "ID of the customer",
            cls.CUSTOMER_EMAIL: "Email address of the customer",
            cls.CUSTOMER_PHONE: "Phone number of the customer",
            cls.CUSTOMER_ADDRESS: "Address of the customer",
            cls.CUSTOMER_CITY: "City of the customer",
            cls.CUSTOMER_STATE: "State of the customer",
            cls.CUSTOMER_ZIP: "Zip code of the customer",
            cls.CUSTOMER_COUNTRY: "Country of the customer",
            cls.CUSTOMER_FIRST_NAME: "First name of the customer",
            cls.CUSTOMER_LAST_NAME: "Last name of the customer",
            cls.USER_NAME: "Full name of the user",
            cls.USER_EMAIL: "Email address of the user",
            cls.USER_FIRST_NAME: "First name of the user",
            cls.USER_LAST_NAME: "Last name of the user",
            cls.COMPANY_NAME: "Name of the company",
            cls.COMPANY_ADDRESS: "Company address",
            cls.COMPANY_PHONE: "Company phone number",
            cls.COMPANY_EMAIL: "Company email address",
            cls.COMPANY_WEBSITE: "Company website URL",
            cls.APP_NAME: "Name of the application",
            cls.APP_URL: "Base URL of the application",
            cls.CURRENT_DATE: "Current date",
            cls.CURRENT_TIME: "Current time",
            cls.SUPPORT_EMAIL: "Support email address",
            cls.LOGO_URL: "URL to company logo",
            cls.TICKET_NUMBER: "Ticket number",
            cls.TICKET_URL: "Ticket URL",
            cls.FEEDBACK_LINK: "Feedback link",
            cls.VERIFICATION_LINK: "Verification link",
            cls.EXPIRY_TIME: "Expiry time",
            cls.CODE: "Code",
            cls.REASON: "Reason",
            cls.STATUS: "Status",
            cls.SEVERITY: "Severity",
            cls.ACTION_REQUIRED: "Action required",
            cls.ACTION_URL: "Action URL"
        } 

class SystemEmailTrigger:
    """System email trigger events and their descriptions"""
    
    # Authentication related
    LOGIN_NOTIFICATION = "login_notification"
    LOGIN_FAILED_NOTIFICATION = "login_failed_notification"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"
    TWO_FACTOR_CODE = "two_factor_code"
    ACCESS_CHANGED = "access_changed"
    TWO_FACTOR_STATUS_CHANGED = "two_factor_status_changed"
    SECURITY_KEY_STATUS_CHANGED = "security_key_status_changed"
    
    # Customer related
    CUSTOMER_WELCOME_LIVE_EMAIL = "customer_welcome_live_email"
    CUSTOMER_WELCOME_DEMO_EMAIL = "customer_welcome_demo_email"
    CUSTOMER_WELCOME_IB_EMAIL = "customer_welcome_ib_email"
    CUSTOMER_AGENT_ASSIGNED = "customer_agent_assigned"
    CUSTOMER_AGENT_UNASSIGNED = "customer_agent_unassigned"
    CUSTOMER_FEEDBACK = "customer_feedback"
    CUSTOMER_SUPPORT = "customer_support"
    ACCOUNT_UPDATED = "account_updated"

    # User related
    USER_WELCOME_EMAIL = "user_welcome_email"
    USER_CUSTOMER_ASSIGNED = "user_customer_assigned"
    USER_CUSTOMER_UNASSIGNED = "user_customer_unassigned"
    USER_CUSTOMER_ADDED = "user_customer_added"

    # System related
    SYSTEM_ALERT = "system_alert"
    MAINTENANCE_NOTIFICATION = "maintenance_notification"
    SECURITY_ALERT = "security_alert"

    @classmethod
    def get_all_triggers(cls) -> list:
        """Get all trigger events as a list"""
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]

    @classmethod
    def get_trigger_descriptions(cls) -> dict:
        """Get descriptions for all trigger events"""
        return {
            cls.LOGIN_NOTIFICATION: "Sent when a user/customer logs in",
            cls.LOGIN_FAILED_NOTIFICATION: "Sent when a user's/customer's login attempt fails",
            cls.PASSWORD_RESET: "Sent when a user/customer requests a password reset",
            cls.EMAIL_VERIFICATION: "Sent to verify a user's/customer's email address",
            cls.TWO_FACTOR_CODE: "Sent with two-factor authentication code",
            cls.ACCESS_CHANGED: "Sent when a user's/customer's access level is changed",
            cls.TWO_FACTOR_STATUS_CHANGED: "Sent when two-factor authentication status is changed",
            cls.SECURITY_KEY_STATUS_CHANGED: "Sent when security key status is changed",
            
            cls.CUSTOMER_WELCOME_LIVE_EMAIL: "Sent when a customer registers via /live or added as a client in the crm",
            cls.CUSTOMER_WELCOME_DEMO_EMAIL: "Sent when a customer registers via /demo or added as a lead in the crm",
            cls.CUSTOMER_WELCOME_IB_EMAIL: "Sent when a customer registers via /ib or added as a ib in the crm",
            cls.CUSTOMER_AGENT_ASSIGNED: "Sent when a customer is assigned to an agent",
            cls.CUSTOMER_AGENT_UNASSIGNED: "Sent when a customer is unassigned from an agent",
            cls.CUSTOMER_FEEDBACK: "Sent to request customer feedback",
            cls.CUSTOMER_SUPPORT: "Sent in response to customer support requests",
            cls.ACCOUNT_UPDATED: "Sent when account details are updated",
            
            cls.USER_WELCOME_EMAIL: "Sent when a new user registers/added to the system",
            cls.USER_CUSTOMER_ASSIGNED: "Sent when a user is assigned to a customer",
            cls.USER_CUSTOMER_UNASSIGNED: "Sent when a user is unassigned from a customer",
            cls.USER_CUSTOMER_ADDED: "Sent when a user is assigned to a customer",

            cls.SYSTEM_ALERT: "Sent for important system alerts",
            cls.MAINTENANCE_NOTIFICATION: "Sent for scheduled maintenance notifications",
            cls.SECURITY_ALERT: "Sent for security-related alerts"
        }

    @classmethod
    def get_trigger_variables(cls) -> dict:
        """Get required variables for each trigger event"""
        return {
            cls.LOGIN_NOTIFICATION: ["name", "ip", "location"],
            cls.LOGIN_FAILED_NOTIFICATION: ["name", "ip", "location"],
            cls.PASSWORD_RESET: ["name", "verification_link", "expiry_time"],
            cls.EMAIL_VERIFICATION: ["name", "code", "expiry_time"],
            cls.TWO_FACTOR_CODE: ["name", "code", "expiry_time"],
            cls.ACCESS_CHANGED: ["name", "reason", "support_contact", "status"],
            cls.TWO_FACTOR_STATUS_CHANGED: ["name", "status"],
            cls.SECURITY_KEY_STATUS_CHANGED: ["name", "status"],
            
            cls.CUSTOMER_WELCOME_LIVE_EMAIL: ["name", "cp_login_link"],
            cls.CUSTOMER_WELCOME_DEMO_EMAIL: ["name", "cp_login_link"],
            cls.CUSTOMER_WELCOME_IB_EMAIL: ["name", "cp_login_link"],
            cls.CUSTOMER_AGENT_ASSIGNED: ["customer_name", "user_name", "cp_login_link"],
            cls.CUSTOMER_AGENT_UNASSIGNED: ["customer_name", "user_name", "cp_login_link"],
            cls.CUSTOMER_FEEDBACK: ["user_name", "feedback_link"],
            cls.CUSTOMER_SUPPORT: ["ticket_number", "support_message"],
            cls.ACCOUNT_UPDATED: ["user_name", "updated_fields"],

            cls.USER_WELCOME_EMAIL: ["name", "crm_login_link"],
            cls.USER_CUSTOMER_ASSIGNED: ["customer_name", "user_name", "crm_login_link", "customer_crm_link"],
            cls.USER_CUSTOMER_UNASSIGNED: ["customer_name", "user_name", "crm_login_link", "customer_crm_link"],
            cls.USER_CUSTOMER_ADDED: ["customer_name", "user_name", "crm_login_link", "customer_crm_link"],
            
            cls.SYSTEM_ALERT: ["alert_message", "severity", "action_required"],
            cls.MAINTENANCE_NOTIFICATION: ["start_time", "end_time", "affected_services"],
            cls.SECURITY_ALERT: ["alert_type", "alert_message", "recommended_action"]
        }

# Variable classes for different types of emails
class AuthenticationEmailVariables:
    """Variables specific to authentication-related emails"""
    IP_ADDRESS = "ip_address"
    BROWSER = "browser"
    DEVICE = "device"
    LOCATION = "location"
    VERIFICATION_CODE = "verification_code"
    VERIFICATION_LINK = "verification_link"
    EXPIRY_TIME = "expiry_time"
    ACCESS_LEVEL = "access_level"
    PREVIOUS_ACCESS = "previous_access"
    NEW_ACCESS = "new_access"
    SECURITY_STATUS = "security_status"

    @classmethod
    def get_all_variables(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]

    @classmethod
    def get_variable_descriptions(cls) -> dict:
        return {
            cls.IP_ADDRESS: "IP address of the login attempt",
            cls.BROWSER: "Browser used for the login attempt",
            cls.DEVICE: "Device used for the login attempt",
            cls.LOCATION: "Location of the login attempt",
            cls.VERIFICATION_CODE: "Code for email verification or 2FA",
            cls.VERIFICATION_LINK: "Link for email verification or password reset",
            cls.EXPIRY_TIME: "Expiry time for verification code/link",
            cls.ACCESS_LEVEL: "User's access level",
            cls.PREVIOUS_ACCESS: "Previous access level",
            cls.NEW_ACCESS: "New access level",
            cls.SECURITY_STATUS: "Status of security feature"
        }

class CustomerEmailVariables:
    """Variables specific to customer-related emails"""
    ACCOUNT_TYPE = "account_type"
    ACCOUNT_NUMBER = "account_number"
    ACCOUNT_STATUS = "account_status"
    ASSIGNED_AGENT = "assigned_agent"
    PREVIOUS_AGENT = "previous_agent"
    FEEDBACK_LINK = "feedback_link"
    TICKET_NUMBER = "ticket_number"
    TICKET_STATUS = "ticket_status"
    TICKET_PRIORITY = "ticket_priority"
    SUPPORT_MESSAGE = "support_message"
    UPDATED_FIELDS = "updated_fields"

    @classmethod
    def get_all_variables(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]

    @classmethod
    def get_variable_descriptions(cls) -> dict:
        return {
            cls.ACCOUNT_TYPE: "Type of customer account (live/demo/ib)",
            cls.ACCOUNT_NUMBER: "Customer's account number",
            cls.ACCOUNT_STATUS: "Status of customer's account",
            cls.ASSIGNED_AGENT: "Name of assigned agent",
            cls.PREVIOUS_AGENT: "Name of previously assigned agent",
            cls.FEEDBACK_LINK: "Link to provide feedback",
            cls.TICKET_NUMBER: "Support ticket number",
            cls.TICKET_STATUS: "Status of support ticket",
            cls.TICKET_PRIORITY: "Priority of support ticket",
            cls.SUPPORT_MESSAGE: "Support message or response",
            cls.UPDATED_FIELDS: "List of updated account fields"
        }

class SystemEmailVariables:
    """Variables specific to system-related emails"""
    ALERT_TYPE = "alert_type"
    ALERT_MESSAGE = "alert_message"
    SEVERITY = "severity"
    ACTION_REQUIRED = "action_required"
    MAINTENANCE_START = "maintenance_start"
    MAINTENANCE_END = "maintenance_end"
    AFFECTED_SERVICES = "affected_services"
    SYSTEM_STATUS = "system_status"
    ERROR_DETAILS = "error_details"
    RESOLUTION_STEPS = "resolution_steps"

    @classmethod
    def get_all_variables(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]

    @classmethod
    def get_variable_descriptions(cls) -> dict:
        return {
            cls.ALERT_TYPE: "Type of system alert",
            cls.ALERT_MESSAGE: "Alert message details",
            cls.SEVERITY: "Severity level of the alert",
            cls.ACTION_REQUIRED: "Required action to be taken",
            cls.MAINTENANCE_START: "Start time of maintenance",
            cls.MAINTENANCE_END: "End time of maintenance",
            cls.AFFECTED_SERVICES: "Services affected by maintenance/issue",
            cls.SYSTEM_STATUS: "Current system status",
            cls.ERROR_DETAILS: "Detailed error information",
            cls.RESOLUTION_STEPS: "Steps to resolve the issue"
        }

class TriggerVariableMapping:
    """Maps trigger events to their specific variable classes"""
    MAPPINGS = {
        # Authentication triggers
        "login_notification": AuthenticationEmailVariables,
        "login_failed_notification": AuthenticationEmailVariables,
        "password_reset": AuthenticationEmailVariables,
        "email_verification": AuthenticationEmailVariables,
        "two_factor_code": AuthenticationEmailVariables,
        "access_changed": AuthenticationEmailVariables,
        "two_factor_status_changed": AuthenticationEmailVariables,
        "security_key_status_changed": AuthenticationEmailVariables,
        
        # Customer triggers
        "customer_welcome_live_email": CustomerEmailVariables,
        "customer_welcome_demo_email": CustomerEmailVariables,
        "customer_welcome_ib_email": CustomerEmailVariables,
        "customer_agent_assigned": CustomerEmailVariables,
        "customer_agent_unassigned": CustomerEmailVariables,
        "customer_feedback": CustomerEmailVariables,
        "customer_support": CustomerEmailVariables,
        "account_updated": CustomerEmailVariables,
        
        # System triggers
        "system_alert": SystemEmailVariables,
        "maintenance_notification": SystemEmailVariables,
        "security_alert": SystemEmailVariables
    }

    @classmethod
    def get_variables_for_trigger(cls, trigger_event: str) -> tuple:
        """Get all available variables for a trigger event"""
        # Always include base variables
        variables = BaseEmailVariables.get_all_variables()
        descriptions = BaseEmailVariables.get_variable_descriptions()
        
        # Add trigger-specific variables
        if trigger_event in cls.MAPPINGS:
            variable_class = cls.MAPPINGS[trigger_event]
            variables.extend(variable_class.get_all_variables())
            descriptions.update(variable_class.get_variable_descriptions())
        
        return variables, descriptions 
    
class AccountType(str, Enum):
    LIVE = 'LIVE'
    DEMO = 'DEMO'
    IB = 'IB'

    @classmethod
    def get_all_types(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]

