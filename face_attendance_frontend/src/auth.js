export function login(username) {
  localStorage.setItem("loggedInUser", username);
}

export function isLoggedIn() {
  return !!localStorage.getItem("loggedInUser");
}

export function logout() {
  localStorage.removeItem("loggedInUser");
}
