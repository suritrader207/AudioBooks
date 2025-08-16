document.addEventListener('DOMContentLoaded', function() {
    const loginButton = document.getElementById('login-button');
    const authSection = document.getElementById('auth-section');
    const shelfContainer = document.getElementById('shelf-container');
    const uploadSection = document.getElementById('upload-section');
    const uploadForm = document.getElementById('upload-form');

    function loadBooks() {
        fetch('/api/books')
            .then(response => response.json())
            .then(books => {
                shelfContainer.innerHTML = ''; // Clear existing books
                if (books && books.length > 0) {
                    books.forEach(book => {
                        const bookElement = document.createElement('div');
                        bookElement.className = 'book';

                        const title = document.createElement('h3');
                        title.textContent = book.name;
                        bookElement.appendChild(title);

                        if (book.webContentLink) {
                            const audioPlayer = document.createElement('audio');
                            audioPlayer.controls = true;
                            audioPlayer.src = book.webContentLink;
                            bookElement.appendChild(audioPlayer);
                        }

                        shelfContainer.appendChild(bookElement);
                    });
                } else {
                    shelfContainer.textContent = 'Your shelf is empty. Upload a book to get started!';
                }
            })
            .catch(error => {
                console.error('Error loading books:', error);
                shelfContainer.textContent = 'Could not load books.';
            });
    }

    // Check if the user is authenticated
    fetch('/api/is_authenticated')
        .then(response => response.json())
        .then(data => {
            if (data.is_authenticated) {
                // User is authenticated, show the main content
                authSection.style.display = 'none';
                shelfContainer.style.display = 'block';
                uploadSection.style.display = 'block';
                loadBooks(); // Load the books
            } else {
                // User is not authenticated, show the login button
                authSection.style.display = 'block';
                shelfContainer.style.display = 'none';
                uploadSection.style.display = 'none';
            }
        });

    // Add click listener to the login button
    loginButton.addEventListener('click', function() {
        window.location.href = '/authorize';
    });

    // Handle the upload form submission
    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const title = document.getElementById('book-title').value;
        const file = document.getElementById('book-file').files[0];

        if (!title || !file) {
            alert('Please provide both a title and a file.');
            return;
        }

        const formData = new FormData();
        formData.append('title', title);
        formData.append('file', file);

        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('File uploaded successfully!');
                document.getElementById('book-title').value = '';
                document.getElementById('book-file').value = '';
                loadBooks(); // Refresh the list of books
            } else {
                alert('Error uploading file: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while uploading the file.');
        });
    });
});
