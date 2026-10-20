const db = require("../config/db");

exports.getTasksByUser = (userId) => {
  return new Promise((resolve, reject) => {
    const q = "SELECT * FROM tasks WHERE user_id = ?";
    db.query(q, [userId], (err, result) => {
      if (err) return reject(err);
      resolve(result);
    });
  });
}; 

exports.createTask = (userId, data) => {
  return new Promise((resolve, reject) => {
    const q = `
      INSERT INTO tasks (title, priority, category, due_date, completed, status, description, user_id)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `;

    db.query(
      q,
      [
        data.title,
        data.priority || "Medium",
        data.category || "Work",
        data.due_date || null,
        data.completed || false,
        data.status || "To Do",
        data.description || null,
        userId,
      ],
      (err, result) => {
        if (err) return reject(err);

        const eventQ = "INSERT INTO app_events (user_id, event_type) VALUES (?, 'Created Task')";
        db.query(eventQ, [userId], (eventErr) => {
          if (eventErr) {
            console.error("Failed to log task event", eventErr);
          }
          resolve({ message: "Task Added", id: result.insertId });
        });
      }
    );
  });
};

exports.toggleCompleted = (userId, taskId, completed) => {
  return new Promise((resolve, reject) => {
    const q = "UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?";
    db.query(q, [completed, taskId, userId], (err, result) => {
      if (err) return reject(err);
      resolve(result);
    });
  });
};

exports.updateTask = (userId, taskId, data) => {
  return new Promise((resolve, reject) => {
    const selectQ = "SELECT * FROM tasks WHERE id = ? AND user_id = ?";
    db.query(selectQ, [taskId, userId], (selectErr, rows) => {
      if (selectErr) return reject(selectErr);
      if (!rows.length) {
        const err = new Error("Task not found");
        err.statusCode = 404;
        return reject(err);
      }

      const existingTask = rows[0];
      const safeTitle = data.title ?? existingTask.title;
      const safePriority = data.priority ?? existingTask.priority;
      const safeCategory = data.category ?? existingTask.category;
      const safeDueDate = data.due_date === undefined || data.due_date === null || data.due_date === ""
        ? existingTask.due_date
        : data.due_date;
      const safeCompleted = data.completed ?? existingTask.completed;
      const safeStatus = data.status ?? existingTask.status;
      const safeDescription = data.description ?? existingTask.description;

      const q = `
        UPDATE tasks
        SET title = ?, priority = ?, category = ?, due_date = ?, completed = ?, status = ?, description = ?
        WHERE id = ?
      `;

      db.query(
        q,
        [safeTitle, safePriority, safeCategory, safeDueDate, safeCompleted, safeStatus, safeDescription, taskId],
        (err) => {
          if (err) return reject(err);

          const eventQ = "INSERT INTO app_events (user_id, event_type) VALUES (?, 'Updated Task')";
          db.query(eventQ, [userId], (eventErr) => {
            if (eventErr) {
              console.error("Failed to log update event", eventErr);
            }
            resolve({ message: "Task Updated!" });
          });
        }
      );
    });
  });
};

exports.deleteTask = (userId, taskId) => {
  return new Promise((resolve, reject) => {
    const q = "DELETE FROM tasks WHERE id = ? AND user_id = ?";
    db.query(q, [taskId, userId], (err, result) => {
      if (err) return reject(err);

      const eventQ = "INSERT INTO app_events (user_id, event_type) VALUES (?, 'Deleted Task')";
      db.query(eventQ, [userId], (eventErr) => {
        if (eventErr) {
          console.error("Failed to log delete event", eventErr);
        }
        resolve({ message: "Task Deleted" });
      });
    });
  });
};
