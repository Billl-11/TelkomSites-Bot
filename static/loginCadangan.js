const express = require('express');
const app = express();
const path = require('path');
const port = 3006;
const mysql = require('mysql2');

// Create a MySQL connection pool
const connection = mysql.createConnection({
	host     : 'localhost',
	user     : 'root',
	password : '',
	database : 'ciamic_db'
});

// Middleware to parse the request body for login.
app.use(express.urlencoded({ extended: true }));

// Middleware to check if the user is authenticated.
function checkAuthentication(req, res, next) {
  if (isAuthenticated) {
    next();
  } else {
    res.redirect('/');
  }
}

// Your authentication logic should be here.
// For this example, we'll simulate it with a simple variable.
let isAuthenticated = false;

// Middleware to parse the request body for login.
app.use(express.urlencoded({ extended: true }));

// Middleware to check if the user is authenticated.
function checkAuthentication(req, res, next) {
  if (isAuthenticated) {
    next();
  } else {
    res.redirect('/');
  }
}

// Serve static files (CSS, JS, images, etc.)
app.use(express.static(path.join(__dirname, 'public')));
app.use('/css', express.static(path.join(__dirname, 'css')));
app.use('/assets', express.static(path.join(__dirname, 'assets')));

// Route for the dashboard page (index.html with CSS).
app.get('/', checkAuthentication, (req, res) => {
  // res.sendFile(path.join(__dirname, 'http://127.0.0.1:5000/'));
  res.redirect('http://127.0.0.1:5000/');
});

// Route for the login page.
app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, '../templates/login.html'));
});

// Handle login form submission
// app.post('/login', (req, res) => {
//   const { username, password } = req.body;

//   const validUsername = 'user@gmail.com';
//   const validPassword = '12345678';

//   if (username === validUsername && password === validPassword) {
//     isAuthenticated = true;
//     res.redirect('/');
//   } else {
//     res.redirect('/login');
//   }
// });

// http://localhost:3000/auth
app.post('/login', function(request, response) {
	// Capture the input fields
	let username = request.body.username;
	let password = request.body.password;
	// Ensure the input fields exists and are not empty
	if (username && password) {
		// Execute SQL query that'll select the account from the database based on the specified username and password
		connection.query('SELECT * FROM accounts WHERE username = ? AND password = ?', [username, password], function(error, results, fields) {
			// If there is an issue with the query, output the error
			if (error) throw error;
			// If the account exists
			if (results.length > 0) {
				// Authenticate the user
				request.session.loggedin = true;
				request.session.username = username;
				// Redirect to home page
				response.redirect('/home');
			} else {
				response.send('Incorrect Username and/or Password!');
			}			
			response.end();
		});
	} else {
		response.send('Please enter Username and Password!');
		response.end();
	}
});


// Route to handle the logout request.
app.get('/logout', (req, res) => {
  // Clear the authentication status.
  isAuthenticated = false;

  // Redirect back to the login page.
  res.redirect('/login');
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}/login`);
  // console.log(`Server running on http://127.0.0.1:${port}`);
});
