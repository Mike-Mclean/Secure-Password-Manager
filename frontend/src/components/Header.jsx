import { NavLink, Link } from 'react-router'

export default function Header({isLoggedIn}) {

    return (
        <div>
            <header>
                <div className="header-container">
                    <h1><Link to="/">Secure Password Manager</Link></h1>
                    <nav>
                        {isLoggedIn == false ? (
                            <>
                            <Link to="/guide">Guide</Link>
                            <Link to="/register">Create Account</Link>
                            <Link to="/login">Login</Link> 
                            </>
                        ) : (
                            <>
                            <Link to="/dashboard">Dashboard</Link>
                            <Link to="/guide">Guide</Link>
                            <Link to="/account">Account</Link>
                            <Link to="/logout">Logout</Link>
                            </>
                        )}
                    </nav>
                </div>
            </header>
        </div>
    );
}