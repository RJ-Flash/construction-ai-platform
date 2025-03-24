# Subscription Management System

The Construction AI Platform includes a comprehensive subscription management system to handle different pricing tiers, plugin licenses, and usage tracking.

## Key Components

1. **Organizations**: The top-level entity that represents a customer. An organization can have multiple users, and all users within an organization share the same subscription plan.

2. **Subscriptions**: Defines the service level for an organization, including:
   - Plan type (Free, Starter, Essential, Professional, Advanced, Ultimate)
   - Document limits
   - User limits
   - Pricing information
   - Billing cycle (monthly/annual)

3. **Plugin Licenses**: Specialized plugin modules that can be purchased separately:
   - Each plugin requires a license
   - Licenses can be one-time, monthly, or annual
   - Licenses are tied to an organization

4. **Usage Tracking**: Records usage events for billing and analytics:
   - Document uploads
   - Document analysis
   - Plugin usage

## Database Models

The following models are implemented:

1. **Organization**: Represents a customer with subscription
2. **Subscription**: Defines the service level and limits
3. **PluginLicense**: Represents purchased plugin licenses
4. **UsageRecord**: Tracks usage for billing purposes

## API Endpoints

The subscription API is available at `/api/subscriptions` and includes the following endpoints:

### Organization Management

- `GET /api/subscriptions/{organization_id}` - Get organization details
- `POST /api/subscriptions/` - Create a new organization

### Subscription Management

- `GET /api/subscriptions/subscription/{subscription_id}` - Get subscription details
- `POST /api/subscriptions/subscription/` - Create a new subscription
- `PUT /api/subscriptions/subscription/{subscription_id}` - Update subscription
- `POST /api/subscriptions/subscription/{subscription_id}/reset-usage` - Reset usage counters
- `GET /api/subscriptions/subscription/{subscription_id}/expiry-status` - Check subscription expiry status

### Plugin License Management

- `GET /api/subscriptions/plugins/{organization_id}` - Get organization's plugin licenses
- `POST /api/subscriptions/plugins/` - Create a new plugin license
- `PUT /api/subscriptions/plugins/{plugin_id}` - Update plugin license
- `GET /api/subscriptions/plugins/{organization_id}/check/{plugin_id}` - Check plugin access

### Usage Management

- `POST /api/subscriptions/usage/` - Record a usage event
- `GET /api/subscriptions/usage/{organization_id}` - Get organization usage stats
- `GET /api/subscriptions/organization/{organization_id}/can-upload-document` - Check if document upload is allowed

### Plan Information

- `GET /api/subscriptions/plans/` - Get subscription plan information

### User Organization Management

- `POST /api/subscriptions/organization/{organization_id}/users/{user_id}` - Add user to organization
- `DELETE /api/subscriptions/organization/users/{user_id}` - Remove user from organization

## Subscription Service

The `SubscriptionService` class provides a clean interface for interacting with subscription-related functionality:

- Organization management
- Subscription creation and updates
- License management
- Usage tracking
- Access control checks

## Subscription Enforcement

The system enforces subscription limits at several points:

1. **Document Uploads**: Checks if the organization has reached its document limit
2. **Plugin Access**: Validates if the organization has a valid license for specific plugins
3. **User Limits**: Ensures the organization doesn't exceed its user seat limit

## Pricing Tiers

The system implements the following subscription plans:

1. **Free**
   - 1 PDF per month
   - 1 user
   - Basic features only

2. **Starter** ($49/month)
   - 5 PDFs per month
   - 1 user
   - Basic features

3. **Essential** ($129/month)
   - 10 documents per month
   - 3 users
   - PDF, CAD & BIM support
   - 1 specialized plugin included

4. **Professional** ($249/month)
   - 20 documents per month
   - 5 users
   - Priority analysis
   - 2 specialized plugins included

5. **Advanced** ($599/month)
   - 40 documents per month
   - 10 users
   - All file formats supported
   - 3 specialized plugins included
   - API access

6. **Ultimate** ($999/month)
   - Unlimited documents
   - Unlimited users
   - All features and plugins included
   - Enterprise-level support
   - Custom integrations

## Annual Discount

All plans offer a 10-15% discount for annual billing:

- Starter: $529/year (save $59)
- Essential: $1,393/year (save $155)
- Professional: $2,690/year (save $298)
- Advanced: $5,990/year (save $1,198)
- Ultimate: $9,990/year (save $1,998)

## Implementation Details

### Organization-User Relationship

- Each User can belong to one Organization
- Organizations can have multiple Users
- The organization administrator has permission to add/remove users

### Document Usage Tracking

1. When a user uploads a document, the system:
   - Checks if the organization has reached its document limit
   - Records the usage event
   - Increments the organization's document counter

2. At the beginning of each billing cycle:
   - The document counter is reset to zero
   - A new usage period begins

### Plugin License Management

1. Plugin licenses can be:
   - One-time purchases (perpetual license)
   - Subscription-based (monthly or annual)

2. Each plugin license includes:
   - A unique license key
   - Activation/expiration dates
   - Usage permissions

3. The system validates license status before allowing plugin access

## Integration with Payment Processing

The subscription system is designed to integrate with payment processors like Stripe:

1. **Subscription Creation**: Creates a subscription record in the database and initiates the payment process
2. **Payment Webhook**: Updates subscription status when payment is successful
3. **Subscription Updates**: Changes in plan are synchronized with the payment processor
4. **Failed Payments**: Subscription status is updated when payments fail

## Subscription Management UI

The frontend provides interfaces for:

1. **Organization Dashboard**: Shows subscription status, usage metrics, and user management
2. **Subscription Management**: Allows plan selection, upgrades, and downgrades
3. **Plugin Marketplace**: For purchasing additional plugin licenses
4. **Usage Reports**: Visualization of document usage, analysis activity, and plugin utilization

## Security Considerations

1. **Role-Based Access Control**: Only organization administrators can manage subscriptions
2. **Payment Information**: No sensitive payment data is stored in the application database
3. **License Validation**: Plugin licenses are validated in real-time to prevent unauthorized access

## Testing

The subscription system includes comprehensive tests:

1. **Unit Tests**: For individual components of the subscription system
2. **Integration Tests**: Ensure proper interaction between subscription components
3. **End-to-End Tests**: Validate the complete subscription workflow

## Future Enhancements

Planned enhancements for the subscription system include:

1. **Metered Billing**: For usage beyond plan limits
2. **Team Management**: For organizing users into teams within an organization
3. **Custom Plans**: Ability to create tailored plans for enterprise customers
4. **Usage Analytics**: Advanced reporting and visualization of usage patterns
5. **Auto-scaling**: Automatic plan upgrades based on usage patterns
