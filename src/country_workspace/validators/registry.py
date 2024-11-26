from strategy_field.registry import Registry

from country_workspace.validators.base import BeneficiaryGroupValidator


class NoopValidator(BeneficiaryGroupValidator):
    pass


class BeneficiaryValidatorRegistry(Registry):
    def get_name(self, entry):
        return entry.__name__


beneficiary_validator_registry = BeneficiaryValidatorRegistry(BeneficiaryGroupValidator)

beneficiary_validator_registry.register(NoopValidator)
