import pytest

from SmartTestPy.fixtures import mock_response_200  # noqa
from SmartTestPy.fixtures import fake_company, fake_product, fake_user  # noqa


# 🧪 Testes para a fixture fake_user
def test_fake_user(fake_user): # noqa
    """✅ Testa se a fixture fake_user gera dados válidos."""
    user = fake_user
    assert "name" in user
    assert "email" in user
    assert "address" in user
    assert "phone_number" in user
    assert "birthdate" in user
    assert "@" in user["email"], "❌ E-mail inválido."


# 🏢 Testes para a fixture fake_company
def test_fake_company(fake_company): # noqa
    """🏢 Testa se a fixture fake_company gera dados válidos."""
    company = fake_company
    assert "company_name" in company
    assert "catch_phrase" in company
    assert "address" in company
    assert "website" in company
    assert company["website"].startswith("http"), "❌ URL inválida."


# 🛒 Testes para a fixture fake_product
def test_fake_product(fake_product): # noqa
    """🛒 Testa se a fixture fake_product gera dados válidos."""
    product = fake_product
    assert "product_name" in product
    assert "price" in product
    assert product["price"] > 0, "❌ Preço deve ser positivo."
    assert "description" in product
    assert "created_at" in product


# ✅ Testes para mock_response_200
def test_mock_response_200(mock_response_200): # noqa
    """✅ Testa se a fixture mock_response_200 retorna código 200 e texto OK."""
    response = mock_response_200
    assert response.status_code == 200, "❌ Status code inválido."
    assert response.text == "OK", "❌ Texto da resposta incorreto."


# 🏃 **Execução dos testes**
if __name__ == "__main__":
    pytest.main(["-v", "tests/test_fixtures.py"])
if __name__ == "__main__":
    pytest.main(["-v", "tests/test_fixtures.py"])
