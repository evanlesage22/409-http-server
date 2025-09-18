*AI WROTE THIS READ ME* 

# Simple HTTP 1.0 Web Server

This project is a basic web server built with Python sockets.  
It serves `index.html` along with other linked files like `about.html`, `poll.html`, and `style.css`.  
If a file is not found, the server returns a `404 Not Found` response.

---

## How to Run

1. Make sure Python 3 is installed on your machine.  
   You can check by running: python --version

2. Clone this repository or download the project folder.

3. Open a terminal in the project folder and run: python main.py

4. The server will start and listen on port **8080** by default.  
You should see something like: Serving HTTP/1.0 on http://127.0.0.1:8080 (doc root: .../www)

5. Open a web browser and go to: http://localhost:8080/
---

## Testing

- **Home page:** [http://localhost:8080/](http://localhost:8080/)  
- **About page:** [http://localhost:8080/about.html](http://localhost:8080/about.html)  
- **Poll page:** [http://localhost:8080/poll.html](http://localhost:8080/poll.html)  
- **404 test:** [http://localhost:8080/doesnotexist.html](http://localhost:8080/doesnotexist.html)  

You can also use `curl` to check headers: curl -I http://localhost:8080/
---

## Notes

- Only **GET** requests are supported.  
- The server closes the connection after each request (HTTP/1.0 behavior).  
- Directory traversal (like `../`) is blocked for safety.

