// static/js/app.js

document.addEventListener('DOMContentLoaded', function() {
    // Add confirm dialogs to delete buttons
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Material type indicator
    const materialTypes = {
        'Lecture': 'bg-blue-100 text-blue-800',
        'Assignment': 'bg-red-100 text-red-800',
        'PDF': 'bg-green-100 text-green-800',
        'Word Document': 'bg-purple-100 text-purple-800',
        'Notes': 'bg-yellow-100 text-yellow-800',
        'Other': 'bg-gray-100 text-gray-800'
    };

    document.querySelectorAll('.material-type').forEach(element => {
        const type = element.textContent.trim();
        if (materialTypes[type]) {
            element.className = `px-2 py-1 rounded-full text-xs ${materialTypes[type]}`;
        }
    });

    // Course search functionality
    const searchInput = document.getElementById('course-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            document.querySelectorAll('.course-card').forEach(card => {
                const courseName = card.querySelector('.course-name').textContent.toLowerCase();
                const courseCode = card.querySelector('.course-code').textContent.toLowerCase();
                
                if (courseName.includes(query) || courseCode.includes(query)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Sort weeks functionality
    const sortSelect = document.getElementById('week-sort');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const container = document.querySelector('.weeks-container');
            const weeks = Array.from(container.children);
            
            weeks.sort((a, b) => {
                const aWeekNum = parseInt(a.dataset.weekNum);
                const bWeekNum = parseInt(b.dataset.weekNum);
                
                if (this.value === 'asc') {
                    return aWeekNum - bWeekNum;
                } else {
                    return bWeekNum - aWeekNum;
                }
            });
            
            container.innerHTML = '';
            weeks.forEach(week => container.appendChild(week));
        });
    }

    // Drag and drop file upload
    const dropArea = document.getElementById('drop-area');
    if (dropArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            dropArea.classList.add('bg-indigo-100');
        }

        function unhighlight() {
            dropArea.classList.remove('bg-indigo-100');
        }

        dropArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                document.getElementById('file').files = files;
                document.getElementById('filename-display').textContent = files[0].name;
            }
        }
    }
});