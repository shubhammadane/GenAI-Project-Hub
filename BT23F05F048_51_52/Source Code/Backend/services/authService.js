const db = require("../config/db");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
require("dotenv").config();

exports.register = (data, hashedPassword, role) => {
    return new Promise((resolve, reject) => {
        const q = "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)";
        db.query(q, [data.username, data.email, hashedPassword, role], (err) => {
            if (err) {
                return reject(err);
            }
            resolve({
                message: "User Registered"
            });
        });
    });
};

exports.login = (data) => {
    return new Promise((resolve, reject) => {
        const q = `SELECT id, username, email, password, role FROM users WHERE email=?`;

        db.query(q, [data.email], async (err, result) => {
            if (err) {
                return reject(err);
            }

            if (result.length === 0) {
                return reject({ status: 404, message: "user not found!" });
            }

            const user = result[0];
            const match = await bcrypt.compare(data.password, user.password);

            if (!match) {
                return reject({ status: 401, message: "Wrong password" });
            }

            const eventQuery = `INSERT INTO app_events (user_id, event_type) VALUES (?, 'User Login')`;
            db.query(eventQuery, [user.id], (eventInsertErr) => {
                if (eventInsertErr) {
                    console.error("failed to insert login event", eventInsertErr);
                }

                const updateLoginQuery = "UPDATE users SET last_login = NOW() WHERE id=?";
                db.query(updateLoginQuery, [user.id], (updateErr) => {
                    if (updateErr) {
                        console.error("failed to update last login", updateErr);
                    }

                    const token = jwt.sign(
                        {
                            id: user.id,
                            email: user.email,
                            role: user.role || "user"
                        },
                        process.env.JWT_SECRET,
                        { expiresIn: "1d" }
                    );

                    resolve({
                        message: "Login Success",
                        token,
                        user: {
                            id: user.id,
                            username: user.username,
                            email: user.email,
                            role: user.role || "user"
                        }
                    });
                });
            });
        });
    });
};

