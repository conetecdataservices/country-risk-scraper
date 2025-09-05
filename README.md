To scrap data from Watson page to get information on each country's risk level.

**Note**: If the workflow fails due to expiry of secret in future, follow the below steps to update the secret PLAYWRIGHT_AUTH_B64  :

          1. Download login_once.py to your desktop(Location: Desktop)
          
          2. Makes sure Python 3 is installed in your system.
          
          3. Open Terminal (or PowerShell) window and run these commands:
              python -m pip install --upgrade pip playwright
              python -m playwright install chromium
              
          4. Run this command after above package installtions: python login_once.py
              -- A Chromium window opens.
              -- Sign in with Microsoft (company email + password + MFA if exists).
              -- Wait until you actually see the Watson Rules page.
              -- Return to the Command terminal and press Enter.
              
          5. Run this command in terminal to create auth.json and to convert it into Base64 string format
              [Convert]::ToBase64String([IO.File]::ReadAllBytes("auth.json")) | Set-Clipboard
              
          6. Update the secret in the repository:
              -- Go to the GitHub repo → Settings → Secrets and variables → Actions.
              -- Click secret PLAYWRIGHT_AUTH_B64.
              -- Paste the base64 text from your clipboard into the Value box.
              -- Save (Add/Update secret).

