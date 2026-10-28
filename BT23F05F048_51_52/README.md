# 📋 Task Planner

A full-stack task management and productivity application that helps users organize tasks, schedule events, generate AI-powered daily plans, and track productivity through analytics.

The application is built using **React**, **Node.js**, **Express.js**, **MySQL**, and **Google Gemini AI**, providing users with a modern interface for planning and managing their daily activities.

---

# ✨ Features

## 🔐 Authentication

* User Registration
* User Login
* JWT Authentication
* Protected API Routes
* Secure Password Handling

## ✅ Task Management

* Create Tasks
* View Tasks
* Update Tasks
* Delete Tasks
* Task Status Tracking
* Priority Management

## 📅 Event Management

* Create Events
* Update Events
* Delete Events
* View Upcoming Events

## 🤖 AI Planner

* Generate AI-powered daily plans
* Accept AI-generated plans
* Smart scheduling suggestions

## 📊 Dashboard & Analytics

* Task Summary
* Event Summary
* Productivity Analytics
* Completion Statistics

## 👨‍💼 Admin Panel

* User Metrics
* Event Reports
* Dashboard Statistics

---

# 🛠 Tech Stack

## Frontend

* React
* Vite
* React Router
* Axios
* CSS (or Tailwind CSS if used)

## Backend

* Node.js
* Express.js
* JWT Authentication
* REST API

## Database

* MySQL

## AI Integration

* Google Gemini API

## Tools

* Git
* GitHub
* npm

---

# 📂 Project Structure

```text
TASK-PLANNER/
│
├── backend/
│   ├── config/                # Database & application configuration
│   ├── controllers/           # Business logic for API routes
│   ├── middleware/            # Authentication & middleware
│   ├── routes/                # API route definitions
│   ├── services/              # AI services & helper functions
│   ├── node_modules/
│   ├── .env                   # Environment variables (ignored by Git)
│   ├── package.json
│   ├── package-lock.json
│   └── server.js              # Express application entry point
│
├── frontend/
│   ├── dist/                  # Production build
│   ├── node_modules/
│   ├── public/                # Static assets
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── .env                   # Frontend environment variables
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── README.md
│   └── vite.config.js
│
├── schema.sql                 # MySQL database schema
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

# 🏗 System Architecture

```text
                 React + Vite Frontend
                         │
                         │
                    REST API Calls
                         │
                         ▼
              Express.js Backend Server
                  │              │
                  │              │
              MySQL Database   Gemini AI API
```

---

# ⚙ Prerequisites

Before running the project, make sure you have installed:

* Node.js (v18 or later recommended)
* npm
* MySQL 8+
* Git

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Adityaraut67/task-planner.git

cd task-planner
```

---

# ⚙ Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Install dependencies:

```bash
npm install
```

Create a `.env` file inside the `backend` folder.

```env
PORT=5000

JWT_SECRET=your_jwt_secret

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=taskplanner

GEMINI_API_KEY=your_gemini_api_key
```

Start the backend server:

```bash
npm run dev
```

---

# 💻 Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create a `.env` file.

```env
VITE_API_BASE_URL=http://localhost:5000
```

Start the frontend:

```bash
npm run dev
```

---

# 🗄 Database Setup

Create a MySQL database.

```sql
CREATE DATABASE taskplanner;
```

Import the schema:

```bash
mysql -u root -p taskplanner < schema.sql
```

Alternatively, use MySQL Workbench and execute the `schema.sql` file.

---

# 🌐 API Modules

The backend exposes APIs for:

* Authentication
* Tasks
* Events
* Dashboard
* Analytics
* AI Planner
* Admin

---

# 🔑 Environment Variables

## Backend

| Variable       | Description           |
| -------------- | --------------------- |
| PORT           | Backend Server Port   |
| JWT_SECRET     | Secret Key for JWT    |
| DB_HOST        | MySQL Host            |
| DB_USER        | MySQL Username        |
| DB_PASSWORD    | MySQL Password        |
| DB_NAME        | Database Name         |
| GEMINI_API_KEY | Google Gemini API Key |

## Frontend

| Variable          | Description      |
| ----------------- | ---------------- |
| VITE_API_BASE_URL | Backend Base URL |

---


# 🔒 Security Notes

* Never commit `.env` files.
* Store API keys securely.
* Rotate JWT secrets if compromised.
* Validate user input on both client and server.

---

# 📄 .gitignore

Ensure the following files are ignored:

```gitignore
node_modules/

backend/.env
frontend/.env

dist/

coverage/

*.log
```

---

# 🚀 Deployment

### Backend

You can deploy using:

* Railway
* Render
* DigitalOcean
* AWS
* Azure

### Frontend

You can deploy using:

* Vercel
* Netlify
* Firebase Hosting

Update the frontend environment variable:

```env
VITE_API_BASE_URL=https://your-backend-url.com
```

---

# 📈 Future Enhancements

* Drag-and-drop task management
* Calendar integration
* Email notifications
* Team collaboration
* Recurring tasks
* Dark mode
* Push notifications
* File attachments
* Mobile application

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature-name
```

3. Commit your changes.

```bash
git commit -m "Add new feature"
```

4. Push the branch.

```bash
git push origin feature-name
```

5. Open a Pull Request.

---

# 📜 License

This project is licensed under the **MIT License**.

---

# 👨‍💻 Author

**Aditya Raut**

GitHub: https://github.com/Adityaraut67

---

# ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub. It helps others discover the project and supports its continued development.
