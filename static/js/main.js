// Authentication utilities
const auth = {
  // Check if user is logged in
  isLoggedIn: function () {
    return localStorage.getItem("token") !== null;
  },

  // Get the JWT token
  getToken: function () {
    return localStorage.getItem("token");
  },

  // Logout the user
  logout: function () {
    localStorage.removeItem("token");
    window.location.href = "/login";
  },

  // Add Authorization header to fetch options
  addAuthHeader: function (options = {}) {
    const token = this.getToken();
    if (!token) return options;

    if (!options.headers) {
      options.headers = {};
    }

    options.headers["Authorization"] = `Bearer ${token}`;
    return options;
  },
};

// Update UI based on authentication state
function updateAuthUI() {
  const isLoggedIn = auth.isLoggedIn();

  // Update navigation elements
  const userStatus = document.getElementById("userStatus");
  const loggedOutView = document.getElementById("loggedOutView");
  const loggedInView = document.getElementById("loggedInView");

  if (userStatus) {
    userStatus.textContent = isLoggedIn ? "Account" : "Account";
  }

  if (loggedOutView) {
    loggedOutView.style.display = isLoggedIn ? "none" : "block";
  }

  if (loggedInView) {
    loggedInView.style.display = isLoggedIn ? "block" : "none";
  }

  // Mobile menu
  const mobileLogin = document.getElementById("mobileLogin");
  const mobileRegister = document.getElementById("mobileRegister");
  const mobileLoggedIn = document.getElementById("mobileLoggedIn");

  if (mobileLogin) {
    mobileLogin.style.display = isLoggedIn ? "none" : "block";
  }

  if (mobileRegister) {
    mobileRegister.style.display = isLoggedIn ? "none" : "block";
  }

  if (mobileLoggedIn) {
    mobileLoggedIn.style.display = isLoggedIn ? "block" : "none";
  }
}

// Set up logout functionality
function setupLogout() {
  const logoutLink = document.getElementById("logoutLink");
  const mobileLogout = document.getElementById("mobileLogout");

  if (logoutLink) {
    logoutLink.addEventListener("click", function (e) {
      e.preventDefault();
      auth.logout();
    });
  }

  if (mobileLogout) {
    mobileLogout.addEventListener("click", function (e) {
      e.preventDefault();
      auth.logout();
    });
  }
}

// Initialize authentication when page loads
document.addEventListener("DOMContentLoaded", function () {
  updateAuthUI();
  setupLogout();
});

// Handle authenticated fetch requests
async function authFetch(url, options = {}) {
  const authOptions = auth.addAuthHeader(options);
  const response = await fetch(url, authOptions);

  // If unauthorized, redirect to login
  if (response.status === 401) {
    auth.logout();
    return null;
  }

  return response;
}
