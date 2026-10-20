const authService = require("../services/authService");
const bcrypt = require("bcrypt");

exports.register = async (req, res, next) => {
    try {
        const hashedPassword = await bcrypt.hash(req.body.password, 10);
        const role = req.body.role || "user";
        const result = await authService.register(req.body, hashedPassword, role);
        return res.status(201).json(result);
    } catch (err) {
        next(err);
    }
};

exports.login = async (req, res, next) => {
    try {
        const result = await authService.login(req.body);
        return res.json(result);
    } catch (err) {
        if (err?.status) {
            return res.status(err.status).json({ message: err.message });
        }
        next(err);
    }
};