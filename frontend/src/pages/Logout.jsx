import Cookies from 'js-cookie';

export default function Logout({onLoginChange}) {

    const logout = async () => {


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
                const response = await fetch('/api/accounts/logout/', {
                    method: 'POST',
                    headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                    },
                    credentials: 'include', // include the sessionid
                });
                const data = await response.json();
                console.log('The Response:', data);
                // TODO: handle redirect or whatever after registration
                onLoginChange(false);            // Trigger navbar change
            } catch (error) {
                console.error('Logout error:', error);
        }
    }

    logout();

    return (
        <>
            <p>You have been logged out.</p>
        </>
    );
}