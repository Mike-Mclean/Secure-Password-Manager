import { FaPen, FaTrash, FaClipboard } from "react-icons/fa";

export default function Guide() {
    return (
        <div>
            <h2>User Guide</h2>

            <hr />
            <h3>Introduction</h3>
            <p>Welcome to the Secure Password Manager! This web-based application is designed to help users securely store and manage their passwords. </p>
            <p>This guide provides detailed instructions for the use of the Secure Password Manager.</p>

            <hr />
            <h3>Account Management</h3>
            <p>To access your Account Settings, click the Account link in the navbar at the top of the screen. There you will be able to make modifications to your account, such as changing your password or enabling Multifactor Authentication.</p>
            
            <h4>Account Registration</h4>
            <p>To use the Secure Password Manager, you must first create an account. Click on the Create Account link in the navbar at the top of the screen. This will take you to the Create Account page. Enter your email address. This will be used as your unique username throughout the Secure Password Manager. Next enter a strong password. This will be your master password that will be used to encrypt and decrypt your vault contents. As an added layer of security, we do not store this password in plaintext on our servers. That means you are the only one with the key to decrypt your vault. Do not forget this password. Without it your vault would be permanently locked.</p>
            <p>Upon creating your account, will be automatically logged in and ready to start storing credentials in your vault.</p>
            
            <h4>Login</h4>
            <p>If you already have a Secure Password Manager account, you will need to log into the site to access your vault. Enter your email address and password into the login form and click Submit. If you have Multifactor Authentication enabled, you will then be asked to complete additional steps to complete the authentication process. Once authenticated you will have access to your vault.</p>

            <h4>Multifactor Authentication</h4>
            <p>Multifactor Authentication adds an additional layer of security to your account. Once enabled, upon login you will be sent a unique code that must be entered MFA input screen. Once authenticated you will have access to your secure vault.</p>
            <p>Multifactor Authentication can be enabled in your Account Settings. There are two options for receiving your code. You can either use an Authenticator App, or have the code emailed to you.</p>

            <h4>Change Password</h4>
            <p>To change your master password, click on the change password button in your Account Settings.</p>

            <h4>Logout</h4>
            <p>To logout of the Secure Password Manager, click Logout in the navbar at the top of the screen.</p>

            <hr />
            <h3>Vault Management</h3>
            <p>The Dashboard is where you will interact with your vault. Here you can add, edit, and delete credentials, and access your stored passwords.</p>

            <h4>Add Credentials</h4>
            <p>Click on the Add Credentials button at the top of the Dashboard. This will take you to the Add Credentials page. Enter the account name, username, and password into the form and submit. This will add the credentials to your vault. You will then be automatically redirected back to your dashboard where you will see your newly added credentials.</p>

            <h4>Edit Credentials</h4>
            <p>To edit a particular item in your vault, click on the edit icon ( <FaPen /> ) for the item. This will take you to the Edit Credentials page where you can change the account name, username, or password. Once you click submit the edits will be applied and you will be redirected back to your dashboard where you will see your edited credentials.</p>

            <h4>Delete Credentials</h4>
            <p>To delete a particular item in your vault, click on the trash can icon ( <FaTrash /> ) for the item. This will take you to a confirmation page where you will have a chance to review the item. To delete the item, click on the Delete button. The item will be deleted from your vault and you will be redirected back to your vault where you will see the item has been deleted. If you choose Cancel instead of delete, the item will not be deleted. You will be redirected back to your dashboard</p>

            <h4>Copy Password</h4>
            <p>To copy the password to the clipboard for an item in your vault, simply click the clipboard icon ( <FaClipboard /> ) for the item. You will then be able to paste the password into the login screen for that account.</p>
        </div>
    );
}