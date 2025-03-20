import pytest

from src.edge_api_client import EdgeAPI

edge = EdgeAPI()
affiliate_permissions = EdgeAPI(api_key='d2f2f34bdc8f45a687bc231faab4496e')


def test_change_affiliate_offer_approval():
    aos = edge.get_affiliate_offer_settings(affiliate_id=3055, offer_id=310841)
    current_status = aos.json()[0]['status']

    if current_status == 'Approved':
        target_status = 'Denied'
    elif current_status == 'Denied':
        target_status = 'Applied'
    elif current_status == 'Applied':
        target_status = 'Approved'
    else:
        # this should never happen
        pytest.fail()
        
    resp = edge.change_affiliate_offer_approval(affiliate_id=3055, offer_id=310841, status=target_status)

    assert resp.status_code == 200
    assert resp.json()[0]['status'] == target_status


def test_get_offer_approvals():
    resp = edge.get_offer_approvals(offer_id=310841)
    assert resp.status_code == 200

    bad_resp = affiliate_permissions.get_offer_approvals(offer_id=310841)
    assert bad_resp.status_code != 200


# TODO: add test create offer 
