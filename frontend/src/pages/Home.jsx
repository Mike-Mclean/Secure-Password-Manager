import { Link } from "react-router-dom";

export default function Home() {
    return (
        <div>
            <h2>Welcome!</h2>
            <p>Welcome to the Secure Password Manager. This free app provides a secure vault for storing your passwords. You no longer need to remember long, complicated passwords. Simply store them in your vault and retrieve them whenever you need them.</p>
            <p><Link to='/register'>Sign up</Link> for a free account today!</p>
        </div>
    );
}