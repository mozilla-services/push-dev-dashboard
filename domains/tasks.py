from .models import DomainAuthorization


# TODO: decorate with celery.task
def validate_domain_authorizations():
    domain_authorizations = DomainAuthorization.objects.need_validation()
    for auth in domain_authorizations:
        auth.validate()
