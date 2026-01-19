import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginApi } from "./api/auth.api";
import { useAuth } from "./auth/AuthContext";

function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();
    const { login } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const data = await loginApi({
                email: email,
                password: password,
            });

            // data = { session_id, user }
            login(data);

            const role = data.user.role;
            const status = data.user.status;

            // Only block login if account is suspended or closed
            if (status === "SUSPENDED" || status === "CLOSED") {
                setError("Your account has been disabled");
                return;
            }

            if (role === "DRIVER") {
                navigate("/app/driver");
            } else if (role === "TENANT_ADMIN") {
                navigate("/app/tenant");
            } else {
                // Riders and other roles
                navigate("/app/ride");
            }

        } catch (err) {
            setError(
                err.response?.data?.detail || "Login failed. Try again."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: "400px", margin: "80px auto" }}>
            <h2>Login</h2>

            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: "10px" }}>
                    <label>Email</label>
                    <br />
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        style={{ width: "100%" }}
                    />
                </div>

                <div style={{ marginBottom: "10px" }}>
                    <label>Password</label>
                    <br />
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        style={{ width: "100%" }}
                    />
                </div>

                {error && (
                    <div style={{ color: "red", marginBottom: "10px" }}>
                        {error}
                    </div>
                )}

                <button type="submit" disabled={loading}>
                    {loading ? "Logging in..." : "Login"}
                </button>
            </form>
        </div>
    );
}

export default Login;
