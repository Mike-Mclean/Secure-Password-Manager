import { useNavigate } from "react-router-dom";
import Cookies from 'js-cookie';

export default function MFAChallege() {

    const navigate = useNavigate();

    const handleClick = async (e) => {
        e.preventDefault();
        console.log('MFA test');



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
            const response = await fetch('/api/accounts/mfa/challenge/', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
                },
                credentials: 'include', // include the sessionid
                body: JSON.stringify({mfa_type: 'email'})
            });
            const data = await response.json();
            const status = response.status;
            console.log('The Response:', data);
            console.log('Status:', status);
            if (status == 200) {
                navigate('/mfa-input', {state: {endPoint: '/api/accounts/mfa/verify/'}});
            }
        } catch (error) {
            console.error(error);
        }
    }

    return (
        <div class="formbox">
            <h2>Multi-factor Authentication</h2>
            <p>Multi-factor Authentication has been enabled on your account. Click the button below to receive your authentication code.</p>
            <form>
                <button onClick={handleClick}>Email Code</button>
            </form>
        </div>
    );
}