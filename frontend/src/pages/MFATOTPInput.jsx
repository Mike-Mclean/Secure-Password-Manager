import { useNavigate } from "react-router-dom";
import Cookies from 'js-cookie';
import { Link } from "react-router-dom";

export default function MFAInput({onLoginChange}) {
    const navigate = useNavigate();


    async function handleSubmit(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);
        
        const formJson = Object.fromEntries(formData.entries());

        console.log('formJson:', formJson);

        let userInfo;
        try {
            userInfo = await (await fetch('/api/accounts/userinfo/')).json();
            console.log('userInfo:', userInfo);
        } catch(error) {
            console.error(error);
        }

        
        let csrfToken = Cookies.get('csrftoken');
        console.log('csrfToken:', csrfToken);
        
        try {
            const csrftokenresponse = await (await fetch('/api/accounts/csrf/')).json()
                console.log("CSRF Token response:", csrftokenresponse);
                csrfToken = csrftokenresponse['csrftoken'];
                console.log("CSRF Token from API:", csrfToken);
        } catch(error) {
            console.error('CSRF Token error:', error);
        }

        try {
            const response = await fetch('/api/accounts/mfa/totp/verify/', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
                },
                credentials: 'include', // include the sessionid
                body: JSON.stringify(formJson)
            });
            const data = await response.json();
            const status = response.status;
            console.log('response:', data);
            if (status == 200) {
                onLoginChange(true);
                navigate('/dashboard');
            }
        } catch(error) {
            console.error(error);
        }
    }

    return (
    
            <div class="formbox">
            <h2>Multi-factor Authentication</h2>
            <p>As an added layer of security, Multi-factor Authentication is required to access your accout.</p>
            <form method="post" onSubmit={handleSubmit}>
                <label>Enter MFA code:</label>
                <input name="otp" type="text" />
                <button>Submit</button>
            </form>
            </div>
    
    );
}