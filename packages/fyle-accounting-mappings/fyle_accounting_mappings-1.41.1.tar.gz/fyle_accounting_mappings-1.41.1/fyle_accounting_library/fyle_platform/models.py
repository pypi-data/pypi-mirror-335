from typing import Any


class ExpenseGroupSettingsAdapter:
    """
    Adapter class to handle different column names across integrations
    """
    # Mapping of column names for different integrations
    COLUMN_MAPPINGS = {
        'default': {
            'id': 'id',
            'reimbursable_expense_group_fields': 'reimbursable_expense_group_fields',
            'corporate_credit_card_expense_group_fields': 'corporate_credit_card_expense_group_fields',
            'expense_state': 'expense_state',
            'reimbursable_expense_state': 'reimbursable_expense_state',
            'ccc_expense_state': 'ccc_expense_state',
            'reimbursable_export_date_type': 'reimbursable_export_date_type',
            'ccc_export_date_type': 'ccc_export_date_type',
            'import_card_credits': 'import_card_credits',
            'split_expense_grouping': 'split_expense_grouping',
            'workspace': 'workspace',
            'created_at': 'created_at',
            'updated_at': 'updated_at'
        }
    }
    COLUMN_MAPPINGS['xero'] = dict(COLUMN_MAPPINGS['default'])
    COLUMN_MAPPINGS['xero']['expense_state'] = 'reimbursable_expense_state'

    def __init__(self, settings_model: Any, integration_type: str = 'default'):
        """
        Initialize adapter with settings model and integration type
        :param settings_model: Django model instance containing settings
        :param integration_type: Type of integration (e.g. 'default', 'xero')
        """
        self.settings = settings_model
        self.mapping = self.COLUMN_MAPPINGS.get(integration_type, self.COLUMN_MAPPINGS['default'])

    def __getattr__(self, name: str) -> Any:
        """
        Get attribute using the mapping
        :param name: Attribute name
        :return: Mapped value from settings
        """
        if name in self.mapping:
            mapped_name = self.mapping[name]
            # Safely get the mapped attribute, return None if it doesn't exist
            return getattr(self.settings, mapped_name, None)

        return getattr(self.settings, name)
