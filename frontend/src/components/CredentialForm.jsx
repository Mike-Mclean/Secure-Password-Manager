import { useNavigate } from "react-router-dom";
import Cookies from 'js-cookie';
import encryptJson from '../utils/encdec.js';

export default function CredentialForm(props) {
    navigate = useNavigate();

    const request_method = props.data ? 'PUT' : 'POST';

    const handleSubmit = async (e) => {
            e.preventDefault();

            const endpoint = props.data ? props.endpoint + props.data.id + '/' : props.endpoint;
    
            console.log('endpoint:', props.endpoint);
    
            const form = e.target;
            const formData = new FormData(form);
            
            const formJson = Object.fromEntries(formData.entries());

            const masterPass = localStorage.getItem('masterPass');
            const encrypted = await encryptJson({username: formJson.username, password: formJson.password}, masterPass);

            const dataJson = {title: formJson.account, encrypted_data: encrypted};

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
                const response = await fetch(endpoint, {
                    method: request_method,
                    headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                    },
                    credentials: 'include', // include the sessionid
                    body: JSON.stringify(dataJson)
                });
                const data = await response.json();
                console.log('The Response:', data);
                navigate('/dashboard');
            } catch (error) {
                console.error('Credential error:', error);
            }
    }

    function handleCancel() {
        navigate('/dashboard');
    }

    return (
        <div>
            <form method="post" onSubmit={handleSubmit}>
                    <label>
                        Company:
                    </label>
                    <input 
                        name="account"
                        type="text"
                        defaultValue={props.data ? props.data.title : ''}
                    />
                    <label>
                        Username:
                    </label>
                    <input 
                        name="username"
                        type="text"
                        defaultValue={props.data ? props.data.encrypted_data.username : ''}
                    />
                    <label>
                        Password:
                    </label>
                    <input 
                        name="password"
                        type="password"
                        defaultValue={props.data ? props.data.encrypted_data.password : ''}
                    />
                    <dev class='button-row'>
                        <button type='submit' class='multi-button'>Submit</button>
                        <button type='cancal' class='multi-button' onClick={handleCancel}>Cancel</button>
                    </dev>
                </form>
        </div> 
    );
}