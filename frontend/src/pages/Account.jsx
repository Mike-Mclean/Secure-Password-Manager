import Cookies from 'js-cookie';
import { useNavigate } from 'react-router-dom';


export default function Account(props) {

    const navigate = useNavigate();

    const userEmail = localStorage.getItem('email');
    // console.log('email:', userEmail);

    const handleEmailClick = async (e) => {
        e.preventDefault();

        let csrfToken = Cookies.get('csrftoken');
        try {
            const csrftokenresponse = await (await fetch('/api/accounts/csrf/')).json()
                console.log("CSRF Token response:", csrftokenresponse);
                csrfToken = csrftokenresponse['csrftoken'];
                console.log("CSRF Token from API:", csrfToken);
        } catch(error) {
            console.error('CSRF Token error:', error);
        }

        try {
            const response = await fetch('/api/accounts/mfa/email/enroll/', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
                },
                credentials: 'include', // include the sessionid
                body: JSON.stringify({email: userEmail})
            });
            const data = await response.json();
            const status = response.status;
            console.log('The Response:', data);
            console.log('Status:', status);
            props.onLoginChange(false);
            navigate('/mfa-challenge', {state: {endPoint: '/api/accounts/mfa/verify/'}});  
        } catch(error) {
            console.error(error);
        }
    }

    function handleTOTPClick() {
        navigate('/totp-enroll');
    }


    return (
        <div>
        <h2>Account Settings</h2>
        <h3>Multi-factor Authentication</h3>
        <p>Enable Multi-factor Authentication for increased security on your account. To enable using an authenticator app, click the button below.</p>
        <button onClick={handleTOTPClick}>Enable Authenticator App MFA</button>
        <hr />
        <p>Alternatively, you can opt to have your multi-factor authentication code sent to your email. Click the button below to enable.</p>
        <button onClick={handleEmailClick}>Enable Email MFA</button> 

        </div>
    );
}