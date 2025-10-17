
import { useNavigate } from 'react-router-dom';
import LoginForm from "../components/LoginForm";

export default function Register({onLoginChange, onMessageChange, message}) {

    const navigate = useNavigate();
    const endpoint = '/api/accounts/register/';

    const processRegisterData = (data) => {
        // TODO: implement registration specific procedures
        console.log("email:", data.email);
        console.log("password:", data.password);
        onLoginChange(true);
        navigate('/reg-confirm', {state : { submitData: data.email}});
    };

    return (
        <div className="formbox">
            <h2>Create Account</h2>
            {message ? (
                <>
                <p class="alert">{message}</p>
                </>
            ) : (<></>)
            }
            <LoginForm endpoint={endpoint} processData={processRegisterData} onMessageChange={onMessageChange} />
        </div>
    );
}