import React, { useEffect, useState } from "react";
import Cookies from 'js-cookie';
import { Link } from "react-router-dom";

const QRCodeEnrollment = () => {
  const [qrCodeData, setQrCodeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchQRCode = async () => {
      try {

        const response = await fetch('api/accounts/mfa/totp/enroll/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken') 
            },
            credentials: 'include',
        });

        if (!response.ok) {
          throw new Error("Failed to fetch QR code data");
        }
        const data = await response.json();
        setQrCodeData(data);
      } catch (err) {
        setError(err.message || "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    fetchQRCode();
  }, []); 

  if (loading) return <p>Loading QR code...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="qr-code-enrollment">
      <p>Scan this QR Code with your Authenticator App, then <Link to='/mfa-totp-input'>click here</Link> to enter the 6 digit code from your app.</p>
      <img src={qrCodeData.qr_code} alt="TOTP QR Code" />
      <p><strong>Secret:</strong> {qrCodeData.secret}</p>
      <p><strong>URI:</strong> <code>{qrCodeData.uri}</code></p>
    </div>
  );
};

export default QRCodeEnrollment;
