import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';

export default function LoginForm(props) {
    const navigate = useNavigate();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();

        console.log('endpoint:', props.endpoint);
        console.log('props:', props);

        const form = e.target;
        const formData = new FormData(form);
        
        const formJson = Object.fromEntries(formData.entries());

        console.log('formJson:', formJson);
        
        setEmail(formJson.email);
        setPassword(formJson.password);

        const csrfToken = Cookies.get('csrftoken');
        
        try {
            const response = await fetch(props.endpoint, {
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
            console.log('The Response:', data);
            console.log('Status:', status);
            // TODO: handle redirect or whatever after registration
            if (response.status == 200) {
                localStorage.setItem('masterPass', formJson.password);
                localStorage.setItem('email', formJson.email);

                try {
                    const response = await (await fetch('/api/accounts/userinfo/')).json();
                    props.processData(response);
                    console.log('userdata:', response);
                } catch(error) {
                    console.error(error);
                }


            } else if (response.status == 201) {
                try {
                    const response = await fetch('/api/accounts/login/', {
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
                    console.log('The Response:', data);
                    console.log('Status:', status);
                    if (response.status == 200) {
                        localStorage.setItem('masterPass', formJson.password);
                        props.processData(formJson);
                    }
                } catch(error) {
                    console.error(error);
                }
            } else {
                props.onMessageChange("Email or password is invalid.");
                navigate('/login');
            }
        } catch (error) {
            console.error(error);
        };
    }

    return (
        <div>
            <form method="post" onSubmit={handleSubmit}>
                <label>
                    Email:
                </label>
                <input 
                    name="email"
                    type="email"
                />
                <label>
                    Password:
                </label>
                <input 
                    name="password"
                    type="password"
                />
                <button>Submit</button>
            </form>
        </div>
    );
}