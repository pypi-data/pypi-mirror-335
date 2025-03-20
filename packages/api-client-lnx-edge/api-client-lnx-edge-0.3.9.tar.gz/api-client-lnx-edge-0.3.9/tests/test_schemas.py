import pytest
from marshmallow import ValidationError

from src.edge_api_client.utilities.schemas import AffiliateOfferSettingsSchema


def test_affiliate_offer_settings_schema():

    valid_data = {
        'affiliateId': 1234,
        'offerId': 567890,
        'status': 'Approved'
    }

    schema = AffiliateOfferSettingsSchema()
    result = schema.load(valid_data)

    assert result == valid_data

    invalid_data = {
        'affiliateId': 1234
    }

    with pytest.raises(ValidationError) as exc:
        schema.load(invalid_data)
    assert 'offerId' in str(exc.value.messages)
    
    invalid_data = {
        'affiliateId': 1234,
        'offerId': 567890
    }

    with pytest.raises(ValidationError) as exc:
        schema.load(invalid_data)
    assert 'status' in str(exc.value.messages)
