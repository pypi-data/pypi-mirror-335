def test_import():
    from dmtapi import DMTAPI

    api = DMTAPI(
        api_key="01JJE3CAFEZB6NDH51R08DC9XB", api_base_url="http://localhost:8000"
    )
    assert api.api_key == "01JJE3CAFEZB6NDH51R08DC9XB"
    assert api.account.api_base_url == "http://localhost:8000"
