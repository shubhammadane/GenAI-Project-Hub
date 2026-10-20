const taskService = require("../services/taskService");

exports.getTasks = async (req, res, next) => {
  try {
    const tasks = await taskService.getTasksByUser(req.user.id);
    res.json(tasks);
  } catch (err) {
    next(err);
  }
};

exports.createTask = async (req, res, next) => {
  try {
    const { title } = req.body || {};

    if (!title || typeof title !== "string" || title.trim() === "") {
      const error = new Error("Title is required");
      error.statusCode = 400;
      throw error;
    }

    const result = await taskService.createTask(req.user.id, req.body);
    res.status(201).json(result);
  } catch (err) {
    next(err);
  }
};

exports.toggleCompleted = async (req, res, next) => {
  try {
    const result = await taskService.toggleCompleted(req.user.id, req.params.id, req.body.completed);
    res.json(result);
  } catch (err) {
    next(err);
  }
};

exports.updateTask = async (req, res, next) => {
  try {
    const result = await taskService.updateTask(req.user.id, req.params.id, req.body);
    res.json(result);
  } catch (err) {
    next(err);
  }
};

exports.deleteTask = async (req, res, next) => {
  try {
    const result = await taskService.deleteTask(req.user.id, req.params.id);
    res.json(result);
  } catch (err) {
    next(err);
  }
};
