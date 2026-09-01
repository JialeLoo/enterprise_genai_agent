# Production Deployment Rollback Runbook

A rollback should be considered when a newly deployed
version causes significant production degradation.

Operators should first verify service health, error rates
and downstream dependency status.

If the deployment is confirmed as the likely cause,
operators should roll back to the previously stable
application version.

After rollback, service health and application metrics
must be monitored to confirm recovery.

A production incident should be created when the impact
meets the organization's incident severity criteria.