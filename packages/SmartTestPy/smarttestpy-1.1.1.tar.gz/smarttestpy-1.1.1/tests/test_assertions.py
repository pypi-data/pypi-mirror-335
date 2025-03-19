import pytest

from SmartTestPy.assertions import (assert_equal_with_message,
                                    assert_in_response, assert_status_code)


# 🔄 Classe mock para simular respostas
class MockResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


# ✅ Testes para assert_status_code
def test_assert_status_code_pass():
    response = MockResponse(200, "OK")
    assert_status_code(response, 200)


def test_assert_status_code_fail():
    response = MockResponse(404, "Not Found")
    with pytest.raises(AssertionError, match="❌ Código de status inválido"):
        assert_status_code(response, 200)


# 🔍 Testes para assert_in_response
def test_assert_in_response_pass():
    response = MockResponse(200, "Usuário cadastrado com sucesso!")
    assert_in_response(response, "cadastrado")


def test_assert_in_response_fail():
    response = MockResponse(200, "Operação concluída.")
    with pytest.raises(AssertionError, match="❌ Conteúdo 'cadastrado' não encontrado"): # noqa501
        assert_in_response(response, "cadastrado")


# ⚡ Testes para assert_equal_with_message
def test_assert_equal_with_message_pass():
    assert_equal_with_message(5 * 2, 10, "Multiplicação incorreta.")


def test_assert_equal_with_message_fail():
    with pytest.raises(AssertionError, match="❌ Multiplicação incorreta."):
        assert_equal_with_message(5 * 2, 12, "Multiplicação incorreta.")


def test_assert_equal_with_default_message():
    with pytest.raises(AssertionError, match="❌ Valores não correspondem."):
        assert_equal_with_message("abc", "def")


# 🏃 Para rodar os testes, execute:
# pytest tests/test_assertions.py --maxfail=1 --disable-warnings -v

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_assertions.py"])
