
function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];

    for (const item of cookies) {
        const cookie = item.trim();

        if (cookie.startsWith(name + "=")) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }

    return null;
}

function logout() {
    document.cookie = "access_token=; Max-Age=0; path=/; SameSite=Lax";
    document.cookie = "access-token=; Max-Age=0; path=/; SameSite=Lax";
    window.location.href = "/auth/login-page";
}


// Add Todo
const todoForm = document.getElementById("todoForm");

if (todoForm) {
    todoForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const token = getCookie("access_token");

        if (!token) {
            window.location.href = "/auth/login-page";
            return;
        }

        const payload = {
            title: formData.get("title"),
            description: formData.get("description"),
            priority: Number(formData.get("priority")),
            complete: false
        };

        try {
            const response = await fetch("/todos/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                window.location.href = "/todos/todo-page";
                return;
            }

            const errorData = await response.json();
            alert(
                "Error: " +
                (errorData.detail || "Unable to create todo.")
            );
        } catch (error) {
            console.error("Error creating todo:", error);
            alert("An error occurred. Please try again.");
        }
    });
}


// Edit Todo
const editTodoForm = document.getElementById("editTodoForm");

if (editTodoForm) {
    editTodoForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const todoId = window.location.pathname.split("/").pop();
        const token = getCookie("access_token");

        if (!token) {
            window.location.href = "/auth/login-page";
            return;
        }

        const payload = {
            title: formData.get("title"),
            description: formData.get("description"),
            priority: Number(formData.get("priority")),
            complete: formData.get("complete") === "on"
        };

        try {
            const response = await fetch(`/todos/${todoId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                window.location.href = "/todos/todo-page";
                return;
            }

            const errorData = await response.json();
            alert(
                "Error: " +
                (errorData.detail || "Unable to update todo.")
            );
        } catch (error) {
            console.error("Error updating todo:", error);
            alert("An error occurred. Please try again.");
        }
    });

    // Delete Todo
    const deleteTodoButton = document.getElementById("deleteTodo");

    if (deleteTodoButton) {
        deleteTodoButton.addEventListener("click", async function () {
            const todoId = window.location.pathname.split("/").pop();
            const token = getCookie("access_token");

            if (!token) {
                window.location.href = "/auth/login-page";
                return;
            }

            if (!confirm("Are you sure you want to delete this todo?")) {
                return;
            }

            try {
                const response = await fetch(`/todos/${todoId}`, {
                    method: "DELETE",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    window.location.href = "/todos/todo-page";
                    return;
                }

                const errorData = await response.json();
                alert(
                    "Error: " +
                    (errorData.detail || "Unable to delete todo.")
                );
            } catch (error) {
                console.error("Error deleting todo:", error);
                alert("An error occurred. Please try again.");
            }
        });
    }
}
