import { useLocation } from "react-router-dom";
import Cookies from 'js-cookie';
import { useNavigate } from "react-router-dom";

export default function ConfirmDelete() {
    const navigate = useNavigate();

    const location = useLocation();
    const data = location.state;
    const id = data.id;
    const title = data.title;
    const username = data.encrypted_data.username

    console.log('id:', id);

    const handleConfirm = async () => {
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
            const response = await fetch('/api/vault/items/'+id+'/soft_delete/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken // have to include the CSRF token for POST requests in Django, 
                },
                credentials: 'include',
                body: JSON.stringify({title: title, soft_deleted: true})
            });
            const data = await response.json();
            console.log('delete response:', data);
            console.log("soft delete status:", response.status);
            navigate('/dashboard');

        } catch(error) {
            console.error(error);
        }
    }


    function handleCancel() {
        navigate('/dashboard');
    }


    return (
        <div class='formbox'>
            <h2>Confirmation</h2>
            <p>Are you sure you want to delete the following credentials:</p>
            {/* <div class="cred-box"> */}
            <blockquote class="cred-box">
                <p class='biggest-text'>{title}</p>
                <p class='big-text'>{username}</p>
                </blockquote>
            {/* </div> */}
            <div class='button-row'>
                <button class='multi-button' onClick={handleConfirm}>Delete</button>
                <button class='multi-button' onClick={handleCancel}>Cancel</button>
            </div>
        </div>
    )
}