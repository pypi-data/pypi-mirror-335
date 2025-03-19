# PyOTPX - Secure Email OTP Generator

PyOTPX is a **fully free, open-source OTP (One-Time Password) generator** with **email verification**.  
It allows developers to integrate secure OTP-based authentication into their applications.

## 🚀 Features
✅ **Secure OTP generation** (Randomized & Time-based)  
✅ **Email-based OTP sending** (via Gmail SMTP)  
✅ **Custom OTP expiration time**  
✅ **Lightweight & easy to use**  
✅ **No third-party dependencies**  

---

## 📌 Installation

To install PyOTPX, run:
```bash
pip install pyotpx
```

## 🔧 EXAMPLE

```python
from pyotpx import OTP, send_otp

otp_system = OTP()

email = "mail@example.com"
otp = otp_system.generate(email)

if send_otp(email, otp):
    print(f"🔹 OTP sent to {email}")

entered_otp = input("Enter OTP: ")
if otp_system.verify(email, entered_otp):
    print("✅ OTP Verified!")
else:
    print("❌ Invalid or Expired OTP!")
```