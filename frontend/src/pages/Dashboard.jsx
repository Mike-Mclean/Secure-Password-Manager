import Cookies from 'js-cookie';
import { useNavigate } from 'react-router-dom';
import VaultItemsList from "../components/Vault/VaultItemsList";

export default function Dashboard() {

    const navigate = useNavigate();

    function handleAdd() {
        navigate('/add-credential');
    }

    return (

        <>
            <div class='dash-head'>
                <h2 class='dash-title'>Dashboard</h2>
                <button class='add-button' onClick={handleAdd}>Add Credentials</button>
            </div>
            <VaultItemsList />

        </>

    );
}