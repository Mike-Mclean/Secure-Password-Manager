
import { useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import { FaPen, FaTrash, FaClipboard } from "react-icons/fa";
import { decryptJson } from '../../utils/encdec.js';
import { Link } from 'react-router-dom'
    
export default function VaultItemsList() {
    const [vaultItemList, setVaultItemList] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    async function getVaults() {
        try {
            const response = await fetch('/api/vault/items/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': Cookies.get('csrftoken') // have to include the CSRF token for POST requests in Django, 
                },
                credentials: 'include', // this will include the session cookie
            });
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (err) {
            throw new Error(`Failed to fetch vaults: ${err.message}`);
        }
    }

    async function getVaultItem(id) {
        try {
            const endpoint = '/api/vault/items/' + id + '/'
            const response = await fetch(endpoint, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': Cookies.get('csrftoken') // have to include the CSRF token for POST requests in Django, 
                    // but GET requests can also include it for consistency and security purposes. T
                },
                credentials: 'include', // this will include the session cookie which django wioll use to get the user on the backend
            });
            const data = await response.json();
            const masterPass = localStorage.getItem('masterPass');
            const decrypt = await decryptJson(data.encrypted_data, masterPass);
            data.encrypted_data = decrypt;
            return data;
        } catch (err) {
            throw new Error(`Failed to fetch vaults: ${err.message}`);
        }
    }

    useEffect(() => {
        const fetchVaults = async () => {
            try {
                setLoading(true);
                const vaults = await getVaults();       // Get list of vault contents
                const vaultItems = []
                
                // Get full data for each vault item
                for (let i = 0; i < vaults.results.length; i++) {
                    const vaultItem = await getVaultItem(vaults.results[i].id);
                    vaultItems.push(vaultItem);
                }
                setVaultItemList(vaultItems);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchVaults();
    }, []);

    async function copyToClipboard(password) {
        try {
            await navigator.clipboard.writeText(password);
            console.log("Password copied to clipboard.");
        } catch (err) {
            console.error("Failed to copy password to clipboard:", err);
        }
    }

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    return (
        <table class="cred-table">
            <tr class='cred-head'>
                <th class='head-cell'>Account</th>
                <th class='head-cell'>Username</th>
                <th class='head-cell head-cell-center'>Tools</th>
            </tr>
            {vaultItemList && vaultItemList.length > 0 ? (
                vaultItemList.map(vaultItem => (
                    <tr class="cred-row" key={vaultItem.id}>
                        <td class='cred-cell account-name'>{vaultItem.title}</td>
                        <td class='cred-cell'>{vaultItem.encrypted_data.username}</td>
                        <td >
                            <div class='cred-tools'><FaClipboard class="icon" onClick={() => copyToClipboard(vaultItem.encrypted_data.password)} />
                        <Link to='/edit-credential' state={vaultItem}><FaPen class="icon" /></Link>
                        <Link to='/delete-credential' state={vaultItem}><FaTrash class="icon" /></Link>
                        </div>
                        </td>

                    </tr>
                ))
            ) : (
                <tr class="cred-row">
                    <td></td>
                    <td class='cred-cell'>No vault items found</td>
                    </tr>
            )}
        </table>
        )
    }