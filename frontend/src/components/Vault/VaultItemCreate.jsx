
import { useState, useEffect } from 'react';
import Cookies from 'js-cookie';
    
export default function CreateVaultItemForm() {
    const [myVaults, setMyVaults] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    async function createVault() {
        try {
            const response = await fetch('/api/vault/items/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': Cookies.get('csrftoken') // have to include the CSRF token for POST requests in Django
                },
                credentials: 'include', // this will include the session cookie which django wioll use to get the user on the backend
            });
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log(data)
            return data;
        } catch (err) {
            throw new Error(`Failed to create vaults: ${err.message}`);
        }
    }

    useEffect(() => {
        const fetchVaults = async () => {
            try {
                setLoading(true);
                const vaults = await createVault();
                setMyVaults(vaults);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchVaults();
    }, []);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    return (
        <ul>
            {myVaults && myVaults.length > 0 ? (
                myVaults.map(vault => (
                    <li key={vault.id}>
                        <h3>{vault.title}</h3>
                        <p>{vault.description}</p>
                    </li>
                ))
            ) : (
                <li>No vault items found</li>
            )}
        </ul>
        )
    }