import CredentialForm from "../components/CredentialForm";

export default function AddCredential() {
    const endpoint = '/api/vault/items/';
    return (
        <div class="formbox">
            <h2>Add Credentials</h2>
            <CredentialForm endpoint={endpoint} />
        </div>
    );

}