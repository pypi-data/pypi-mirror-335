import random
import time

class OTP:
    def __init__(self, length=6, expiry=300):
        self.length = length
        self.expiry = expiry
        self.otp_data = {}

    def generate(self, user):
        otp = ''.join(str(random.randint(0, 9)) for _ in range(self.length))
        self.otp_data[user] = {"otp": otp, "time": time.time()}
        return otp

    def verify(self, user, entered_otp):
        if user not in self.otp_data:
            return False
        data = self.otp_data[user]
        if time.time() - data["time"] > self.expiry:
            del self.otp_data[user]
            return False  # OTP expired
        return data["otp"] == entered_otp
