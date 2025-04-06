/**
 * Authentication utilities for AgriTransport platform
 */

const auth = {
  /**
   * Check if user is logged in by looking for a valid token
   * @returns {boolean} True if user is logged in
   */
  isLoggedIn() {
    const token = localStorage.getItem("token");
    if (!token) return false;

    // Basic check if token is expired
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      const expiryTime = payload.exp * 1000; // Convert to milliseconds

      if (Date.now() >= expiryTime) {
        this.logout(); // Token expired, clear it
        return false;
      }

      return true;
    } catch (e) {
      console.error("Error checking token:", e);
      this.logout(); // Invalid token, clear it
      return false;
    }
  },

  /**
   * Get current user's username from token
   * @returns {string|null} Username or null if not logged in
   */
  getCurrentUser() {
    if (!this.isLoggedIn()) return null;

    try {
      const token = localStorage.getItem("token");
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.sub; // Username is stored in the 'sub' claim
    } catch (e) {
      console.error("Error getting current user:", e);
      return null;
    }
  },

  /**
   * Log out the current user by removing the token
   */
  logout() {
    localStorage.removeItem("token");
    // Refresh UI state after logout
    this.updateUIState();
    // Redirect to home page if on a protected page
    const currentPath = window.location.pathname;
    if (
      currentPath.startsWith("/my-transports") ||
      currentPath.startsWith("/transports/add") ||
      (currentPath.startsWith("/transports/") && currentPath.includes("/edit"))
    ) {
      window.location.href = "/";
    }
  },

  /**
   * Update UI elements based on authentication state
   */
  updateUIState() {
    const isLoggedIn = this.isLoggedIn();
    const username = this.getCurrentUser();

    // Update auth button text
    const authBtnText = document.getElementById("authBtnText");
    const userMenuContainer = document.getElementById("userMenuContainer");
    const authMenuForGuests = document.getElementById("authMenuForGuests");
    const authMenuForUsers = document.getElementById("authMenuForUsers");
    const usernameDisplay = document.getElementById("usernameDisplay");

    if (authBtnText) {
      if (isLoggedIn && username) {
        authBtnText.textContent = username;
      } else {
        authBtnText.textContent = "Guest";
      }
    }

    // Update dropdown menu visibility
    if (userMenuContainer && authMenuForGuests && authMenuForUsers) {
      if (isLoggedIn) {
        authMenuForGuests.classList.add("hidden");
        authMenuForUsers.classList.remove("hidden");
        if (usernameDisplay) {
          usernameDisplay.textContent = username;
        }
      } else {
        authMenuForGuests.classList.remove("hidden");
        authMenuForUsers.classList.add("hidden");
      }
    }
  },
};

/**
 * Fetch wrapper that includes the authentication token
 * @param {string} url - The URL to fetch
 * @param {object} options - Fetch options
 * @returns {Promise<Response>} - Fetch response
 */
async function authFetch(url, options = {}) {
  // Add token to Authorization header if available
  const token = localStorage.getItem("token");

  if (token) {
    options.headers = {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    };
  }

  try {
    return await fetch(url, options);
  } catch (error) {
    console.error("Auth fetch error:", error);
    throw error;
  }
}

// Update UI state when page loads
document.addEventListener("DOMContentLoaded", function () {
  auth.updateUIState();
});
