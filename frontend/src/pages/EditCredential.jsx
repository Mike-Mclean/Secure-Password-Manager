import { useLocation } from "react-router-dom";
import CredentialForm from "../components/CredentialForm";

export default function EditCredential() {
    const endpoint = '/api/vault/items/';

    const location = useLocation();
    const data = location.state;

    const handleSubmit = async (e) => {
        e.preventDefault();
    }


    return (
        <div class="formbox">
            <h2>Edit Credentials</h2>
            <p>Make any desired changes to the values below. Once you are certain all values are correct, click Submit.</p>

            <CredentialForm endpoint={endpoint} data={data} />

        </div> 
    );
}