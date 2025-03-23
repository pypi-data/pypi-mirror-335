# Facebook Auth

Un package Python per l'autenticazione con Facebook.

## Installazione

```bash
pip install facebook_auth


---

## **7. File `requirements.txt`**
Aggiungi le dipendenze del package.


---

## **8. Test del Package**
Crea dei test per verificare il funzionamento del package.

```python
# tests/test_client.py
import unittest
from facebook_auth.client import FacebookAuthClient

class TestFacebookAuthClient(unittest.TestCase):
    def test_get_auth_url(self):
        client = FacebookAuthClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://test.com/callback",
        )
        auth_url = client.get_auth_url()
        self.assertIn("https://www.facebook.com/v17.0/dialog/oauth", auth_url)

if __name__ == "__main__":
    unittest.main()
