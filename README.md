***CSE451 Computer and Network Security - Secure Email Communication System***

This project implements a secure email communication system with robust encryption features, leveraging Microsoft Outlook for seamless integration. Below is a concise README guide:

### Features:
- **Outlook Integration:** Utilizes Outlook servers for email transmission, providing a familiar interface for users.
- **AES Encryption:** Employs Advanced Encryption Standard (AES) for secure encryption of email content, attachments, and metadata.
- **Digital Signatures:** Enhances security with digital signatures, ensuring sender verification and content integrity.
- **Firebase Key Management:** Safely manages public keys on Firebase, with private keys stored locally, preventing key errors.

### Usage:
1. **Requirements:**
   - Python environment
   - Necessary libraries (Google Cloud Firestore, cryptography, PyQt5)

2. **Setup:**
   - Install required libraries using `pip install -r requirements.txt`.
   - Ensure Outlook is configured for the user.

3. **Run Application:**
   - Execute `main.py` to launch the secure email client.
   - Compose, send, and view secure emails with ease.

### File Structure:
- `main.py`: Main application file for the secure email client.
- `encryption.py`, `decryption.py`: Handling encryption and decryption mechanisms.
- `outlook.py`: Integrating with Outlook servers for email functionalities.
- `firebase_handler.py`: Managing public keys securely on Firebase.

### Security Testing:
- Rigorous security testing has been conducted to validate encryption, key management, and Outlook integration.
- Email transmission via Outlook servers ensures reliability and secure communication.

### Notes:
- Files are read as bytes and encrypted for secure attachment handling.
- Subject line "Secure Email Through Team 7" aids in efficient inbox filtering.

### Appendix:
- Detailed implementation code is available in the project's code repository.

### Contributors:
- Team 7

**CSE451 Computer and Network Security**