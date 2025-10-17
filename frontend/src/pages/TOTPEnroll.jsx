import QRCodeEnrollment from "../components/Registration/TOTPEnrollQRCode";

function MFASetupPage() {
  return (
    <div>
      <h2>Multi-Factor Authentication Enrollment</h2>
      <QRCodeEnrollment />
    </div>
  );
}
export default MFASetupPage;