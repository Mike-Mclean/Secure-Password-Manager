import { NavLink, Link } from 'react-router'
import { useNavigate } from "react-router-dom";
import LoginForm from "../components/LoginForm";


export default function Login({onLoginChange, onMessageChange, message}) {

    const navigate = useNavigate();
    const endpoint = '/api/accounts/login/';

    const processLoginData = (data) => {
        if (data.mfa_totp_enabled) {
            navigate('/mfa-totp-input');
        } else if (data.mfa_enabled) {
            navigate('/mfa-challenge');
        } else {
            onLoginChange(true);         // Trigger navbar change
            navigate('/dashboard');
        }
    };

    return (
        <div className="formbox">
            <h2>Login</h2>
            {message ? (
                <>
                <p class="alert">{message}</p>
                </>
            ) : (<></>)
            }
            <LoginForm endpoint={endpoint} processData={processLoginData} onLoginChange={onLoginChange} onMessageChange={onMessageChange} />
        </div>
    );
}
