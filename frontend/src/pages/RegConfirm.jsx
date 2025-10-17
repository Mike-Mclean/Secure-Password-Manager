import { NavLink, Link } from 'react-router';
import { useLocation } from 'react-router-dom';

export default function RegConfirm() {
    const location = useLocation();
    const email = location.state.submitData;
    console.log("data:", location.state);
    return (
        <>
            <h2>Registration Confirmation</h2>
            <p>An account for {email} has been created.</p>
            <p>Proceed to your <Link to='/dashboard'>dashboard</Link> to add credentials to your password vault.</p>
        </>
    );
}