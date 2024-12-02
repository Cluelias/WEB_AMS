<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Page</title>
    <style>
        /* Styles remain the same as the previous code */
        body {
            margin: 0;
            padding: 0;
            font-family: 'Arial', sans-serif;
            background: linear-gradient(to bottom, #f8f9fa, #d4e0f0);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            display: flex;
            width: 80%;
            max-width: 900px;
            background: #ffffff;
            box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.1);
            border-radius: 20px;
            overflow: hidden;
        }

        .left-section {
            flex: 1;
            background: linear-gradient(to bottom right, #e7f3ff, #f0fff6);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .left-section img {
            max-width: 80%;
            height: auto;
        }

        .right-section {
            flex: 1;
            padding: 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .right-section h2 {
            text-align: center;
            font-size: 28px;
            margin-bottom: 20px;
            color: #333;
        }

        .user-type-buttons {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
        }

        .user-type-buttons input {
            display: none;
        }

        .user-type-buttons label {
            padding: 10px 25px;
            border-radius: 20px;
            border: 2px solid #6A5ACD;
            font-size: 16px;
            color: #6A5ACD;
            background-color: transparent;
            cursor: pointer;
            transition: 0.3s;
        }

        .user-type-buttons input:checked + label {
            background-color: #6A5ACD;
            color: #fff;
        }

        form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .form-group {
            position: relative;
        }

        .form-group input {
            width: 80%;
            padding: 12px 40px;
            font-size: 14px;
            border: 2px solid #ddd;
            border-radius: 10px;
            outline: none;
            transition: 0.3s;
        }

        .form-group input:focus {
            border-color: #6A5ACD;
        }

        .form-group svg {
            position: absolute;
            top: 50%;
            left: 10px;
            transform: translateY(-50%);
            color: #6A5ACD;
            font-size: 18px;
        }

        .form-options {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .form-options input[type="checkbox"] {
            width: auto;
        }

        .form-options label {
            font-size: 14px;
            color: #555;
        }

        .login-button {
            width: 100%;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
            background-color: #6A5ACD;
            color: #fff;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: 0.3s;
        }

        .login-button:hover {
            background-color: #5846c9;
        }

        .under-construction {
            display: none;
            text-align: center;
            color: #f44336;
            font-size: 18px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Left Section with Image -->
        <div class="left-section">
          
        </div>

        <!-- Right Section with Form -->
        <div class="right-section">
            <h2>Log In</h2>
            <div class="user-type-buttons">
                <input type="radio" id="employee" name="user-type" value="employee" checked>
                <label for="employee">Employee</label>
                <input type="radio" id="admin" name="user-type" value="admin">
                <label for="admin">Admin</label>
            </div>

            <!-- Construction Message -->
            <div id="construction-message" class="under-construction">
                Employee login is under construction.
            </div>

            <form action="/login" method="POST" id="login-form">
                <div class="form-group">
                    <select id="user_type" name="user_type" required style="display:none;">
                        <option value="Admin">Admin</option>
                        <option value="Employee">Employee</option>
                    </select>
                </div>

                <div class="form-group">
                    <!-- ID Input -->
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-user" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="#6A5ACD" fill="none" stroke-linecap="round" stroke-linejoin="round">
                        <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                        <circle cx="12" cy="7" r="4" />
                        <path d="M5.5 20a5.5 5.5 0 0 1 13 0" />
                    </svg>
                    <input type="text" id="id-field" name="id" placeholder="Employee Email or ID" required>
                </div>
                
                <div class="form-group">
                    <!-- Password Input -->
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-lock" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="#6A5ACD" fill="none" stroke-linecap="round" stroke-linejoin="round">
                        <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                        <rect x="5" y="11" width="14" height="10" rx="2" />
                        <circle cx="12" cy="16" r="1" />
                        <path d="M8 11v-4a4 4 0 1 1 8 0v4" />
                    </svg>
                    <input type="password" name="password" placeholder="Password" required>
                </div>

                <div class="form-options">
                    <input type="checkbox" id="keep-logged-in">
                    <label for="keep-logged-in">Keep me logged in</label>
                </div>
                
                <button type="submit" class="login-button">Log In</button>
            </form>
        </div>
    </div>

    <script>
        const employeeRadio = document.getElementById('employee');
        const adminRadio = document.getElementById('admin');
        const idField = document.getElementById('id-field');
        const userTypeSelect = document.getElementById('user_type');
        const loginForm = document.getElementById('login-form');
        const constructionMessage = document.getElementById('construction-message');

        // Update the form action and user type selection based on radio button choice
        employeeRadio.addEventListener('change', () => {
            idField.placeholder = "Employee Email or ID";
            userTypeSelect.value = "Employee";  // Dynamically set the value
            constructionMessage.style.display = 'none';  // Hide message by default
        });

        adminRadio.addEventListener('change', () => {
            idField.placeholder = "Admin Email or ID";
            userTypeSelect.value = "Admin";
            constructionMessage.style.display = 'none';  // Hide the under construction message
        });

        // Handle form submission for Employee login
        loginForm.addEventListener('submit', (e) => {
            if (employeeRadio.checked) {
                e.preventDefault();  // Prevent form submission for employees
                constructionMessage.style.display = 'block';  // Show under construction message
            }
        });
    </script>
</body>
</html>
